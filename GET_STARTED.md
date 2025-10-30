# 🚀 Getting Started - Your $100+ Profit Alerts

This system will automatically email you when it finds arbitrage opportunities with **at least $100 guaranteed profit**.

## 📋 What You'll Need (5 minutes setup)

1. ✅ Kalshi account with credentials
2. ✅ Gmail account for receiving alerts
3. ✅ Python 3.9+ installed

## 🔧 Setup Instructions

### Step 1: Install Dependencies

```bash
cd /Users/urimeir/Documents/arbitrage
pip install -r requirements.txt
```

If you get permission errors, use:
```bash
pip install --user -r requirements.txt
```

Or create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Create Your Configuration File

Create a file named `.env` in the `/Users/urimeir/Documents/arbitrage` directory:

```bash
# REQUIRED: Kalshi API credentials
# Sign up at https://kalshi.com if you don't have an account
KALSHI_EMAIL=your_kalshi_email@example.com
KALSHI_PASSWORD=your_kalshi_password

# REQUIRED: Email configuration for alerts
EMAIL_ENABLED=true
EMAIL_FROM=your_gmail@gmail.com
EMAIL_TO=your_gmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

# This ensures you only get alerts for $100+ profit opportunities
MIN_PROFIT_USD=100

# Scan every 5 minutes
SCAN_INTERVAL_MINUTES=5

# Platform fees (already configured correctly)
POLYMARKET_FEE=0.02
KALSHI_FEE=0.07

# Match threshold (already configured correctly)
FUZZY_MATCH_THRESHOLD=85
```

### Step 3: Get Your Gmail App Password

**IMPORTANT:** Don't use your regular Gmail password!

1. **Enable 2-Factor Authentication:**
   - Go to: https://myaccount.google.com/security
   - Turn on "2-Step Verification"

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "Arbitrage Bot"
   - Click "Generate"
   - **Copy the 16-character password** (ignore spaces)

3. **Add to .env file:**
   ```bash
   EMAIL_PASSWORD=abcd efgh ijkl mnop  # Your generated password
   ```

### Step 4: Test Your Setup

Run a single test scan:

```bash
python3 main.py --mode once
```

**What to look for:**
- ✅ "Successfully authenticated with Kalshi"
- ✅ "Found X binary markets" for both platforms
- ✅ No error messages

If you see errors, check the [Troubleshooting](#troubleshooting) section below.

### Step 5: Start Continuous Monitoring

Once the test works, start continuous scanning:

```bash
python3 main.py --mode scheduled
```

The scanner will:
- ✅ Run immediately
- ✅ Continue scanning every 5 minutes
- ✅ **Email you when arbitrage with $100+ profit is found**
- ✅ Keep running until you stop it (Ctrl+C)

### Step 6: Run in Background (Optional)

To keep it running even after you close the terminal:

```bash
nohup python3 main.py --mode scheduled > arbitrage_output.log 2>&1 &
```

View the process:
```bash
ps aux | grep "main.py"
```

Stop it:
```bash
pkill -f "main.py"
```

View logs in real-time:
```bash
tail -f arbitrage.log
```

## 📧 What You'll Receive

When an arbitrage opportunity with $100+ profit is found, you'll get an email like this:

**Subject:** 🚨 Arbitrage Alert: $102.34 Profit!

**Body:**
```
ARBITRAGE OPPORTUNITY DETECTED!

Event: Will Bitcoin reach $100k in 2025?
Match Score: 95.2%

BETTING STRATEGY
Polymarket: Bet $430.12 on YES
Kalshi: Bet $569.88 on NO
Total Investment: $1000.00

EXPECTED RETURNS
If YES: $102.34 profit
If NO: $102.34 profit
Minimum Guaranteed Profit: $102.34
ROI: 10.23%

[Direct links to both markets included]
```

## ⚡ When You Get an Alert

### Action Checklist:

1. **Act Quickly** - Arbitrage opportunities close fast (minutes or seconds)

2. **Verify Markets**
   - Click both links in the email
   - Confirm markets are still open
   - Check current prices match the alert

3. **Check Your Balance**
   - Ensure you have enough funds on both platforms
   - Account for the exact bet amounts in the email

4. **Place Bets Simultaneously**
   - Open both markets in separate tabs
   - Place both bets as quickly as possible
   - Even a small price change can eliminate the arbitrage

5. **Document Everything**
   - Screenshot bet confirmations
   - Save the email alert
   - Track actual profits vs predicted

## 🎯 Understanding the Numbers

### Example Alert Breakdown

```
Total Investment: $1000.00
Bet Polymarket: $430.12 on YES
Bet Kalshi: $569.88 on NO
```

**If YES happens:**
- Polymarket bet wins: $430.12 → Payout after fees
- Kalshi bet loses: -$569.88
- **Net profit: $102.34**

**If NO happens:**
- Polymarket bet loses: -$430.12
- Kalshi bet wins: $569.88 → Payout after fees
- **Net profit: $102.34**

**You win either way!** 🎉

### Why Different Bet Amounts?

The system calculates optimal distribution based on:
- Current prices on each platform
- Platform fees (Polymarket ~2%, Kalshi ~7%)
- Goal to **equalize profit in both outcomes**

## ⚙️ Customization

### Get More Alerts (Lower Profit Threshold)

In your `.env` file:
```bash
MIN_PROFIT_USD=50    # Alert for $50+ profit
```

### Get Fewer, Higher Quality Alerts

```bash
MIN_PROFIT_USD=200         # Only $200+ opportunities
FUZZY_MATCH_THRESHOLD=90   # Stricter matching
```

### Scan More Frequently

```bash
SCAN_INTERVAL_MINUTES=1    # Every minute (aggressive)
```

**Warning:** More frequent scanning means more API calls. Don't set below 1 minute.

### Scan Less Frequently

```bash
SCAN_INTERVAL_MINUTES=10   # Every 10 minutes (conservative)
```

## 📊 Monitoring Your Scanner

### Check if it's running:
```bash
ps aux | grep "main.py"
```

### View recent activity:
```bash
tail -50 arbitrage.log
```

### View all found opportunities:
```bash
cat arbitrage_log.json | python3 -m json.tool
```

### Count opportunities found:
```bash
wc -l arbitrage_log.json
```

## 🔧 Troubleshooting

### "Configuration errors: EMAIL_FROM is required"

**Problem:** `.env` file is missing or incorrect

**Solution:**
```bash
# Make sure .env file exists
ls -la .env

# If not, create it with the template from Step 2
```

### "Failed to authenticate with Kalshi"

**Problem:** Wrong Kalshi credentials

**Solution:**
1. Log in at https://kalshi.com to verify credentials
2. Copy exact email and password to `.env`
3. Make sure there are no extra spaces

### "Failed to send email alert: Username and Password not accepted"

**Problem:** Wrong Gmail password or not using app password

**Solution:**
1. You MUST use an App Password, not your regular Gmail password
2. Follow Step 3 carefully
3. Enable 2FA first
4. Copy the 16-character app password exactly

### "No module named 'rapidfuzz'" or "No module named 'requests'"

**Problem:** Dependencies not installed

**Solution:**
```bash
cd /Users/urimeir/Documents/arbitrage
pip install -r requirements.txt
```

### "No arbitrage opportunities found" (Every scan)

**This is NORMAL!** Arbitrage opportunities are rare.

**What to do:**
1. Be patient - might take hours or days
2. Lower MIN_PROFIT_USD temporarily to test (e.g., 10)
3. Check logs to ensure scanning is working
4. Verify markets are being fetched successfully

### Getting Stuck in "Scheduled" Mode

**To stop:**
- Press `Ctrl+C` in the terminal
- Or: `pkill -f "main.py"`

## 💡 Pro Tips

### 1. Start Small
When you get your first alert, test with 10% of the suggested amounts to verify calculations.

### 2. Account for ALL Costs
- Platform fees (already included)
- Withdrawal fees (not included - varies by platform)
- Deposit fees
- Taxes on winnings

### 3. Check Liquidity
Large bet amounts might not be fillable if market liquidity is low.

### 4. Speed Matters
Have accounts funded in advance. Arbitrage windows close quickly.

### 5. Keep Records
Save all email alerts and track actual results vs predictions.

### 6. Don't Chase Every Opportunity
Verify the match score is high (>90%) and you understand both markets.

## ❓ FAQ

### How often will I get alerts?

True arbitrage is rare. You might get:
- 0-2 alerts per day (typical)
- Several per day during volatile events
- None for several days (also normal)

### What's the typical ROI?

Most arbitrage opportunities when found are:
- 5-15% ROI
- $100-300 profit on $1000 investment
- Occasionally higher during market inefficiencies

### Can I run this on a server?

Yes! Use:
```bash
nohup python3 main.py --mode scheduled > output.log 2>&1 &
```

Or set up as a systemd service (see QUICKSTART.md for details).

### Is this guaranteed profit?

No guarantees in trading. Risks include:
- Prices change before you execute
- Markets resolve differently than expected
- Platform issues or delays
- Withdrawal restrictions

**Always verify manually before betting.**

### Can I use this with other platforms?

The current system only supports Polymarket and Kalshi. Adding other platforms would require:
- New API client modules
- Fee configuration
- Testing

## 📚 Additional Resources

- **Detailed Documentation:** See `README.md`
- **Setup Help:** See `SETUP.md`  
- **Quick Reference:** See `QUICKSTART.md`
- **Sample Outputs:** See `SAMPLE_OUTPUT.md`

## 🎯 Ready to Go!

Your arbitrage scanner is configured to alert you when it finds opportunities with **at least $100 profit**.

**Final Checklist:**
- [ ] Dependencies installed
- [ ] `.env` file created with your credentials
- [ ] Test scan completed successfully
- [ ] Started in scheduled mode
- [ ] Monitoring logs for activity

**Now you wait for the alerts!** 📧💰

When you receive one, act quickly but carefully. Good luck!

---

**Questions or Issues?**
Check the troubleshooting section above or review the detailed documentation in README.md.

