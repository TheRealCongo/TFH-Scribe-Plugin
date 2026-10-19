# Changelog

## 4.0.0 — 2026-10-19

### Changed

- Renamed to **TFH Scribe Plugin** (formerly the AutoScript Discord Voice Transcriber). Bifrost Scribe ships it:
  turn it on in Scribe's Plugins page. The repository is now TheRealCongo/TFH-Scribe-Plugin.
- The notices the bot posts in Discord now say "TFH Scribe" instead of "AutoScript".
- Unchanged, so existing setups keep working: the plugin ID (`cdct.discord-transcriber`), its saved settings and
  bot token, the transcript header, `.asenc` files and the token vault location. It still works in AutoScript.

## 3.0.1 — 2026-09-06

### Fixed

- Use AutoScript's shared Windows DPAPI implementation for bot-token storage.
- Start a replacement bot immediately after saving a corrected token instead of
  waiting indefinitely for a failed gateway client to close.
- Explicitly set the connected bot account's Discord presence to online.
