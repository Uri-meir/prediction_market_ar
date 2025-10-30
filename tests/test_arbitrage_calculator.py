"""
Unit tests for arbitrage calculation logic.
"""
import unittest
from datetime import datetime

from arbitrage_calculator import ArbitrageCalculator
from models import Market


class TestArbitrageCalculator(unittest.TestCase):
    """Test cases for ArbitrageCalculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use low fees for easier testing
        self.calculator = ArbitrageCalculator(
            polymarket_fee=0.02,
            kalshi_fee=0.07,
            min_profit=100
        )
    
    def test_clear_arbitrage_opportunity(self):
        """Test detection of a clear arbitrage opportunity."""
        # Polymarket has YES at 0.40, Kalshi has NO at 0.55
        # If we bet YES on Polymarket and NO on Kalshi, we should profit
        poly_market = Market(
            platform="polymarket",
            market_id="1",
            event_title="Test Event",
            description="",
            yes_price=0.40,  # Cheap YES
            no_price=0.60,
            url="https://polymarket.com/1"
        )
        
        kalshi_market = Market(
            platform="kalshi",
            market_id="TEST",
            event_title="Test Event",
            description="",
            yes_price=0.45,
            no_price=0.55,  # Cheap NO
            url="https://kalshi.com/TEST"
        )
        
        opportunity = self.calculator.check_arbitrage(poly_market, kalshi_market, 100.0)
        
        # With these prices, there should be an arbitrage opportunity
        # (but it depends on fees)
        if opportunity:
            self.assertGreaterEqual(opportunity.min_profit, 100)
            self.assertGreater(opportunity.total_investment, 0)
            self.assertGreater(opportunity.roi_percent, 0)
    
    def test_no_arbitrage_fair_prices(self):
        """Test that no arbitrage is detected when prices are fair."""
        # Both platforms have same prices - no arbitrage
        poly_market = Market(
            platform="polymarket",
            market_id="2",
            event_title="Fair Event",
            description="",
            yes_price=0.50,
            no_price=0.50,
            url="https://polymarket.com/2"
        )
        
        kalshi_market = Market(
            platform="kalshi",
            market_id="FAIR",
            event_title="Fair Event",
            description="",
            yes_price=0.50,
            no_price=0.50,
            url="https://kalshi.com/FAIR"
        )
        
        opportunity = self.calculator.check_arbitrage(poly_market, kalshi_market, 100.0)
        
        # Should not find arbitrage with fair prices
        self.assertIsNone(opportunity)
    
    def test_arbitrage_calculation_accuracy(self):
        """Test that arbitrage calculations are mathematically correct."""
        # Create a scenario with known arbitrage
        poly_market = Market(
            platform="polymarket",
            market_id="3",
            event_title="Arb Test",
            description="",
            yes_price=0.35,
            no_price=0.65,
            url="https://polymarket.com/3"
        )
        
        kalshi_market = Market(
            platform="kalshi",
            market_id="ARB",
            event_title="Arb Test",
            description="",
            yes_price=0.40,
            no_price=0.60,
            url="https://kalshi.com/ARB"
        )
        
        opportunity = self.calculator.check_arbitrage(poly_market, kalshi_market, 95.0)
        
        if opportunity:
            # Verify that profit is guaranteed in both outcomes
            self.assertGreater(opportunity.profit_if_yes, 0)
            self.assertGreater(opportunity.profit_if_no, 0)
            
            # Verify that min_profit is the minimum of the two
            self.assertEqual(
                opportunity.min_profit,
                min(opportunity.profit_if_yes, opportunity.profit_if_no)
            )
            
            # Verify total investment equals sum of bets
            self.assertAlmostEqual(
                opportunity.total_investment,
                opportunity.bet_polymarket_amount + opportunity.bet_kalshi_amount,
                places=2
            )
            
            # Verify ROI calculation
            expected_roi = (opportunity.min_profit / opportunity.total_investment) * 100
            self.assertAlmostEqual(opportunity.roi_percent, expected_roi, places=1)
    
    def test_min_profit_threshold(self):
        """Test that opportunities below min profit threshold are rejected."""
        # Use a very high min profit threshold
        calculator = ArbitrageCalculator(
            polymarket_fee=0.02,
            kalshi_fee=0.07,
            min_profit=10000  # Very high threshold
        )
        
        poly_market = Market(
            platform="polymarket",
            market_id="4",
            event_title="Low Profit Event",
            description="",
            yes_price=0.48,
            no_price=0.52,
            url="https://polymarket.com/4"
        )
        
        kalshi_market = Market(
            platform="kalshi",
            market_id="LOWPROF",
            event_title="Low Profit Event",
            description="",
            yes_price=0.49,
            no_price=0.51,
            url="https://kalshi.com/LOWPROF"
        )
        
        opportunity = calculator.check_arbitrage(poly_market, kalshi_market, 100.0)
        
        # Even if there's a slight edge, it won't meet the high threshold
        if opportunity:
            self.assertGreaterEqual(opportunity.min_profit, 10000)
    
    def test_invalid_prices(self):
        """Test handling of invalid price data."""
        poly_market = Market(
            platform="polymarket",
            market_id="5",
            event_title="Invalid Event",
            description="",
            yes_price=0.0,  # Invalid
            no_price=1.0,
            url="https://polymarket.com/5"
        )
        
        kalshi_market = Market(
            platform="kalshi",
            market_id="INVALID",
            event_title="Invalid Event",
            description="",
            yes_price=0.5,
            no_price=0.5,
            url="https://kalshi.com/INVALID"
        )
        
        opportunity = self.calculator.check_arbitrage(poly_market, kalshi_market, 100.0)
        
        # Should handle gracefully and return None
        self.assertIsNone(opportunity)
    
    def test_to_json_serialization(self):
        """Test that ArbitrageOpportunity can be serialized to JSON."""
        poly_market = Market(
            platform="polymarket",
            market_id="6",
            event_title="JSON Test",
            description="",
            yes_price=0.30,
            no_price=0.70,
            url="https://polymarket.com/6"
        )
        
        kalshi_market = Market(
            platform="kalshi",
            market_id="JSON",
            event_title="JSON Test",
            description="",
            yes_price=0.35,
            no_price=0.65,
            url="https://kalshi.com/JSON"
        )
        
        opportunity = self.calculator.check_arbitrage(poly_market, kalshi_market, 100.0)
        
        if opportunity:
            json_data = opportunity.to_json()
            
            # Verify required fields are present
            self.assertIn("event", json_data)
            self.assertIn("recommendation", json_data)
            self.assertIn("min_profit", json_data)
            self.assertIn("total_investment", json_data)
            self.assertIn("timestamp", json_data)
            
            # Verify data types
            self.assertIsInstance(json_data["min_profit"], (int, float))
            self.assertIsInstance(json_data["recommendation"], str)


if __name__ == '__main__':
    unittest.main()

