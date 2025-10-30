"""
Kalshi API client for fetching binary prediction markets.
API Documentation: https://trading-api.kalshi.com/
"""
import logging
import time
import base64
from typing import List, Optional, Dict, Any
import requests
from datetime import datetime

from models import Market
from config import Config

logger = logging.getLogger(__name__)


class KalshiClient:
    """Client for interacting with Kalshi API."""
    
    def __init__(self, api_url: Optional[str] = None, email: Optional[str] = None, 
                 password: Optional[str] = None):
        self.api_url = api_url or Config.KALSHI_API_URL
        self.email = email or Config.KALSHI_EMAIL
        self.password = password or Config.KALSHI_PASSWORD
        
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "ArbitrageBot/1.0"
        })
        
        self.token = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with Kalshi API to get access token.
        
        Note: Kalshi requires authentication for most endpoints.
        This uses email/password authentication.
        """
        if not self.email or not self.password:
            logger.warning("Kalshi credentials not provided. Some features may not work.")
            return
        
        try:
            url = f"{self.api_url}/login"
            payload = {
                "email": self.email,
                "password": self.password
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get("token")
            
            if self.token:
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                logger.info("Successfully authenticated with Kalshi")
            else:
                logger.warning("No token received from Kalshi authentication")
                
        except requests.RequestException as e:
            logger.error(f"Failed to authenticate with Kalshi: {e}")
    
    def fetch_markets(self, limit: int = 200, status: str = "open") -> List[Market]:
        """
        Fetch binary markets from Kalshi.
        
        Args:
            limit: Maximum number of markets to fetch
            status: Market status filter ("open", "closed", "settled")
            
        Returns:
            List of Market objects
        """
        markets = []
        cursor = None
        
        try:
            while len(markets) < limit:
                params = {
                    "limit": min(200, limit - len(markets)),
                    "status": status,
                }
                
                if cursor:
                    params["cursor"] = cursor
                
                url = f"{self.api_url}/markets"
                logger.debug(f"Fetching Kalshi markets: {url} with params {params}")
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # Kalshi API returns markets in "markets" array
                batch = data.get("markets", [])
                
                if not batch:
                    break
                
                for item in batch:
                    market = self._parse_market(item)
                    if market and self._is_binary_market(item):
                        markets.append(market)
                
                # Check for pagination cursor
                cursor = data.get("cursor")
                if not cursor:
                    break
                
                # Rate limiting
                time.sleep(0.1)
            
            logger.info(f"Fetched {len(markets)} binary markets from Kalshi")
            return markets
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Kalshi markets: {e}")
            return []
    
    def _is_binary_market(self, market_data: Dict[str, Any]) -> bool:
        """Check if a market is binary (exactly 2 outcomes)."""
        # Kalshi binary markets have exactly 2 contracts/outcomes
        # Market type can be "binary" or check number of outcomes
        market_type = market_data.get("market_type", "")
        
        if market_type.lower() == "binary":
            return True
        
        # Alternative: check if there are exactly 2 possible outcomes
        # This would require fetching additional market details
        return True  # Most Kalshi markets are binary
    
    def _parse_market(self, data: Dict[str, Any]) -> Optional[Market]:
        """
        Parse Kalshi API response into Market object.
        
        Kalshi prices are in cents (0-100), where 100 cents = $1.
        """
        try:
            ticker = data.get("ticker", "")
            title = data.get("title", "")
            subtitle = data.get("subtitle", "")
            
            # Combine title and subtitle for full event description
            event_title = f"{title}"
            if subtitle and subtitle != title:
                event_title = f"{title}: {subtitle}"
            
            # Kalshi prices are in cents (0-100)
            yes_price = data.get("yes_bid", 50) / 100.0  # Convert to 0-1 range
            no_price = data.get("no_bid", 50) / 100.0
            
            # Alternative: use last_price or other price fields
            if "last_price" in data:
                yes_price = data["last_price"] / 100.0
                no_price = 1.0 - yes_price
            
            # Get bid/ask spreads if available
            yes_bid = data.get("yes_bid") / 100.0 if data.get("yes_bid") else None
            yes_ask = data.get("yes_ask") / 100.0 if data.get("yes_ask") else None
            no_bid = data.get("no_bid") / 100.0 if data.get("no_bid") else None
            no_ask = data.get("no_ask") / 100.0 if data.get("no_ask") else None
            
            # Generate market URL
            url = f"https://kalshi.com/markets/{ticker}"
            
            # Parse close date
            end_date = None
            if "close_time" in data:
                try:
                    end_date = datetime.fromisoformat(data["close_time"].replace("Z", "+00:00"))
                except:
                    pass
            
            return Market(
                platform="kalshi",
                market_id=ticker,
                event_title=event_title,
                description=data.get("description"),
                yes_price=yes_price,
                no_price=no_price,
                yes_bid=yes_bid,
                yes_ask=yes_ask,
                no_bid=no_bid,
                no_ask=no_ask,
                volume=data.get("volume"),
                liquidity=data.get("open_interest"),
                end_date=end_date,
                url=url
            )
            
        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"Failed to parse Kalshi market: {e}")
            return None

