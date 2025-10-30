# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Requirements

```bash
cd /Users/urimeir/Documents/arbitrage
pip install -r requirements.txt
```

## Step 2: Configure Your Credentials

Copy the template and edit it:

```bash
cp .env.template .env
nano .env  # or use your favorite editor
```

**Required fields:**
- `KALSHI_EMAIL` - Your Kalshi account email
- `KALSHI_PASSWORD` - Your Kalshi password
- `EMAIL_FROM` - Your Gmail address
- `EMAIL_TO` - Where to send alerts
- `EMAIL_PASSWORD` - Gmail app password (see below)

### Get Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Enable 2FA if not already enabled
3. Create app password for "Mail"
4. Copy the 16-character password to `EMAIL_PASSWORD` in `.env`

## Step 3: Test Your Setup

Run a single scan:

```bash
python main.py --mode once
```

**Expected output:**
```
===============================================================================
Starting arbitrage scan...
===============================================================================
Fetching markets from Polymarket...
  Found 150 binary markets
Fetching markets from Kalshi...
  Found 120 binary markets
Matching markets between platforms...
  Found 15 matching market pairs
Analyzing matches for arbitrage opportunities...
No arbitrage opportunities found in this scan
Scan completed at 2025-10-29T20:44:00.123456
```

## Step 4: Run Continuously

Once testing works, run in scheduled mode:

```bash
python main.py --mode scheduled
```

Or use the convenience script:

```bash
./run.sh --mode scheduled
```

This will:
- ✅ Scan immediately
- ✅ Continue scanning every 5 minutes
- ✅ Send email alerts when arbitrage is found
- ✅ Log all opportunities to `arbitrage_log.json`

## Step 5: Monitor

Watch the logs in real-time:

```bash
tail -f arbitrage.log
```

Check for opportunities:

```bash
cat arbitrage_log.json | python -m json.tool
```

## What to Expect

### ✅ Success Indicators

- "Successfully authenticated with Kalshi"
- "Found X binary markets" (both platforms)
- "Found X matching market pairs"
- No error messages

### ❌ Common Issues

**"Configuration errors: EMAIL_FROM is required"**
- Create `.env` file from `.env.template`

**"Failed to authenticate with Kalshi"**
- Check credentials in `.env`
- Verify account at kalshi.com

**"Failed to send email alert"**
- Use app password, not regular Gmail password
- Enable 2FA on Google account first

## Understanding Results

### No Arbitrage Found (Normal!)

Arbitrage opportunities are **rare**. You might run for hours or days without finding any.

To increase detection (with more risk):
```bash
MIN_PROFIT_USD=50              # Lower threshold
FUZZY_MATCH_THRESHOLD=75       # More lenient matching
```

### Arbitrage Found! 🎉

You'll receive an email with:
- Exact betting amounts for each platform
- Expected profit in both outcomes
- Direct links to markets

**Before betting:**
1. ✅ Manually verify markets are still open
2. ✅ Check current prices haven't changed
3. ✅ Verify you have enough account balance
4. ✅ Confirm liquidity exists for your bet size
5. ✅ Calculate fees yourself as double-check

## Next Steps

1. **Test with small amounts** - Verify calculations are correct
2. **Monitor logs** - Watch for patterns in when arbs appear
3. **Adjust settings** - Fine-tune thresholds for your needs
4. **Set up alerts** - Ensure you get notifications quickly

## Advanced Usage

### Run in background (keeps running after logout):

```bash
nohup python main.py --mode scheduled > output.log 2>&1 &
```

### View background process:

```bash
ps aux | grep main.py
```

### Stop background process:

```bash
pkill -f "python main.py"
```

### Use with systemd (Linux):

Create `/etc/systemd/system/arbitrage.service`:

```ini
[Unit]
Description=Arbitrage Scanner
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/Users/urimeir/Documents/arbitrage
ExecStart=/usr/bin/python3 /Users/urimeir/Documents/arbitrage/main.py --mode scheduled
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable arbitrage
sudo systemctl start arbitrage
sudo systemctl status arbitrage
```

## Need Help?

- **Setup issues**: See `SETUP.md`
- **Detailed docs**: See `README.md`
- **API errors**: Check platform status pages
- **No opportunities**: This is normal! Be patient.

---

Happy hunting! 🎯💰

