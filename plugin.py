"""Entry point of the TFH Scribe Plugin (Discord voice transcription) for Bifrost Scribe and AutoScript."""
from __future__ import annotations

import json
import re
import threading
from datetime import datetime
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox
from transcript_security import protect_secret, unprotect_secret


DEFAULT_ANNOUNCEMENT = "Break Break Break, this call is being transcribed by the 25th Armored Division Scribe."
DEFAULT_START_COMMAND = "spawnscribe"
DEFAULT_STOP_COMMAND = "killscribe"
COMMAND_RE = re.compile(r"^[a-z0-9_-]{1,32}$")
SAVED_TOKEN_MARKER = "autoscript-saved-token"


class Plugin:
    """Starts a separate bot process thread only after local configuration."""

    def __init__(self):
        self.context = None
        self.service = None

    @property
    def config_path(self) -> Path:
        return self.context.data_dir / "config.json"

    def _load_config(self) -> dict:
        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _save_config(self, config: dict) -> None:
        self.context.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    def _log(self, message: str) -> None:
        """Keep diagnostics available even when the host app runs as a windowed EXE."""
        try:
            self.context.data_dir.mkdir(parents=True, exist_ok=True)
            log_path = self.context.data_dir / "discord-plugin.log"
            with log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}\n")
        except OSError:
            pass
        self.context.log(message)

    def activate(self, context) -> None:
        self.context = context
        config = self._load_config()
        if config.get("token_dpapi"):
            # Older configurations started the bot on launch. New configurations
            # can store a token solely to open encrypted transcripts.
            if config.get("bot_enabled", True):
                self._start(config)
            else:
                self._log("TFH Scribe Plugin is configured for encrypted transcript access. The bot is not running.")
        else:
            self._log("TFH Scribe Plugin enabled. Choose Configure to save a bot token.")

    def deactivate(self) -> None:
        if self.service:
            self.service.stop()
            self.service = None

    def _start(self, config: dict) -> None:
        previous = self.service
        self.service = None
        if previous:
            self._log("Restarting Discord bot with updated settings…")
            # A dead or partially connected gateway can take an unbounded time
            # to close. Let it finish in the background so a saved replacement
            # token can establish the new bot session immediately.
            threading.Thread(target=previous.stop, daemon=True).start()
        self._start_service(config)

    def _start_service(self, config: dict) -> None:
        try:
            token = unprotect_secret(config["token_dpapi"])
            from discord_service import DiscordVoiceTranscriber

            self.service = DiscordVoiceTranscriber(
                token=token,
                transcripts_dir=self.context.transcripts_dir,
                work_dir=self.context.data_dir,
                model_size=config.get("model", "small"),
                chunk_seconds=int(config.get("chunk_seconds", 30)),
                announcement=str(config.get("announcement", DEFAULT_ANNOUNCEMENT)),
                start_command=str(config.get("start_command", DEFAULT_START_COMMAND)),
                stop_command=str(config.get("stop_command", DEFAULT_STOP_COMMAND)),
                log=self._log,
                copy_token=self.context.copy_token,
            )
            self.service.start()
        except Exception as exc:
            self.service = None
            self._log(f"TFH Scribe Plugin could not start: {exc}")

    def open_settings(self, parent) -> None:
        config = self._load_config()
        dialog = ctk.CTkToplevel(parent)
        dialog.title("TFH Scribe Plugin")
        dialog.geometry("500x630")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="TFH Scribe Plugin", font=("Cascadia Mono", 16, "bold")).pack(
            anchor="w", padx=24, pady=(24, 8)
        )
        ctk.CTkLabel(
            dialog,
            text="Paste a newly generated bot token here. It is encrypted with Windows DPAPI for this Windows account and is never shown again by this dialog.",
            justify="left", wraplength=430,
        ).pack(anchor="w", padx=24, pady=(0, 14))
        token = ctk.CTkEntry(dialog, placeholder_text="Bot token", show="•")
        if config.get("token_dpapi"):
            # Display a password-style mask without exposing or rewriting the
            # real token. Saving this unchanged keeps the DPAPI-protected value.
            token.insert(0, SAVED_TOKEN_MARKER)
        token.pack(fill="x", padx=24, pady=(0, 12))
        ctk.CTkLabel(
            dialog,
            text="A masked value means a token is already saved. Leave it unchanged to keep it, or select it and paste a replacement token.",
            justify="left", wraplength=430,
        ).pack(anchor="w", padx=24, pady=(0, 12))
        model = ctk.CTkOptionMenu(dialog, values=["tiny", "base", "small", "medium"])
        model.set(config.get("model", "small"))
        ctk.CTkLabel(dialog, text="Whisper model").pack(anchor="w", padx=24)
        model.pack(fill="x", padx=24, pady=(2, 18))

        ctk.CTkLabel(dialog, text="Voice announcement on join (leave blank to disable)").pack(
            anchor="w", padx=24
        )
        announcement = ctk.CTkTextbox(dialog, height=82, wrap="word")
        announcement.insert("1.0", config.get("announcement", DEFAULT_ANNOUNCEMENT))
        announcement.pack(fill="x", padx=24, pady=(2, 18))

        ctk.CTkLabel(dialog, text="Start command (without /; lowercase)").pack(anchor="w", padx=24)
        start_command = ctk.CTkEntry(dialog)
        start_command.insert(0, config.get("start_command", DEFAULT_START_COMMAND))
        start_command.pack(fill="x", padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Stop command (without /; lowercase)").pack(anchor="w", padx=24)
        stop_command = ctk.CTkEntry(dialog)
        stop_command.insert(0, config.get("stop_command", DEFAULT_STOP_COMMAND))
        stop_command.pack(fill="x", padx=24, pady=(2, 10))

        def save(start_bot: bool):
            value = token.get().strip()
            if value == SAVED_TOKEN_MARKER:
                value = ""
            if not value and not config.get("token_dpapi"):
                messagebox.showerror("Bot token required", "Paste the bot token before saving.", parent=dialog)
                return
            if value:
                config["token_dpapi"] = protect_secret(value)
            start = start_command.get().strip().lower()
            stop = stop_command.get().strip().lower()
            if not COMMAND_RE.fullmatch(start) or not COMMAND_RE.fullmatch(stop):
                messagebox.showerror(
                    "Invalid command",
                    "Commands must be 1–32 lowercase letters, numbers, hyphens, or underscores.",
                    parent=dialog,
                )
                return
            if start == stop:
                messagebox.showerror("Commands must differ", "Choose different start and stop commands.", parent=dialog)
                return
            config["model"] = model.get()
            config["chunk_seconds"] = 30
            config["announcement"] = announcement.get("1.0", "end-1c").strip()
            config["start_command"] = start
            config["stop_command"] = stop
            # Saving a token for decryption alone must not create another bot
            # session on an approved admin's computer. Preserve an already
            # running service when changing ordinary settings.
            config["bot_enabled"] = bool(start_bot or self.service)
            self._save_config(config)
            if start_bot:
                self._start(config)
            dialog.destroy()

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.pack(anchor="e", padx=24, pady=(0, 18))
        ctk.CTkButton(buttons, text="Save settings", command=lambda: save(False)).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkButton(buttons, text="Save and start bot", command=lambda: save(True)).pack(
            side="left"
        )
