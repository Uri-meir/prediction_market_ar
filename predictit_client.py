"""
PredictIt API client for fetching binary prediction markets.
PredictIt API: https://www.predictit.org/api/marketdata/all
No authentication required - public API.
"""
import logging
import time
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

import requests  # Always import requests for exceptions

from models import Market
from config import Config

logger = logging.getLogger(__name__)


class PredictItClient:
    """Client for interacting with PredictIt API."""
    
    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or Config.PREDICTIT_API_URL
        
        # PredictIt is protected by Cloudflare, use cloudscraper if available
        if CLOUDSCRAPER_AVAILABLE:
            # cloudscraper automatically bypasses Cloudflare
            self.session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'darwin',
                    'desktop': True
                }
            )
            # Visit main page first to establish session and cookies
            try:
                self.session.get("https://www.predictit.org/", timeout=10)
                logger.debug("Using cloudscraper for PredictIt (bypasses Cloudflare)")
            except Exception as e:
                logger.warning(f"Failed to establish PredictIt session: {e}")
        else:
            # Fallback to requests (may fail with Cloudflare protection)
            self.session = requests.Session()
            self.session.headers.update({
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.predictit.org/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            })
            logger.warning("cloudscraper not installed - PredictIt API may be blocked by Cloudflare. Install with: pip install cloudscraper")
    
    def fetch_markets(self, limit: int = 200) -> List[Market]:
        """
        Fetch binary markets from PredictIt.
        
        Args:
            limit: Maximum number of markets to fetch
            
        Returns:
            List of Market objects
        """
        markets = []
        
        try:
            logger.debug(f"Fetching PredictIt markets from {self.api_url}")
            
            response = self.session.get(self.api_url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # PredictIt returns all markets in a list
            all_markets = data if isinstance(data, list) else data.get("markets", [])
            
            if not all_markets:
                logger.warning("PredictIt API returned empty market list")
                return []
            
            logger.info(f"Received {len(all_markets)} total markets from PredictIt")
            
            for item in all_markets:
                # Only process if we haven't reached the limit
                if len(markets) >= limit:
                    break
                
                market = self._parse_market(item)
                if market and self._is_binary_market(item):
                    markets.append(market)
            
            logger.info(f"Fetched {len(markets)} binary markets from PredictIt")
            return markets
            
        except requests.RequestException as e:
            logger.error(f"Error fetching PredictIt markets: {e}")
            if "403" in str(e):
                logger.warning(
                    "PredictIt API is blocked by Cloudflare. This is a known issue. "
                    "PredictIt has strict anti-bot protection. Options: "
                    "1. Wait for Kalshi account approval (recommended), "
                    "2. Try Manifold Markets (easier API access), "
                    "3. Use a VPN/proxy with PredictIt."
                )
            return []
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing PredictIt API response: {e}")
            return []
    
    def _is_binary_market(self, market_data: Dict[str, Any]) -> bool:
        """Check if a market is binary (exactly 2 contracts)."""
        contracts = market_data.get("contracts", [])
        return len(contracts) == 2
    
    def _parse_market(self, data: Dict[str, Any]) -> Optional[Market]:
        """
        Parse PredictIt API response into Market object.
        
        PredictIt prices are in cents (0-100), where 100 cents = $1.
        PredictIt uses "Yes" and "No" contracts for binary markets.
        """
        try:
            market_id = str(data.get("id", ""))
            name = data.get("name", "")
            short_name = data.get("shortName", "")
            
            # Use short name if available, otherwise full name
            event_title = short_name or name
            
            contracts = data.get("contracts", [])
            if len(contracts) != 2:
                return None
            
            # PredictIt binary markets have "Yes" and "No" contracts
            yes_contract = None
            no_contract = None
            
            for contract in contracts:
                contract_name = contract.get("name", "").lower()
                if contract_name == "yes":
                    yes_contract = contract
                elif contract_name == "no":
                    no_contract = contract
            
            if not yes_contract or not no_contract:
                # Try to infer: first contract = Yes, second = No
                yes_contract = contracts[0]
                no_contract = contracts[1]
            
            # Get prices - PredictIt prices are in cents (0-100)
            # Use bestBuyYesCost (what it costs to buy Yes) as the price
            # If not available, use lastTradePrice or bestBuyYesCost
            yes_price_cents = (
                yes_contract.get("bestBuyYesCost") or
                yes_contract.get("lastTradePrice") or
                yes_contract.get("price") or
                50  # Default to 50 cents if no price available
            )
            
            no_price_cents = (
                no_contract.get("bestBuyYesCost") or
                no_contract.get("lastTradePrice") or
                no_contract.get("price") or
                50
            )
            
            # Convert cents (0-100) to probability (0-1)
            # For PredictIt: bestBuyYesCost is what you pay to buy Yes
            # The probability is bestBuyYesCost / 100
            yes_price = float(yes_price_cents) / 100.0
            no_price = float(no_price_cents) / 100.0
            
            # Normalize: Yes + No should sum to ~1 (after accounting for fees)
            # PredictIt charges 10% fee on profits, so prices don't sum to exactly 1
            # But for arbitrage calculation, we'll use these as-is
            
            # Get bid/ask if available
            yes_bid = yes_contract.get("bestBuyYesCost") / 100.0 if yes_contract.get("bestBuyYesCost") else None
            yes_ask = yes_contract.get("bestSellYesCost") / 100.0 if yes_contract.get("bestSellYesCost") else None
            no_bid = no_contract.get("bestBuyYesCost") / 100.0 if no_contract.get("bestBuyYesCost") else None
            no_ask = no_contract.get("bestSellYesCost") / 100.0 if no_contract.get("bestSellYesCost") else None
            
            # Get volume
            volume = data.get("volume") or data.get("totalVolume")
            
            # Generate market URL
            url = f"https://www.predictit.org/markets/detail/{market_id}/{data.get('urlSlug', '')}"
            
            # Parse end date
            end_date = None
            if "dateEnd" in data:
                try:
                    end_date = datetime.fromisoformat(data["dateEnd"].replace("Z", "+00:00"))
                except:
                    pass
            
            return Market(
                platform="predictit",
                market_id=market_id,
                event_title=event_title,
                description=data.get("description") or name,
                yes_price=yes_price,
                no_price=no_price,
                yes_bid=yes_bid,
                yes_ask=yes_ask,
                no_bid=no_bid,
                no_ask=no_ask,
                volume=volume,
                liquidity=data.get("liquidity"),
                end_date=end_date,
                url=url
            )
            
        except (KeyError, ValueError, TypeError) as e:
            logger.debug(f"Failed to parse PredictIt market: {e}")
            return None

