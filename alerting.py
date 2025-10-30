"""
Alerting system for sending notifications about arbitrage opportunities.
Supports email and Telegram notifications.
"""
import logging
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import datetime

from models import ArbitrageOpportunity
from config import Config

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alerts for arbitrage opportunities."""
    
    def __init__(self):
        self.email_enabled = Config.EMAIL_ENABLED
        self.telegram_enabled = Config.TELEGRAM_ENABLED
    
    def send_alert(self, opportunity: ArbitrageOpportunity) -> None:
        """
        Send alert through all enabled channels.
        
        Args:
            opportunity: ArbitrageOpportunity to alert about
        """
        if self.email_enabled:
            self._send_email_alert(opportunity)
        
        if self.telegram_enabled:
            self._send_telegram_alert(opportunity)
    
    def send_batch_alert(self, opportunities: List[ArbitrageOpportunity]) -> None:
        """
        Send a batch alert for multiple opportunities.
        
        Args:
            opportunities: List of ArbitrageOpportunity objects
        """
        if not opportunities:
            return
        
        if self.email_enabled:
            self._send_email_batch_alert(opportunities)
        
        if self.telegram_enabled:
            for opp in opportunities:
                self._send_telegram_alert(opp)
    
    def _send_email_alert(self, opportunity: ArbitrageOpportunity) -> None:
        """Send email alert for a single arbitrage opportunity."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🚨 Arbitrage Alert: ${opportunity.min_profit:.2f} Profit!"
            msg["From"] = Config.EMAIL_FROM
            msg["To"] = Config.EMAIL_TO
            
            # Create plain text version
            text_content = self._format_text_alert(opportunity)
            
            # Create HTML version
            html_content = self._format_html_alert(opportunity)
            
            # Attach both versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(Config.EMAIL_SMTP_HOST, Config.EMAIL_SMTP_PORT) as server:
                server.starttls()
                server.login(Config.EMAIL_FROM, Config.EMAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email alert sent for {opportunity.polymarket_market.event_title}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_email_batch_alert(self, opportunities: List[ArbitrageOpportunity]) -> None:
        """Send email alert for multiple arbitrage opportunities."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🚨 {len(opportunities)} Arbitrage Opportunities Found!"
            msg["From"] = Config.EMAIL_FROM
            msg["To"] = Config.EMAIL_TO
            
            # Create content
            text_content = self._format_text_batch_alert(opportunities)
            html_content = self._format_html_batch_alert(opportunities)
            
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(Config.EMAIL_SMTP_HOST, Config.EMAIL_SMTP_PORT) as server:
                server.starttls()
                server.login(Config.EMAIL_FROM, Config.EMAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Batch email alert sent for {len(opportunities)} opportunities")
            
        except Exception as e:
            logger.error(f"Failed to send batch email alert: {e}")
    
    def _format_text_alert(self, opp: ArbitrageOpportunity) -> str:
        """Format arbitrage opportunity as plain text."""
        return f"""
ARBITRAGE OPPORTUNITY DETECTED!
{'=' * 60}

Event: {opp.polymarket_market.event_title}
Match Score: {opp.match_score:.1f}%
Timestamp: {opp.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

BETTING STRATEGY
{'=' * 60}
Polymarket: Bet ${opp.bet_polymarket_amount:.2f} on {opp.bet_polymarket_side.upper()}
Kalshi: Bet ${opp.bet_kalshi_amount:.2f} on {opp.bet_kalshi_side.upper()}
Total Investment: ${opp.total_investment:.2f}

EXPECTED RETURNS
{'=' * 60}
If YES: ${opp.profit_if_yes:.2f} profit
If NO: ${opp.profit_if_no:.2f} profit
Minimum Guaranteed Profit: ${opp.min_profit:.2f}
ROI: {opp.roi_percent:.2f}%

MARKET DETAILS
{'=' * 60}
Polymarket:
  - YES: {opp.polymarket_market.yes_price:.4f} ({opp.polymarket_market.yes_price * 100:.2f}%)
  - NO: {opp.polymarket_market.no_price:.4f} ({opp.polymarket_market.no_price * 100:.2f}%)
  - URL: {opp.polymarket_market.url}

Kalshi:
  - YES: {opp.kalshi_market.yes_price:.4f} ({opp.kalshi_market.yes_price * 100:.2f}%)
  - NO: {opp.kalshi_market.no_price:.4f} ({opp.kalshi_market.no_price * 100:.2f}%)
  - URL: {opp.kalshi_market.url}

{'=' * 60}
Generated by Arbitrage Detection System
        """
    
    def _format_html_alert(self, opp: ArbitrageOpportunity) -> str:
        """Format arbitrage opportunity as HTML."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
        .section {{ background: #f9f9f9; padding: 15px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
        .bet {{ background: #fff; padding: 10px; margin: 10px 0; border: 1px solid #ddd; }}
        .profit {{ font-size: 24px; font-weight: bold; color: #4CAF50; }}
        .link {{ display: inline-block; margin: 10px 5px; padding: 10px 15px; background: #2196F3; color: white; text-decoration: none; border-radius: 3px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        td, th {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 ARBITRAGE OPPORTUNITY!</h1>
            <p class="profit">${opp.min_profit:.2f} Guaranteed Profit</p>
        </div>
        
        <div class="section">
            <h2>Event</h2>
            <p><strong>{opp.polymarket_market.event_title}</strong></p>
            <p>Match Score: {opp.match_score:.1f}% | {opp.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
        
        <div class="section">
            <h2>Betting Strategy</h2>
            <div class="bet">
                <strong>Polymarket:</strong> Bet <strong>${opp.bet_polymarket_amount:.2f}</strong> on <strong>{opp.bet_polymarket_side.upper()}</strong>
            </div>
            <div class="bet">
                <strong>Kalshi:</strong> Bet <strong>${opp.bet_kalshi_amount:.2f}</strong> on <strong>{opp.bet_kalshi_side.upper()}</strong>
            </div>
            <p><strong>Total Investment:</strong> ${opp.total_investment:.2f}</p>
        </div>
        
        <div class="section">
            <h2>Expected Returns</h2>
            <table>
                <tr>
                    <td>If YES wins:</td>
                    <td><strong>${opp.profit_if_yes:.2f}</strong></td>
                </tr>
                <tr>
                    <td>If NO wins:</td>
                    <td><strong>${opp.profit_if_no:.2f}</strong></td>
                </tr>
                <tr style="background: #e8f5e9;">
                    <td><strong>Minimum Profit:</strong></td>
                    <td><strong style="color: #4CAF50;">${opp.min_profit:.2f}</strong></td>
                </tr>
                <tr>
                    <td>ROI:</td>
                    <td><strong>{opp.roi_percent:.2f}%</strong></td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Market Details</h2>
            <h3>Polymarket</h3>
            <p>YES: {opp.polymarket_market.yes_price * 100:.2f}% | NO: {opp.polymarket_market.no_price * 100:.2f}%</p>
            <a href="{opp.polymarket_market.url}" class="link">View on Polymarket</a>
            
            <h3>Kalshi</h3>
            <p>YES: {opp.kalshi_market.yes_price * 100:.2f}% | NO: {opp.kalshi_market.no_price * 100:.2f}%</p>
            <a href="{opp.kalshi_market.url}" class="link">View on Kalshi</a>
        </div>
    </div>
</body>
</html>
        """
    
    def _format_text_batch_alert(self, opportunities: List[ArbitrageOpportunity]) -> str:
        """Format multiple opportunities as plain text."""
        text = f"\n{len(opportunities)} ARBITRAGE OPPORTUNITIES FOUND!\n{'=' * 60}\n\n"
        
        for i, opp in enumerate(opportunities, 1):
            text += f"\n{i}. {opp.polymarket_market.event_title}\n"
            text += f"   Min Profit: ${opp.min_profit:.2f} (ROI: {opp.roi_percent:.2f}%)\n"
            text += f"   Strategy: ${opp.bet_polymarket_amount:.2f} on {opp.bet_polymarket_side.upper()} (Polymarket), "
            text += f"${opp.bet_kalshi_amount:.2f} on {opp.bet_kalshi_side.upper()} (Kalshi)\n"
        
        return text
    
    def _format_html_batch_alert(self, opportunities: List[ArbitrageOpportunity]) -> str:
        """Format multiple opportunities as HTML."""
        items_html = ""
        for i, opp in enumerate(opportunities, 1):
            items_html += f"""
            <div class="opp-item">
                <h3>{i}. {opp.polymarket_market.event_title}</h3>
                <p><strong>Min Profit: ${opp.min_profit:.2f}</strong> (ROI: {opp.roi_percent:.2f}%)</p>
                <p>Strategy: ${opp.bet_polymarket_amount:.2f} on {opp.bet_polymarket_side.upper()} (Polymarket), 
                   ${opp.bet_kalshi_amount:.2f} on {opp.bet_kalshi_side.upper()} (Kalshi)</p>
                <p>
                    <a href="{opp.polymarket_market.url}" class="link">Polymarket</a>
                    <a href="{opp.kalshi_market.url}" class="link">Kalshi</a>
                </p>
            </div>
            """
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
        .opp-item {{ background: #f9f9f9; padding: 15px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
        .link {{ display: inline-block; margin: 5px; padding: 8px 12px; background: #2196F3; color: white; text-decoration: none; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 {len(opportunities)} Arbitrage Opportunities!</h1>
        </div>
        {items_html}
    </div>
</body>
</html>
        """
    
    def _send_telegram_alert(self, opportunity: ArbitrageOpportunity) -> None:
        """Send Telegram alert (optional feature)."""
        # Implementation for Telegram bot API
        # Requires requests library and bot token
        try:
            import requests
            
            if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
                return
            
            message = f"""
🚨 *ARBITRAGE ALERT* 🚨

*Event:* {opportunity.polymarket_market.event_title}

*Strategy:*
• Polymarket: ${opportunity.bet_polymarket_amount:.2f} on {opportunity.bet_polymarket_side.upper()}
• Kalshi: ${opportunity.bet_kalshi_amount:.2f} on {opportunity.bet_kalshi_side.upper()}

*Returns:*
• Min Profit: ${opportunity.min_profit:.2f}
• ROI: {opportunity.roi_percent:.2f}%

[Polymarket]({opportunity.polymarket_market.url}) | [Kalshi]({opportunity.kalshi_market.url})
            """
            
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": Config.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Telegram alert sent for {opportunity.polymarket_market.event_title}")
            
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

