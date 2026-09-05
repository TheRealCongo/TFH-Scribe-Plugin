# AutoScript Discord Voice Transcriber

> **Note:** AutoScript was previously named CDCT. This is a branding update; the project remains local-first, open source, and functionally continuous.

Optional AutoScript plugin that joins a Discord **server** voice channel and writes a
local AutoScript transcript with actual Discord display-name labels. It receives each
member's decoded Discord audio separately, so overlapping speakers do not need
post-hoc speaker diarization.

## Status

This is an initial test-server implementation. It uses
[`discord-ext-voice-recv`](https://github.com/imayhaveborkedit/discord-ext-voice-recv),
whose maintainers label the receive extension incomplete; test Discord updates
before relying on it for important meetings.

## Install

The plugin currently pins a reviewed DAVE-compatible revision of
`discord-ext-voice-recv`. Discord encrypts current voice traffic with DAVE;
the public PyPI receive package can join a channel but cannot decode it yet.

Discord transcripts use `VoiceChannelName_DDMMMYY_HHMMSS.md`, for example
`General_05SEP26_142530.md`. Every session receives its own transcript file.

1. Download a plugin release and copy its folder into the `plugins` folder next
   to `AutoScript.exe`.
2. A release bundle will include `lib/`. For source installs, run `install.py`
   with Python 3.11+ to create that folder.
3. In AutoScript, open **Settings → Plugins**, enable **Discord Voice Transcriber**,
   then choose **Configure**.
4. Paste a freshly generated bot token directly into that dialog. AutoScript encrypts
   it with Windows DPAPI for the signed-in Windows account; it is not stored in
   the repository or shown after saving.
5. In Discord, join a server voice channel and run `/spawnscribe`. The bot
   posts a visible transcription notice. Run `/killscribe` when finished.

The Configure dialog can change the start/stop commands and the bot's
per-server display name. Discord command names must be lowercase. Changing
the display name requires the bot's role to have Manage Nicknames permission;
the global application name remains managed in the Discord Developer Portal.

The bot needs only View Channels, Send Messages, Connect, and Speak. It works
in server voice channels, not Discord DMs or group DMs.

## Create your own Discord bot

Each person hosting this plugin should create and use their own Discord bot.
A bot token belongs to its application, not to a particular Discord server, and
must never be shared or committed to Git.

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   and create an application.
2. Open **Bot**, add a bot, then use **Reset Token** if needed. Copy the token
   only to the local AutoScript plugin Configure dialog; do not paste it into source
   files, a release, Discord chat, or an issue.
3. Under **Installation**, enable Guild Install and select both the `bot` and
   `applications.commands` scopes.
4. Grant the bot View Channels, Send Messages, Connect, and Speak. Add Manage
   Nicknames only when you want the plugin's custom per-server display name
   option to work.
5. Open the generated install link and add the bot to a server you administer.
6. In AutoScript, enable the plugin under **Settings → Plugins**, choose
   **Configure**, paste the token, and select **Save and start bot**.

Adding somebody else's bot to a server does not give that server its own token
or its own transcription host. It remains controlled by the person running the
AutoScript instance that holds that bot's token.

## Consent

Tell everyone in the call before transcription begins. The bot deliberately
posts a channel notice when `/scribe` starts.
