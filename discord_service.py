"""Discord voice receive and per-member Whisper chunk pipeline."""
from __future__ import annotations

import asyncio
import audioop
import logging
import queue
import re
import threading
import time
import tempfile
import wave
from datetime import datetime
from pathlib import Path


SAMPLE_RATE = 48_000
CHANNELS = 2
SAMPLE_WIDTH = 2


def _safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")[:64] or "speaker"


class SpeakerChunker:
    """Buffers Discord's decoded PCM separately for each Discord member."""

    def __init__(self, queue_: queue.Queue, chunk_dir: Path, seconds: int):
        self.queue = queue_
        self.chunk_dir = chunk_dir
        self.seconds = seconds
        self.lock = threading.Lock()
        self.buffers: dict[int, tuple[str, float, bytearray]] = {}

    def add(self, member, pcm: bytes) -> None:
        if not member or not pcm:
            return
        member_id = int(member.id)
        name = getattr(member, "display_name", None) or getattr(member, "name", str(member_id))
        with self.lock:
            _old_name, start, buffer = self.buffers.get(
                member_id, (name, time.time(), bytearray())
            )
            # Preserve the display name currently used in Discord.
            self.buffers[member_id] = (name, start, buffer)
            buffer.extend(pcm)
            if time.time() - start >= self.seconds:
                self._flush_locked(member_id)

    def flush_all(self) -> None:
        with self.lock:
            for member_id in list(self.buffers):
                self._flush_locked(member_id)

    def _flush_locked(self, member_id: int) -> None:
        name, start, buffer = self.buffers.get(member_id, ("", 0.0, bytearray()))
        if not buffer:
            self.buffers.pop(member_id, None)
            return
        self.chunk_dir.mkdir(parents=True, exist_ok=True)
        path = self.chunk_dir / f"discord_{member_id}_{int(start * 1000)}.wav"
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(CHANNELS)
            wav.setsampwidth(SAMPLE_WIDTH)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(buffer)
        self.queue.put((path, start, name))
        self.buffers.pop(member_id, None)


class DiscordVoiceTranscriber:
    """Runs a Discord bot and creates a single labeled CDCT transcript per session."""

    def __init__(
        self, token, transcripts_dir: Path, work_dir: Path, model_size: str,
        chunk_seconds: int, announcement: str, start_command: str,
        stop_command: str, nickname: str, log,
    ):
        self.token = token
        self.transcripts_dir = transcripts_dir
        self.work_dir = work_dir
        self.model_size = model_size
        self.chunk_seconds = chunk_seconds
        self.announcement = announcement.strip()
        self.start_command = start_command
        self.stop_command = stop_command
        self.nickname = nickname.strip()
        self.log = log
        self.thread: threading.Thread | None = None
        self.loop = None
        self.bot = None
        self.model = None
        self.worker = None
        self.chunker = None
        self.queue: queue.Queue = queue.Queue()

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, name="CDCT Discord bot", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        if self.bot and self.loop:
            try:
                asyncio.run_coroutine_threadsafe(self.bot.close(), self.loop)
            except Exception:
                pass
        self._end_session()
        self.bot = None
        self.loop = None

    def _load_model(self) -> None:
        from transcriber import load_model

        self.model, device = load_model(self.model_size)
        self.log(f"Discord plugin loaded Whisper '{self.model_size}' on {device}.")

    def _begin_session(self, channel_name: str) -> None:
        """Create the daily channel transcript only when /scribe begins."""
        from transcriber import TranscriptionWorker

        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%d%b%y_%H%M%S").upper()
        transcript = self.transcripts_dir / f"{_safe_name(channel_name)}_{stamp}.md"
        transcript.write_text("## Discord voice transcript\n\n", encoding="utf-8")
        self.queue = queue.Queue()
        self.worker = TranscriptionWorker(self.model, self.queue, transcript, delete_chunks=True)
        self.worker.start()
        self.chunker = SpeakerChunker(self.queue, self.work_dir / "chunks", self.chunk_seconds)
        self.log(f"Discord transcription started: {transcript.name}")

    def _end_session(self) -> None:
        if self.chunker:
            self.chunker.flush_all()
        if self.worker:
            self.worker.stop(drain=True)
        self.worker = None
        self.chunker = None

    def _run(self) -> None:
        try:
            import discord
            from discord import app_commands
            from discord.ext import commands, voice_recv
        except ImportError as exc:
            self.log("Discord plugin dependencies are missing. Run install.py or use a release with lib/. " + str(exc))
            return

        try:
            self._load_model()
        except Exception as exc:
            self.log(f"Discord transcription worker could not start: {exc}")
            return
        # Voice connection needs the gateway VOICE_STATE_UPDATE events for the
        # bot itself. Start from Discord's complete non-privileged default
        # set rather than a hand-picked minimal mask.
        intents = discord.Intents.default()
        intents.voice_states = True
        service = self

        class PluginLogHandler(logging.Handler):
            def emit(self, record):
                if record.levelno >= logging.INFO:
                    service.log(self.format(record))

        voice_logger = logging.getLogger("discord.voice_state")
        if not any(isinstance(handler, PluginLogHandler) for handler in voice_logger.handlers):
            handler = PluginLogHandler()
            handler.setFormatter(logging.Formatter("Discord voice: %(message)s"))
            voice_logger.addHandler(handler)
        voice_logger.setLevel(logging.INFO)

        class PCMBytesSource(discord.AudioSource):
            """A finite 48 kHz stereo PCM source for Discord voice playback."""

            def __init__(self, pcm: bytes):
                self.pcm = pcm
                self.offset = 0

            def is_opus(self):
                return False

            def read(self):
                # Discord consumes 20 ms of 48 kHz, stereo, 16-bit PCM at a time.
                frame_size = 3_840
                if self.offset >= len(self.pcm):
                    return b""
                frame = self.pcm[self.offset : self.offset + frame_size]
                self.offset += frame_size
                return frame.ljust(frame_size, b"\0")

        def make_announcement_source():
            """Render the join notice through Windows SAPI into Discord PCM."""
            import pyttsx3

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                wav_path = Path(temp_file.name)
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 170)
                engine.save_to_file(service.announcement, str(wav_path))
                engine.runAndWait()
                engine.stop()
                with wave.open(str(wav_path), "rb") as wav:
                    channels = wav.getnchannels()
                    width = wav.getsampwidth()
                    rate = wav.getframerate()
                    pcm = wav.readframes(wav.getnframes())
            finally:
                try:
                    wav_path.unlink(missing_ok=True)
                except OSError:
                    pass

            if width != 2:
                pcm = audioop.lin2lin(pcm, width, 2)
            if channels == 1:
                pcm = audioop.tostereo(pcm, 2, 1, 1)
            elif channels > 2:
                pcm = audioop.tomono(pcm, 2, 0.5, 0.5)
                pcm = audioop.tostereo(pcm, 2, 1, 1)
            if rate != SAMPLE_RATE:
                pcm, _state = audioop.ratecv(pcm, 2, 2, rate, SAMPLE_RATE, None)
            return PCMBytesSource(pcm)

        class Sink(voice_recv.AudioSink):
            def wants_opus(self):
                return False

            def write(self, user, data):
                service.chunker.add(user, data.pcm)

            def cleanup(self):
                service.chunker.flush_all()

        class Bot(commands.Bot):
            async def setup_hook(self):
                # Preserve the global definition for a public release, but
                # publish guild copies immediately. Global commands can take
                # up to an hour before Discord refreshes them.
                await self.tree.sync()

            async def sync_guild_commands(self):
                for guild in self.guilds:
                    # Replace the server copy wholesale on each fresh bot
                    # connection. This prevents Discord clients using an old
                    # application-command ID after a command rename.
                    self.tree.clear_commands(guild=guild)
                    self.tree.copy_global_to(guild=guild)
                    commands_ = await self.tree.sync(guild=guild)
                    service.log(
                        f"Published Discord commands to {guild.name}: "
                        + ", ".join(command.name for command in commands_)
                    )

            async def on_interaction(self, interaction):
                service.log(f"Discord interaction received: {interaction.data.get('name', 'unknown')}")
                await super().on_interaction(interaction)

        bot = Bot(command_prefix="!", intents=intents)
        self.bot = bot

        @bot.event
        async def on_ready():
            try:
                await bot.sync_guild_commands()
            except Exception as exc:
                service.log(f"Could not sync Discord server commands: {exc}")
            if service.nickname:
                for guild in bot.guilds:
                    try:
                        member = guild.me or await guild.fetch_member(bot.user.id)
                        await member.edit(nick=service.nickname)
                    except Exception as exc:
                        service.log(f"Could not set bot display name in {guild.name}: {exc}")
            service.log(f"Discord bot connected as {bot.user}.")

        @bot.tree.error
        async def on_app_command_error(interaction, error):
            service.log(f"Discord command error: {type(error).__name__}: {error!r}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Scribe could not process that command.", ephemeral=True)

        @bot.tree.command(name=service.start_command, description="Join your voice channel and begin labeled transcription.")
        async def spawnscribe(interaction: discord.Interaction):
            # Voice negotiation can take longer than Discord's three-second
            # deadline. Acknowledge first so the command never looks inert.
            await interaction.response.defer(thinking=True)
            voice_state = getattr(interaction.user, "voice", None)
            channel = getattr(voice_state, "channel", None)
            if channel is None:
                await interaction.followup.send("Join a voice channel first.", ephemeral=True)
                return
            try:
                if service.worker is None:
                    service._begin_session(channel.name)
                existing = interaction.guild.voice_client if interaction.guild else None
                if existing:
                    await existing.move_to(channel)
                    client = existing
                else:
                    client = await channel.connect(
                        cls=voice_recv.VoiceRecvClient,
                        timeout=20.0,
                        reconnect=False,
                        self_deaf=False,
                    )
                client.listen(Sink())
                if service.announcement:
                    try:
                        client.play(await asyncio.to_thread(make_announcement_source))
                    except Exception as exc:
                        # Recording stays active even if the optional local voice
                        # renderer cannot speak on a particular Windows install.
                        service.log(f"Discord join announcement could not play: {exc}")
                await interaction.followup.send(
                    "CDCT transcription is active. This channel is being transcribed; each participant is labeled separately."
                )
            except Exception as exc:
                service._end_session()
                detail = f"{type(exc).__name__}: {exc!r}"
                service.log(f"Discord voice join failed: {detail}")
                await interaction.followup.send(
                    f"CDCT could not join this voice channel: {detail}", ephemeral=True
                )

        @bot.tree.command(name=service.stop_command, description="Stop Discord voice transcription and leave the channel.")
        async def killscribe(interaction: discord.Interaction):
            # Draining the final Whisper chunk can take longer than Discord's
            # three-second interaction deadline, so acknowledge before it.
            await interaction.response.defer(thinking=True)
            client = interaction.guild.voice_client if interaction.guild else None
            if not client:
                await interaction.followup.send("I am not connected to a voice channel.", ephemeral=True)
                return
            client.stop_listening()
            await client.disconnect()
            await asyncio.to_thread(service._end_session)
            await interaction.followup.send("CDCT transcription stopped. The final audio has been transcribed.")

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(bot.start(self.token))
        except Exception as exc:
            self.log(f"Discord bot stopped: {exc}")
        finally:
            self.loop.close()
