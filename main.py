"""
Main orchestration script for arbitrage detection.
Continuously scans Polymarket and Kalshi for arbitrage opportunities.
"""
import logging
import time
import json
from datetime import datetime
from typing import List
import schedule

from config import Config
from models import ArbitrageOpportunity
from polymarket_client import PolymarketClient
from predictit_client import PredictItClient
from market_matcher import MarketMatcher
from arbitrage_calculator import ArbitrageCalculator
from alerting import AlertManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ArbitrageScanner:
    """Main arbitrage scanning system."""
    
    def __init__(self):
        self.polymarket_client = PolymarketClient()
        self.predictit_client = PredictItClient()
        self.matcher = MarketMatcher()
        self.calculator = ArbitrageCalculator()
        self.alert_manager = AlertManager()
        
        self.opportunities_log = []
    
    def scan(self) -> List[ArbitrageOpportunity]:
        """
        Perform a single scan for arbitrage opportunities.
        
        Returns:
            List of detected arbitrage opportunities
        """
        logger.info("=" * 80)
        logger.info("Starting arbitrage scan...")
        logger.info("=" * 80)
        
        try:
            # Step 1: Fetch markets from both platforms
            logger.info("Fetching markets from Polymarket...")
            poly_markets = self.polymarket_client.fetch_markets(limit=200)
            logger.info(f"  Found {len(poly_markets)} binary markets")
            
            logger.info("Fetching markets from PredictIt...")
            predictit_markets = self.predictit_client.fetch_markets(limit=200)
            logger.info(f"  Found {len(predictit_markets)} binary markets")
            
            if not poly_markets or not predictit_markets:
                logger.warning("No markets found on one or both platforms")
                return []
            
            # Step 2: Match similar markets
            logger.info("Matching markets between platforms...")
            matches = self.matcher.find_matches(poly_markets, predictit_markets)
            logger.info(f"  Found {len(matches)} matching market pairs")
            
            # Step 3: Check for arbitrage opportunities
            logger.info("Analyzing matches for arbitrage opportunities...")
            opportunities = []
            
            for poly_market, predictit_market, match_score in matches:
                opportunity = self.calculator.check_arbitrage(
                    poly_market, predictit_market, match_score
                )
                
                if opportunity:
                    opportunities.append(opportunity)
                    logger.info(f"  ✓ Arbitrage found: {poly_market.event_title}")
                    logger.info(f"    Min profit: ${opportunity.min_profit:.2f}, ROI: {opportunity.roi_percent:.2f}%")
            
            # Step 4: Send alerts
            if opportunities:
                logger.info(f"\n{'!' * 80}")
                logger.info(f"FOUND {len(opportunities)} ARBITRAGE OPPORTUNITIES!")
                logger.info(f"{'!' * 80}\n")
                
                for opp in opportunities:
                    logger.info(str(opp))
                    logger.info("-" * 80)
                    
                    # Send individual alerts
                    self.alert_manager.send_alert(opp)
                    
                    # Log to file
                    self._log_opportunity(opp)
            else:
                logger.info("No arbitrage opportunities found in this scan")
            
            logger.info(f"Scan completed at {datetime.utcnow().isoformat()}")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error during scan: {e}", exc_info=True)
            return []
    
    def _log_opportunity(self, opportunity: ArbitrageOpportunity) -> None:
        """Log opportunity to JSON file for historical tracking."""
        try:
            # Append to log file
            with open('arbitrage_log.json', 'a') as f:
                json.dump(opportunity.to_json(), f)
                f.write('\n')
        except Exception as e:
            logger.error(f"Failed to log opportunity: {e}")
    
    def run_scheduled(self) -> None:
        """
        Run scanner on a schedule.
        Scans every N minutes as configured.
        """
        interval = Config.SCAN_INTERVAL_MINUTES
        logger.info(f"Starting scheduled arbitrage scanner (every {interval} minutes)")
        logger.info(f"Minimum profit threshold: ${Config.MIN_PROFIT_USD}")
        logger.info(f"Email alerts: {'enabled' if Config.EMAIL_ENABLED else 'disabled'}")
        logger.info(f"Telegram alerts: {'enabled' if Config.TELEGRAM_ENABLED else 'disabled'}")
        
        # Run immediately on start
        self.scan()
        
        # Schedule future scans
        schedule.every(interval).minutes.do(self.scan)
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    
    def run_once(self) -> None:
        """Run a single scan and exit."""
        logger.info("Running one-time arbitrage scan...")
        opportunities = self.scan()
        
        if opportunities:
            logger.info(f"\n\n{'=' * 80}")
            logger.info(f"SUMMARY: Found {len(opportunities)} arbitrage opportunities")
            logger.info(f"{'=' * 80}\n")
            
            for i, opp in enumerate(opportunities, 1):
                logger.info(f"{i}. {opp.polymarket_market.event_title}")
                logger.info(f"   Min Profit: ${opp.min_profit:.2f}")
                logger.info(f"   Strategy: ${opp.bet_polymarket_amount:.2f} on {opp.bet_polymarket_side.upper()} (Polymarket), "
                          f"${opp.bet_kalshi_amount:.2f} on {opp.bet_kalshi_side.upper()} (Kalshi)")
                logger.info("")
        else:
            logger.info("No arbitrage opportunities found.")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Polymarket-Kalshi Arbitrage Scanner")
    parser.add_argument(
        '--mode',
        choices=['once', 'scheduled'],
        default='once',
        help='Run mode: once (single scan) or scheduled (continuous)'
    )
    
    args = parser.parse_args()
    
    try:
        scanner = ArbitrageScanner()
        
        if args.mode == 'once':
            scanner.run_once()
        else:
            scanner.run_scheduled()
            
    except KeyboardInterrupt:
        logger.info("\nScanner stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()

