"""
Market matching logic using fuzzy string matching.
Matches similar events between Polymarket and Kalshi.
"""
import logging
from typing import List, Tuple
from rapidfuzz import fuzz, process

from models import Market
from config import Config

logger = logging.getLogger(__name__)


class MarketMatcher:
    """Matches similar markets across platforms using fuzzy string matching."""
    
    def __init__(self, threshold: int = None):
        """
        Initialize market matcher.
        
        Args:
            threshold: Minimum fuzzy match score (0-100) to consider a match.
                      Default from config.
        """
        self.threshold = threshold or Config.FUZZY_MATCH_THRESHOLD
    
    def find_matches(self, polymarket_markets: List[Market], 
                    kalshi_markets: List[Market]) -> List[Tuple[Market, Market, float]]:
        """
        Find matching markets between Polymarket and Kalshi.
        
        Args:
            polymarket_markets: List of Polymarket markets
            kalshi_markets: List of Kalshi markets
            
        Returns:
            List of tuples: (polymarket_market, kalshi_market, match_score)
        """
        matches = []
        
        # Create a mapping of Kalshi market titles for fast fuzzy matching
        kalshi_titles = [m.event_title for m in kalshi_markets]
        kalshi_map = {m.event_title: m for m in kalshi_markets}
        
        for poly_market in polymarket_markets:
            # Find best match using fuzzy string matching
            # Use token_sort_ratio for better matching with reordered words
            result = process.extractOne(
                poly_market.event_title,
                kalshi_titles,
                scorer=fuzz.token_sort_ratio
            )
            
            if result:
                best_match_title, score, _ = result
                
                if score >= self.threshold:
                    kalshi_market = kalshi_map[best_match_title]
                    matches.append((poly_market, kalshi_market, score))
                    logger.info(
                        f"Match found (score={score:.1f}): "
                        f"'{poly_market.event_title}' <-> '{kalshi_market.event_title}'"
                    )
        
        logger.info(f"Found {len(matches)} market matches above threshold {self.threshold}")
        return matches
    
    def normalize_title(self, title: str) -> str:
        """
        Normalize market title for better matching.
        
        Remove common variations, standardize formatting, etc.
        """
        # Convert to lowercase
        normalized = title.lower()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ["will ", "does ", "is ", "are ", "did "]
        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
        
        # Remove question marks and extra whitespace
        normalized = normalized.replace("?", "").strip()
        normalized = " ".join(normalized.split())
        
        return normalized

