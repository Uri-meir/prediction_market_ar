"""
Example usage of the arbitrage detection system.
Demonstrates how to use the components programmatically.
"""
import logging
from datetime import datetime

from polymarket_client import PolymarketClient
from kalshi_client import KalshiClient
from market_matcher import MarketMatcher
from arbitrage_calculator import ArbitrageCalculator
from alerting import AlertManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Example: Run a single scan and print results."""
    
    print("=" * 80)
    print("ARBITRAGE SCANNER - EXAMPLE USAGE")
    print("=" * 80)
    
    # Initialize clients
    print("\n1. Initializing API clients...")
    poly_client = PolymarketClient()
    kalshi_client = KalshiClient()
    
    # Fetch markets
    print("\n2. Fetching markets from Polymarket...")
    poly_markets = poly_client.fetch_markets(limit=50)
    print(f"   Found {len(poly_markets)} Polymarket markets")
    
    print("\n3. Fetching markets from Kalshi...")
    kalshi_markets = kalshi_client.fetch_markets(limit=50)
    print(f"   Found {len(kalshi_markets)} Kalshi markets")
    
    # Match markets
    print("\n4. Matching markets between platforms...")
    matcher = MarketMatcher(threshold=85)
    matches = matcher.find_matches(poly_markets, kalshi_markets)
    print(f"   Found {len(matches)} matching pairs")
    
    # Check for arbitrage
    print("\n5. Analyzing for arbitrage opportunities...")
    calculator = ArbitrageCalculator(min_profit=100)
    opportunities = []
    
    for poly_market, kalshi_market, match_score in matches:
        opp = calculator.check_arbitrage(poly_market, kalshi_market, match_score)
        if opp:
            opportunities.append(opp)
    
    # Display results
    print("\n" + "=" * 80)
    if opportunities:
        print(f"✅ FOUND {len(opportunities)} ARBITRAGE OPPORTUNITIES!")
        print("=" * 80)
        
        for i, opp in enumerate(opportunities, 1):
            print(f"\n--- Opportunity #{i} ---")
            print(f"Event: {opp.polymarket_market.event_title}")
            print(f"Match Score: {opp.match_score:.1f}%")
            print(f"\nBetting Strategy:")
            print(f"  • Polymarket: ${opp.bet_polymarket_amount:.2f} on {opp.bet_polymarket_side.upper()}")
            print(f"  • Kalshi: ${opp.bet_kalshi_amount:.2f} on {opp.bet_kalshi_side.upper()}")
            print(f"  • Total Investment: ${opp.total_investment:.2f}")
            print(f"\nExpected Profit:")
            print(f"  • If YES: ${opp.profit_if_yes:.2f}")
            print(f"  • If NO: ${opp.profit_if_no:.2f}")
            print(f"  • Minimum Guaranteed: ${opp.min_profit:.2f}")
            print(f"  • ROI: {opp.roi_percent:.2f}%")
            print(f"\nLinks:")
            print(f"  • Polymarket: {opp.polymarket_market.url}")
            print(f"  • Kalshi: {opp.kalshi_market.url}")
            
    else:
        print("❌ NO ARBITRAGE OPPORTUNITIES FOUND")
        print("=" * 80)
        print("\nThis is normal! Arbitrage opportunities are rare.")
        print("Try adjusting these settings in your .env file:")
        print("  • Lower MIN_PROFIT_USD (e.g., 50)")
        print("  • Lower FUZZY_MATCH_THRESHOLD (e.g., 75)")
        print("  • Run more frequently with scheduled mode")
    
    print("\n" + "=" * 80)
    print("Scan completed at:", datetime.utcnow().isoformat())
    print("=" * 80)


if __name__ == "__main__":
    main()

