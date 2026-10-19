# TFH Scribe Plugin

The TFH Scribe Plugin transcribes Discord server voice channels. It joins the
operator's channel, receives each Discord member's audio separately, and writes
a labeled encrypted transcript to the local transcript folder.

Bifrost Scribe ships with it, so TFH members don't install anything. It was
called the AutoScript Discord Voice Transcriber before version 4.0.0, and it
still works in AutoScript.

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
running the plugin. Share `.asenc` files manually with their matching unique
transcript token when needed.

## Turn it on in Bifrost Scribe

1. In Bifrost Scribe, open the **Plugins** page, select **TFH Scribe Plugin**,
   turn it on, then choose **Configure**.
2. Paste the bot token into the masked token field and choose **Save and start
   bot**.
3. Join a Discord server voice channel and run `/spawnscribe` to start. Run
   `/killscribe` to stop and leave the channel.

Sessions show in Scribe's Library under **From plugins**. Each Scribe update
brings the plugin's current version; its settings and bot token are kept.

## Use it in AutoScript

1. Copy this plugin's folder, with its `lib/` folder, into the `plugins` folder
   next to `AutoScript.exe`. For a source checkout, run `install.py` first, with
   the same Python version as the app's engine, to create `lib/`.
2. In AutoScript, open **Settings → Plugins**, enable **TFH Scribe Plugin**, then
   choose **Configure** and continue as above.

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
5. Paste its token only into the local plugin configuration.

## Share an encrypted Discord transcript

1. The host stops the session and sends the resulting `.asenc` file manually.
2. The host sends that recording's copied sharing token separately.
3. The recipient opens the file in Bifrost Scribe or AutoScript and enters the
   token once.
4. The app decrypts the transcript in memory and saves the successful unlock
   only in that recipient's local Windows vault.

## Responsible use

Tell people before transcription begins, follow applicable laws and platform
rules, and protect transcript files and sharing tokens as sensitive material.
Read the [Privacy Policy](PRIVACY_POLICY.md) and
[Terms of Service](TERMS_OF_SERVICE.md) before using the plugin.

## Compatibility

The plugin uses a reviewed DAVE-compatible revision of
[`discord-ext-voice-recv`](https://github.com/imayhaveborkedit/discord-ext-voice-recv).
Test Discord updates before relying on the plugin for an important session.

Its plugin ID (`cdct.discord-transcriber`), transcript format and token vault
location are unchanged from the AutoScript Discord Voice Transcriber, so
existing setups and shared files keep working.
