# Cloudflare Worker
## Deploy
```bash
cd ingestion/worker
npm install
npx wrangler login
npx wrangler deploy
```
## Secrets
Set:
- TELEGRAM_BOT_TOKEN
- GITHUB_TOKEN
## Security
The worker validates Telegram initData and writes raw transaction JSON files to the GitHub repository. No secrets are exposed to the browser.
