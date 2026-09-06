# AutoScript Discord Voice Transcriber

The AutoScript Discord Voice Transcriber is an optional plugin for Discord server
voice channels. It joins the operator's channel, receives each Discord member's
audio separately, and writes a labeled encrypted transcript to the local
AutoScript transcript folder.

## What it does

- Records Discord server voice channels only; Discord DMs and group DMs are not
  supported.
- Labels transcript lines with the Discord display name of the speaker.
- Saves every session as `VoiceChannelName_DDMMMYY_HHMMSS.asenc`.
- Creates a unique sharing token for every transcript and copies it to the host
  clipboard.
- Keeps the bot token protected with Windows DPAPI. The bot token is not a
  transcript-encryption key.
- Can play the configured join announcement and posts a visible transcription notice
  when an authorized operator starts a session.

Transcription and encrypted transcript storage remain local to the computer
running AutoScript. Share `.asenc` files manually with their matching unique
transcript token when needed.

## Install

1. Download the plugin release and copy its folder into the `plugins` folder next
   to `AutoScript.exe`.
2. Release bundles include `lib/`. For a source checkout, run `install.py` with
   Python 3.11 or later to create that folder.
3. In AutoScript, open **Settings → Plugins**, enable **Discord Voice
   Transcriber**, then choose **Configure**.
4. Paste the bot token into the masked token field and choose **Save and start
   bot**.
5. Join a Discord server voice channel and run `/spawnscribe` to start. Run
   `/killscribe` to stop and leave the channel.

The Configure dialog also allows the transcription model and start/stop command
names to be changed. Server owners and administrators manage the bot's display
name directly in Discord.

## Create a Discord bot

Each host should create and use a separate Discord bot. Never share or commit a
bot token.

1. Open the [Discord Developer Portal](https://discord.com/developers/applications)
   and create an application with a bot.
2. Under **Installation**, enable Guild Install and select the `bot` and
   `applications.commands` scopes.
3. Grant View Channels, Send Messages, Connect, and Speak permissions.
4. Add the bot to a server you administer.
5. Paste its token only into the local AutoScript plugin configuration.

## Share an encrypted Discord transcript

1. The host stops the session and sends the resulting `.asenc` file manually.
2. The host sends that recording's copied sharing token separately.
3. The recipient opens the file in AutoScript and enters the token once.
4. AutoScript decrypts the transcript in memory and saves the successful unlock
   only in that recipient's local Windows vault.

## Responsible use

Tell people before transcription begins, follow applicable laws and platform
rules, and protect transcript files and sharing tokens as sensitive material.

## Compatibility

The plugin uses a reviewed DAVE-compatible revision of
[`discord-ext-voice-recv`](https://github.com/imayhaveborkedit/discord-ext-voice-recv).
Test Discord updates before relying on the plugin for an important session.
