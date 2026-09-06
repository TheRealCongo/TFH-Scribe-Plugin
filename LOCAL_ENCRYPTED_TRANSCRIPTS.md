# Sharing encrypted transcripts

AutoScript and the Discord plugin use the same local encrypted-file workflow.
There is no relay, background connection, peer link, or shared transcript store.

1. Record a transcript. It is saved locally as an `.asenc` file.
2. AutoScript copies that recording's unique sharing token to the host clipboard.
3. Send the `.asenc` file to the intended recipient by a method you trust.
4. Send the unique token separately.
5. The recipient opens the file in AutoScript and enters the token. AutoScript
   decrypts it in memory and stores the successful unlock only in that Windows
   user's local DPAPI-protected token vault.

The Discord bot token is unrelated to transcript encryption and must not be
shared for transcript access. Each transcript token unlocks only its matching
recording.

Do not send a decrypted Markdown copy if you want the transcript to remain
encrypted during storage and transfer. An authorized recipient can still read,
copy, screenshot, or reshare the decrypted text.
