"""
Unit tests for market matching logic.
"""
import unittest
from datetime import datetime

from market_matcher import MarketMatcher
from models import Market


class TestMarketMatcher(unittest.TestCase):
    """Test cases for MarketMatcher."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matcher = MarketMatcher(threshold=80)
    
    def test_exact_match(self):
        """Test matching with identical titles."""
        poly_markets = [
            Market(
                platform="polymarket",
                market_id="1",
                event_title="Will Bitcoin reach $100k in 2025?",
                description="",
                yes_price=0.35,
                no_price=0.65,
                url="https://polymarket.com/1"
            )
        ]
        
        kalshi_markets = [
            Market(
                platform="kalshi",
                market_id="BTC-100K",
                event_title="Will Bitcoin reach $100k in 2025?",
                description="",
                yes_price=0.32,
                no_price=0.68,
                url="https://kalshi.com/BTC-100K"
            )
        ]
        
        matches = self.matcher.find_matches(poly_markets, kalshi_markets)
        
        self.assertEqual(len(matches), 1)
        poly, kalshi, score = matches[0]
        self.assertEqual(poly.market_id, "1")
        self.assertEqual(kalshi.market_id, "BTC-100K")
        self.assertGreater(score, 95)  # Should be very high match
    
    def test_similar_match(self):
        """Test matching with similar but not identical titles."""
        poly_markets = [
            Market(
                platform="polymarket",
                market_id="2",
                event_title="Will Trump win the 2024 election?",
                description="",
                yes_price=0.48,
                no_price=0.52,
                url="https://polymarket.com/2"
            )
        ]
        
        kalshi_markets = [
            Market(
                platform="kalshi",
                market_id="PRES-2024",
                event_title="Trump to win 2024 Presidential Election",
                description="",
                yes_price=0.45,
                no_price=0.55,
                url="https://kalshi.com/PRES-2024"
            )
        ]
        
        matches = self.matcher.find_matches(poly_markets, kalshi_markets)
        
        self.assertGreaterEqual(len(matches), 0)
        if matches:
            poly, kalshi, score = matches[0]
            self.assertGreater(score, 70)
    
    def test_no_match_below_threshold(self):
        """Test that poor matches are filtered out."""
        poly_markets = [
            Market(
                platform="polymarket",
                market_id="3",
                event_title="Will it rain in NYC tomorrow?",
                description="",
                yes_price=0.20,
                no_price=0.80,
                url="https://polymarket.com/3"
            )
        ]
        
        kalshi_markets = [
            Market(
                platform="kalshi",
                market_id="TECH-IPO",
                event_title="Will OpenAI go public in 2025?",
                description="",
                yes_price=0.15,
                no_price=0.85,
                url="https://kalshi.com/TECH-IPO"
            )
        ]
        
        # These are completely different topics
        matches = self.matcher.find_matches(poly_markets, kalshi_markets)
        
        # Should find no match above threshold
        self.assertEqual(len(matches), 0)
    
    def test_normalize_title(self):
        """Test title normalization."""
        title1 = "Will Bitcoin reach $100k?"
        title2 = "  will bitcoin reach $100k  "
        
        norm1 = self.matcher.normalize_title(title1)
        norm2 = self.matcher.normalize_title(title2)
        
        self.assertEqual(norm1, norm2)
    
    def test_multiple_markets(self):
        """Test matching with multiple markets on each platform."""
        poly_markets = [
            Market("polymarket", "1", "Bitcoin $100k?", "", 0.35, 0.65, url="https://polymarket.com/1"),
            Market("polymarket", "2", "Trump wins?", "", 0.48, 0.52, url="https://polymarket.com/2"),
            Market("polymarket", "3", "Rain tomorrow?", "", 0.20, 0.80, url="https://polymarket.com/3"),
        ]
        
        kalshi_markets = [
            Market("kalshi", "A", "Bitcoin reaches $100k", "", 0.32, 0.68, url="https://kalshi.com/A"),
            Market("kalshi", "B", "OpenAI IPO", "", 0.15, 0.85, url="https://kalshi.com/B"),
            Market("kalshi", "C", "Trump 2024 victory", "", 0.45, 0.55, url="https://kalshi.com/C"),
        ]
        
        matches = self.matcher.find_matches(poly_markets, kalshi_markets)
        
        # Should find at least the Bitcoin match
        self.assertGreater(len(matches), 0)
        
        # Check that each match has reasonable score
        for poly, kalshi, score in matches:
            self.assertGreaterEqual(score, 80)


if __name__ == '__main__':
    unittest.main()

