# Expense Tracker Architecture

## System Overview

```
Telegram Group
    ↓
Telegram Mini App (GitHub Pages)
    ↓
Cloudflare Worker (Free Tier)
    ↓
GitHub API (REST)
    ↓
Raw Transaction Files (Git)
    ↓
GitHub Actions (Daily Processor)
    ↓
Processed Analytics JSON (Git)
    ↓
Mini App Dashboard (Re-renders from processed data)
```

## Core Components

### 1. Telegram Mini App (Frontend)
- **Location**: `miniapp/` directory
- **Hosting**: GitHub Pages (static files only)
- **Responsibilities**:
  - User interface for adding/viewing expenses
  - Telegram WebApp API integration
  - Secure init data collection
  - Calling ingestion worker endpoint
  - Fetching and displaying processed analytics

### 2. Cloudflare Worker (Ingestion)
- **Purpose**: Secure serverless ingestion layer
- **Cost**: ₹0 under normal family usage (free tier)
- **Responsibilities**:
  - Validate Telegram Mini App initData using HMAC-SHA256
  - Extract authenticated user and group identity
  - Receive raw expense transaction
  - Append transaction JSON to GitHub repository
  - Return confirmation to frontend

**Why Cloudflare Worker?**
- No deployment infrastructure cost
- Global edge locations (latency)
- Free tier: 100,000 requests/day
- CORS-friendly
- Easy to test

### 3. Transaction Storage (Immutable Ledger)
- **Structure**: `data/raw/<YYYY>/<MM>/<DD>/<transaction-id>.json`
- **Model**: Append-only, immutable
- **Benefit**: No concurrent write conflicts, git-friendly
- **Source of Truth**: Raw transactions are never modified

### 4. GitHub Actions (Daily Processor)
- **Trigger**: Daily schedule (default: 2 AM UTC)
- **Responsibilities**:
  - Checkout latest transactions
  - Validate transaction schema
  - Calculate analytics
  - Generate processed JSON
  - Commit to `data/processed/`

### 5. Processed Analytics
- **Location**: `data/processed/<YYYY>/<MM>/`
- **Files**:
  - `summary.json` - Monthly totals (personal, family, by category)
  - `daily.json` - Daily breakdown
  - `trends.json` - Monthly trends
  - `users.json` - Per-user spending within family
  - `categories.json` - Category breakdown

**Why Separate Processed Data?**
- Analytics calculated once per day, not per request
- Reduces GitHub API calls
- Reliable caching for Mini App
- Clean separation: raw ≠ computed

## Security Model

### Trust Boundary
```
❌ UNTRUSTED (Frontend):
   - telegram_user_id
   - family_id / chat_id
   - usernames
   - amounts
   
✅ TRUSTED (Server-side validated):
   - Telegram initData HMAC signature
   - Extracted user ID from valid initData
   - Extracted chat ID from valid initData
   - Timestamp validation
```

### Telegram Mini App Authentication
1. Mini App collects `initData` from Telegram WebApp
2. Frontend sends initData to Cloudflare Worker
3. Worker:
   - Extracts `user` and `chat` from initData
   - Validates HMAC-SHA256 signature using Telegram Bot Token
   - Derives `telegram_user_id` and `family_id` from validated data
   - Stores transaction with authenticated identities

**Never trust `initDataUnsafe`** — it's unverified frontend data.

### Secret Management
- **Telegram Bot Token**: Stored in Cloudflare Worker secrets
- **GitHub Token**: Stored in GitHub Actions secrets
- **No secrets in**: Browser, HTML, CSS, GitHub Pages

## Cost Target: ₹0/Month

### Free Resources
- GitHub repository (public or private)
- GitHub Pages (unlimited static hosting)
- GitHub Actions (2,000 minutes/month free tier)
- Cloudflare Worker (100,000 requests/day free)
- Git (unlimited commits, branches)

### Expected Usage (Family of 5)
- ~50 transactions/month = ~1.7/day
- Cloudflare Worker: 50 writes/month + 50 reads/month = 100 req/month
- GitHub Actions: ~3-5 minutes/day = ~90-150 minutes/month
- GitHub Pages: Static files cached by CDN

**All within free tier.**

### If Free Tier Exceeded
Document in deployment guide what each service's paid tier costs and when you'd exceed limits.

## Data Privacy

- All data stored in private GitHub repository
- No cloud databases
- No analytics tracking
- No advertising
- No third-party data sharing
- Telegram group membership defines access control (not implemented in app)

## Scalability Considerations

### Current Design Supports
- Single family/group per bot token configuration
- Multiple families in same repository (by chat_id)
- ~1000 transactions/month with same performance

### Bottlenecks (if exceeded)
- GitHub API rate limits (5,000 req/hr for authenticated)
- GitHub Actions concurrent jobs (20 free tier)
- File system scaling: 1000s of files per day would need archival strategy

### Future Enhancements (if needed)
- Archive old transactions to separate branch
- Batch analytics for multiple families
- Caching layer for processed JSON
- Webhook integration instead of polling
