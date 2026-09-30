# Deployment
## Manual requirements
- GitHub repository
- Telegram bot created in BotFather
- Cloudflare Worker account
- GitHub Pages enabled
## Secrets
- TELEGRAM_BOT_TOKEN in the Cloudflare Worker
- GITHUB_TOKEN in the worker environment and possibly GitHub Actions
## Process
1. Deploy the static Mini App to GitHub Pages
2. Configure the Telegram Mini App URL
3. Deploy the Cloudflare Worker
4. Validate a real transaction
5. Confirm a raw transaction file is written under data/raw
