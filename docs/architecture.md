# Architecture
The application is designed around these layers:
Telegram group/chat
 ↓
Telegram Mini App
 ↓
Secure ingestion worker
 ↓
Immutable raw transaction files in Git
 ↓
GitHub Actions daily analytics
 ↓
Processed JSON analytics
 ↓
Mini App dashboard
## Security-first identity model
The app must never trust browser-supplied identity values. Telegram signed initData is validated server-side. Family identity is derived from trusted Telegram chat context, not from a frontend form field.
## Storage model
Each raw transaction is stored as an append-only JSON file:
data/raw/YYYY/MM/DD/<transaction-id>.json
This ensures the ledger is immutable and safe for daily analytics processing.
## Cost target
The design targets approximately ₹0/month under normal family use using GitHub Pages, GitHub Actions, and Cloudflare free tier.
## Important limitation
If Telegram does not expose trusted chat identity in a given Mini App launch mode, the worker must reject the request and document the limitation rather than inventing a fake family enrollment flow.
