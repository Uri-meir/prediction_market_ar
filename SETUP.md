# Quick Setup Guide

## Prerequisites

1. **Python 3.9+** installed
2. **Kalshi account** (https://kalshi.com)
3. **Gmail account** (or other SMTP email)

## Setup Steps

### 1. Install Dependencies

```bash
cd /Users/urimeir/Documents/arbitrage
pip install -r requirements.txt
```

### 2. Create .env File

Copy this template and fill in your credentials:

```bash
# Copy to .env and customize
cat > .env << 'EOF'
# Polymarket (no auth needed)
POLYMARKET_API_URL=https://gamma-api.polymarket.com

# Kalshi (REQUIRED - create account at kalshi.com)
KALSHI_API_URL=https://trading-api.kalshi.com/trade-api/v2
KALSHI_EMAIL=your_email@example.com
KALSHI_PASSWORD=your_kalshi_password

# Email Alerts (REQUIRED for notifications)
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your_gmail@gmail.com
EMAIL_TO=where_to_send_alerts@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

# Telegram (OPTIONAL)
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Settings
MIN_PROFIT_USD=100
SCAN_INTERVAL_MINUTES=5
POLYMARKET_FEE=0.02
KALSHI_FEE=0.07
FUZZY_MATCH_THRESHOLD=85
EOF
```

### 3. Get Gmail App Password

**Important:** Don't use your regular Gmail password!

1. Go to Google Account settings: https://myaccount.google.com/
2. Enable 2-Factor Authentication if not already enabled
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and "Other (Custom name)"
5. Name it "Arbitrage Bot"
6. Click "Generate"
7. Copy the 16-character password (spaces don't matter)
8. Paste into `.env` as `EMAIL_PASSWORD`

### 4. Get Kalshi Credentials

1. Sign up at https://kalshi.com
2. Complete account verification
3. Use your login email and password in `.env`

### 5. Test Your Setup

Run a single scan:

```bash
python main.py --mode once
```

You should see:
- ✅ "Fetching markets from Polymarket..."
- ✅ "Fetching markets from Kalshi..."
- ✅ "Matching markets between platforms..."
- ✅ Either "FOUND X ARBITRAGE OPPORTUNITIES!" or "No arbitrage opportunities found"

### 6. Run Continuously

Once tested, run in scheduled mode:

```bash
python main.py --mode scheduled
```

To run in background:
```bash
nohup python main.py --mode scheduled > output.log 2>&1 &
```

## Common Issues

### "Configuration errors: EMAIL_FROM is required"
- You forgot to create `.env` file
- Copy the template above and fill in your details

### "Failed to authenticate with Kalshi"
- Check email/password are correct
- Make sure Kalshi account is verified
- Try logging in at kalshi.com to verify credentials

### "Failed to send email alert"
- Make sure you're using an App Password, not your regular Gmail password
- Check that EMAIL_FROM, EMAIL_TO, and EMAIL_PASSWORD are all set
- Try the App Password without spaces

### "No markets found"
- Check internet connection
- Polymarket API might be down (check https://polymarket.com)
- Kalshi API might be down (check https://kalshi.com)

## Customization

### Get More Alerts (Lower Standards)

```bash
MIN_PROFIT_USD=50              # Lower profit threshold
FUZZY_MATCH_THRESHOLD=75       # More lenient matching
```

### Get Fewer, Higher Quality Alerts

```bash
MIN_PROFIT_USD=200             # Higher profit requirement
FUZZY_MATCH_THRESHOLD=90       # Stricter matching
```

### Scan More/Less Frequently

```bash
SCAN_INTERVAL_MINUTES=1        # Every minute (aggressive)
SCAN_INTERVAL_MINUTES=10       # Every 10 minutes (conservative)
```

## Testing Email Alerts

To force a test email, you can temporarily lower the profit threshold:

```bash
MIN_PROFIT_USD=0.01
```

Then run:
```bash
python main.py --mode once
```

This should detect some "arbitrage" (even if not profitable) and send you a test email.

Remember to change `MIN_PROFIT_USD` back to 100 after testing!

## Next Steps

Once running:
1. Monitor `arbitrage.log` for activity
2. Check `arbitrage_log.json` for historical opportunities
3. When you get an alert, manually verify the markets before betting
4. Start with small amounts to test the calculations

## Questions?

Check the main README.md for detailed documentation.

