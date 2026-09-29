# Expense Tracker

A Telegram-native family/personal expense tracker designed to run with a near-zero monthly cost target using GitHub Pages, GitHub Actions, and minimal serverless ingestion.

## Features

- Telegram Mini App UI
- Secure Telegram initData validation on the ingestion server
- Append-only raw transaction ledger in Git
- Daily analytics generation by GitHub Actions
- Personal and family expense tracking
- Category/subcategory configuration via JSON
- Deterministic analytics output

## Architecture

See the docs under `docs/` for architecture, security, Telegram setup, deployment, and serverless worker design.

## Local development

```bash
python -m pip install -r requirements.txt
pytest -q
```

## Production deployment

The project targets the following free-stack setup:

- GitHub Pages for the Mini App frontend
- GitHub Actions for testing and daily analytics
- Cloudflare Worker for secure ingestion
- GitHub repository for raw immutable transactions and generated analytics

## Important security rule

Never trust browser-supplied `telegram_user_id`, `family_id`, or `paid_by` values. The server must validate Telegram signed `initData` before writing a transaction.

## Manual setup still required

- Create a Telegram bot via BotFather
- Add the bot to the family Telegram group
- Configure the Mini App URL
- Deploy the Cloudflare Worker
- Configure secrets in the worker and GitHub Actions
- Enable GitHub Pages deployment

## Repository structure

- `config/` contains categories and app settings
- `data/raw/` stores immutable raw transaction files
- `data/processed/` stores generated analytics JSON
- `processor/` contains validation and analytics logic
- `miniapp/` contains the Telegram Mini App frontend
- `ingestion/worker/` contains the Cloudflare Worker
- `tests/` contains pytest coverage

## Cost target

The target is approximately ₹0/month for normal family-scale usage using GitHub free tiers and Cloudflare free tier where applicable.
