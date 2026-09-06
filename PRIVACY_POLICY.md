# AutoScript Discord Voice Transcriber Privacy Policy

**Effective date: September 5, 2026**

AutoScript Discord Voice Transcriber is a local AutoScript plugin for Discord
server voice channels. This policy explains the information the plugin processes
when an operator runs it.

## Who operates the plugin

The person who installs, configures, and runs the plugin controls its operation
and any transcripts it creates. The AutoScript project does not operate a
central transcript service, relay, or hosted transcript database.

## The Discord bot and local plugin

The Discord bot is a bridge between Discord and a properly configured AutoScript
plugin running on an operator's computer. Adding the bot to a server by itself
does not record, transcribe, store, share, or otherwise process a voice channel.
Those actions occur only when an authorized operator has configured the local
plugin and starts a session.

## Information processed

When an authorized operator starts a Discord voice transcription session, the
plugin processes the following information locally on that operator's computer:

- Discord voice audio received for the voice channel;
- Discord display names and member identifiers used to label transcript lines;
- server, channel, and command information needed to operate the bot; and
- the bot token supplied by the operator.

The plugin also creates a transcript-specific sharing token for each session.
That token is separate from the Discord bot token.

## How information is used

Voice audio is used only to produce a speaker-labeled local transcript. Discord
identifiers and display names are used only to operate the bot and identify the
speaker in that transcript. The plugin does not sell data, run advertising,
perform analytics, or send transcript content to an AutoScript-operated remote
service.

Discord itself processes information according to its own policies when you use
Discord. This plugin is a third-party service and is not operated by Discord.

## Local storage and security

Each completed session is saved locally as an AES-256-GCM encrypted `.asenc`
file. Each file has its own high-entropy sharing token. The plugin stores the
operator's bot token and locally remembered transcript tokens in the current
Windows user's DPAPI-protected storage.

Audio chunks used while transcribing are ordinarily deleted after processing.
An unexpected crash or forced shutdown can leave temporary files behind until
the operator removes them.

No security measure can guarantee absolute protection. Operators should protect
their Windows account, transcript files, sharing tokens, and bot token.

## Sharing and retention

The operator chooses where transcripts are stored, how long they are retained,
and whether to share them. To share a transcript, the operator manually sends
the encrypted `.asenc` file and its matching sharing token to an intended
recipient. Anyone who receives both can read that transcript with AutoScript.

Participants should contact the server administrator or the operator running
the plugin for questions about a particular recording, deletion, or access.

## Consent and responsible use

The plugin posts a visible transcription notice and can play a configured join
announcement. These features do not replace the operator's responsibility to
provide any notice, obtain any consent, and follow any recording, privacy, or
employment laws that apply to the conversation.

## Changes and contact

This policy may change when the plugin changes. The effective date will be
updated with a revision. For project-level questions, open an issue at
https://github.com/TheRealCongo/AutoScript-Discord-Plugin/issues.
