# Polymarket-Kalshi Arbitrage Detection System

An automated Python system that continuously scans Polymarket and Kalshi for binary prediction markets, detects risk-free arbitrage opportunities, and sends real-time alerts via email or Telegram.

## 🎯 Overview

This system:
- 📊 Fetches live binary markets from Polymarket and Kalshi APIs
- 🔗 Matches similar events across platforms using fuzzy string matching
- 💰 Detects true arbitrage opportunities where you profit regardless of outcome
- 📧 Sends email/Telegram alerts with detailed betting strategies
- ⏰ Runs continuously on a configurable schedule

## 🔑 Key Features

- **Automated Market Scanning**: Fetches 200+ markets from each platform every scan
- **Smart Matching**: Uses fuzzy matching to find equivalent events across platforms
- **True Arbitrage Detection**: Calculates optimal bet distribution for guaranteed profit
- **Fee Awareness**: Incorporates platform fees (Polymarket ~2%, Kalshi ~7%) into calculations
- **Customizable Profit Targets**: Set minimum profit thresholds (e.g., $100)
- **Real-Time Alerts**: Email and Telegram notifications with complete betting instructions
- **Historical Logging**: JSON logs of all detected opportunities

## 📋 Requirements

- Python 3.9 or higher
- Polymarket API access (public, no auth required)
- Kalshi API access (requires account and credentials)
- Email account for alerts (Gmail recommended)
- Optional: Telegram bot for mobile alerts

## 🚀 Installation

### 1. Clone and Install Dependencies

```bash
cd /Users/urimeir/Documents/arbitrage
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Polymarket Configuration
POLYMARKET_API_URL=https://gamma-api.polymarket.com

# Kalshi Configuration
KALSHI_API_URL=https://trading-api.kalshi.com/trade-api/v2
KALSHI_EMAIL=your_email@example.com
KALSHI_PASSWORD=your_password

# Email Alert Configuration
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com
EMAIL_PASSWORD=your_app_password

# Telegram Configuration (Optional)
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Arbitrage Settings
MIN_PROFIT_USD=100
SCAN_INTERVAL_MINUTES=5
POLYMARKET_FEE=0.02
KALSHI_FEE=0.07
FUZZY_MATCH_THRESHOLD=85
```

### 3. Email Setup (Gmail)

For Gmail, you need to create an "App Password":
1. Enable 2-factor authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use this password in `EMAIL_PASSWORD` (not your regular password)

### 4. Kalshi API Setup

1. Create a Kalshi account at https://kalshi.com
2. Navigate to API settings and generate credentials
3. Add your email and password to the `.env` file

## 💻 Usage

### Single Scan (Test Mode)

Run a one-time scan to test your setup:

```bash
python main.py --mode once
```

### Continuous Scanning

Run continuously, scanning every N minutes:

```bash
python main.py --mode scheduled
```

This will:
- Scan immediately on startup
- Continue scanning every 5 minutes (configurable)
- Send alerts whenever arbitrage is found
- Log all opportunities to `arbitrage_log.json`

### Run Tests

```bash
pytest tests/
```

## 📊 Example Output

When an arbitrage opportunity is found:

```json
{
  "event": "Will Xi Jinping be out in 2025?",
  "match_score": 95.2,
  "polymarket_yes_prob": 0.04,
  "polymarket_no_prob": 0.96,
  "kalshi_yes_prob": 0.07,
  "kalshi_no_prob": 0.93,
  "recommendation": "Bet $430.12 on YES (Polymarket), $569.88 on NO (Kalshi). Profit: $102.34 if Yes, $100.00 if No.",
  "total_investment": 1000.00,
  "min_profit": 100.00,
  "roi_percent": 10.0,
  "timestamp": "2025-10-29T20:44:00Z",
  "link_poly": "https://polymarket.com/event/xi-jinping-2025",
  "link_kalshi": "https://kalshi.com/markets/XI-2025"
}
```

### Email Alert Example

You'll receive a detailed HTML email with:
- Event description and match quality
- Exact betting amounts for each platform
- Expected profit in both outcomes
- ROI percentage
- Direct links to both markets

## 🏗️ Architecture

```
arbitrage/
├── main.py                    # Main orchestration and scheduling
├── config.py                  # Configuration management
├── models.py                  # Data models (Market, ArbitrageOpportunity)
├── polymarket_client.py       # Polymarket API client
├── kalshi_client.py           # Kalshi API client
├── market_matcher.py          # Fuzzy matching logic
├── arbitrage_calculator.py    # Arbitrage detection algorithm
├── alerting.py                # Email/Telegram alerts
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration (create this)
└── tests/
    ├── test_market_matcher.py
    └── test_arbitrage_calculator.py
```

## 🧮 How It Works

### Arbitrage Detection Algorithm

For a binary market, arbitrage exists when you can bet on opposite outcomes across two platforms such that you profit regardless of which outcome occurs.

**Mathematical Condition:**
```
Combined effective return < 1
where effective_return = (1 - fee) / price
```

**Example:**
- Polymarket: YES at 0.40 (40%)
- Kalshi: NO at 0.55 (55%)
- Fees: Polymarket 2%, Kalshi 7%

Effective returns:
- Polymarket YES: (1 - 0.02) / 0.40 = 2.45
- Kalshi NO: (1 - 0.07) / 0.55 = 1.69

Combined: 1/2.45 + 1/1.69 = 0.408 + 0.592 = 1.00 (no arbitrage at this exact price)

The system calculates optimal bet distribution to equalize profits across both outcomes.

### Market Matching

Uses `rapidfuzz` for fuzzy string matching:
- `token_sort_ratio` algorithm handles word reordering
- Configurable threshold (default 85%)
- Normalizes titles (lowercase, removes punctuation)

### Fee Handling

Platform fees are applied to **profits only**, not the entire payout:
- When you win a bet at price P with bet amount B: `payout = B / P`
- Profit before fees: `payout - B`
- Profit after fees: `(payout - B) × (1 - fee_rate)`

## ⚙️ Configuration

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MIN_PROFIT_USD` | 100 | Minimum profit required to alert |
| `SCAN_INTERVAL_MINUTES` | 5 | Time between scans |
| `POLYMARKET_FEE` | 0.02 | Polymarket fee rate (2%) |
| `KALSHI_FEE` | 0.07 | Kalshi fee rate (7%) |
| `FUZZY_MATCH_THRESHOLD` | 85 | Min similarity score (0-100) |

### Adjusting for Risk Tolerance

**Conservative** (fewer false positives):
```bash
MIN_PROFIT_USD=200
FUZZY_MATCH_THRESHOLD=90
```

**Aggressive** (more opportunities):
```bash
MIN_PROFIT_USD=50
FUZZY_MATCH_THRESHOLD=75
```

## 🔔 Alert Customization

### Email Only
```bash
EMAIL_ENABLED=true
TELEGRAM_ENABLED=false
```

### Telegram Only
```bash
EMAIL_ENABLED=false
TELEGRAM_ENABLED=true
```

### Both
```bash
EMAIL_ENABLED=true
TELEGRAM_ENABLED=true
```

## 📝 Logging

All arbitrage opportunities are logged to:
- `arbitrage.log` - General application logs
- `arbitrage_log.json` - Structured JSON logs of opportunities

## 🧪 Testing

The test suite includes:
- Market matching logic verification
- Arbitrage calculation accuracy tests
- Edge case handling (invalid prices, low liquidity)

Run tests with coverage:
```bash
pytest --cov=. tests/
```

## ⚠️ Important Notes

### Disclaimers

1. **Not Financial Advice**: This is an educational tool. Always do your own research.
2. **API Rate Limits**: Respect platform rate limits to avoid being blocked.
3. **Market Liquidity**: Detected arbitrage may disappear before you can execute trades.
4. **Execution Risk**: Prices can change between detection and execution.
5. **Platform Risk**: Always verify calculations before placing real money bets.

### Limitations

- **Liquidity**: System doesn't verify if markets have enough liquidity for your bet size
- **Speed**: Markets move fast; opportunities may vanish in seconds
- **Execution**: You must manually place bets (no automated trading)
- **Withdrawal**: Consider withdrawal fees and times when calculating true profit

### Best Practices

1. **Start Small**: Test with minimum bet amounts first
2. **Verify Manually**: Always check markets yourself before betting
3. **Monitor Logs**: Review `arbitrage.log` for any errors
4. **Update Fees**: Platform fees can change; keep them updated
5. **Check Liquidity**: Ensure markets can handle your bet size

## 🔧 Troubleshooting

### No Markets Found
- Check API URLs are correct
- Verify Kalshi credentials
- Check internet connection

### No Arbitrage Detected
- Lower `MIN_PROFIT_USD` threshold
- Adjust `FUZZY_MATCH_THRESHOLD`
- Arbitrage opportunities are rare!

### Email Alerts Not Working
- Verify Gmail app password is correct
- Check spam folder
- Ensure 2FA is enabled on Google account

### Kalshi Authentication Failed
- Verify email and password
- Check if account is active
- Try generating new API credentials

## 📚 API References

- [Polymarket API Docs](https://docs.polymarket.com/)
- [Kalshi API Docs](https://trading-api.kalshi.com/)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Real-time WebSocket connections for faster detection
- Automated trade execution (with safety limits)
- Additional platform integrations
- Web dashboard for monitoring
- Machine learning for better market matching

## 📜 License

MIT License - Use at your own risk

## 🙏 Acknowledgments

Built with:
- `requests` for HTTP API calls
- `rapidfuzz` for fuzzy string matching
- `schedule` for task scheduling
- `python-dotenv` for configuration management

---

**Happy arbitrage hunting! 🎯💰**

