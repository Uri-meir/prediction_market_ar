"""
Polymarket API client for fetching binary prediction markets.
API Documentation: https://docs.polymarket.com/
"""
import logging
import time
from typing import List, Optional, Dict, Any
import requests
from datetime import datetime

from models import Market
from config import Config

logger = logging.getLogger(__name__)


class PolymarketClient:
    """Client for interacting with Polymarket API."""
    
    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or Config.POLYMARKET_API_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "ArbitrageBot/1.0"
        })
    
    def fetch_markets(self, limit: int = 100, active_only: bool = True) -> List[Market]:
        """
        Fetch binary markets from Polymarket.
        
        Args:
            limit: Maximum number of markets to fetch
            active_only: Only fetch active (open) markets
            
        Returns:
            List of Market objects
        """
        markets = []
        offset = 0
        
        try:
            while len(markets) < limit:
                params = {
                    "limit": min(100, limit - len(markets)),
                    "offset": offset,
                    "active": str(active_only).lower() if active_only else None,
                }
                
                # Remove None values
                params = {k: v for k, v in params.items() if v is not None}
                
                url = f"{self.api_url}/markets"
                logger.debug(f"Fetching Polymarket markets: {url} with params {params}")
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list):
                    batch = data
                elif isinstance(data, dict) and "data" in data:
                    batch = data["data"]
                else:
                    logger.warning(f"Unexpected Polymarket API response format: {type(data)}")
                    break
                
                if not batch:
                    break
                
                for item in batch:
                    market = self._parse_market(item)
                    if market and self._is_binary_market(item):
                        markets.append(market)
                
                offset += len(batch)
                
                # If we got fewer results than requested, we've reached the end
                if len(batch) < params["limit"]:
                    break
                
                # Rate limiting: sleep briefly between requests
                time.sleep(0.1)
            
            logger.info(f"Fetched {len(markets)} binary markets from Polymarket")
            return markets
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Polymarket markets: {e}")
            return []
    
    def _is_binary_market(self, market_data: Dict[str, Any]) -> bool:
        """Check if a market is binary (exactly 2 outcomes)."""
        # Polymarket binary markets typically have 2 outcomes or tokens
        outcomes = market_data.get("outcomes", [])
        tokens = market_data.get("tokens", [])
        
        return len(outcomes) == 2 or len(tokens) == 2
    
    def _parse_market(self, data: Dict[str, Any]) -> Optional[Market]:
        """
        Parse Polymarket API response into Market object.
        
        Polymarket prices are in the range [0, 1] representing probabilities.
        """
        try:
            market_id = data.get("condition_id") or data.get("id") or str(data.get("slug", ""))
            question = data.get("question") or data.get("title", "")
            description = data.get("description", "")
            
            # Extract prices - Polymarket uses 0-1 probability format
            # For binary markets, we need YES and NO prices
            outcomes = data.get("outcomes", [])
            tokens = data.get("tokens", [])
            
            # Try to get prices from outcomePrices or tokens
            outcome_prices = data.get("outcomePrices") or data.get("outcome_prices", [])
            
            yes_price = None
            no_price = None
            
            if len(outcome_prices) >= 2:
                # Assuming first is YES, second is NO
                yes_price = float(outcome_prices[0])
                no_price = float(outcome_prices[1])
            elif len(tokens) >= 2:
                # Try to extract from tokens
                yes_price = float(tokens[0].get("price", 0.5))
                no_price = float(tokens[1].get("price", 0.5))
            
            # Fallback: use equal probabilities if not available
            if yes_price is None or no_price is None:
                logger.debug(f"Could not extract prices for {question}, skipping")
                return None
            
            # Generate market URL
            slug = data.get("slug", market_id)
            url = f"https://polymarket.com/event/{slug}"
            
            # Parse end date if available
            end_date = None
            if "end_date_iso" in data:
                try:
                    end_date = datetime.fromisoformat(data["end_date_iso"].replace("Z", "+00:00"))
                except:
                    pass
            
            return Market(
                platform="polymarket",
                market_id=market_id,
                event_title=question,
                description=description,
                yes_price=yes_price,
                no_price=no_price,
                volume=data.get("volume"),
                liquidity=data.get("liquidity"),
                end_date=end_date,
                url=url
            )
            
        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"Failed to parse Polymarket market: {e}")
            return None

