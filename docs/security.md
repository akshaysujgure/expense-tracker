# Security
## Never trust browser data
The following elements must never be trusted when supplied by frontend JavaScript:
- telegram_user_id
- family_id
- paid_by
- usernames
- group IDs
## Telegram validation
The worker validates Telegram signed initData using the Telegram bot token before creating a transaction.
## Raw ledger rules
- raw transactions are append-only
- never modify previous entries
- no silent corrections
- if a transaction must be corrected, use a reversal/correction record
