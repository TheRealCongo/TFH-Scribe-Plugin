# Changelog

## 3.0.1 — 2026-09-06

### Fixed

- Use AutoScript's shared Windows DPAPI implementation for bot-token storage.
- Start a replacement bot immediately after saving a corrected token instead of
  waiting indefinitely for a failed gateway client to close.
- Explicitly set the connected bot account's Discord presence to online.
