"""
Data models for markets and arbitrage opportunities.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Market:
    """Represents a binary prediction market."""
    platform: str  # "polymarket" or "kalshi"
    market_id: str
    event_title: str
    description: Optional[str]
    yes_price: float  # Price to buy YES (0-1 for Polymarket, cents for Kalshi)
    no_price: float   # Price to buy NO
    yes_bid: Optional[float] = None
    yes_ask: Optional[float] = None
    no_bid: Optional[float] = None
    no_ask: Optional[float] = None
    volume: Optional[float] = None
    liquidity: Optional[float] = None
    end_date: Optional[datetime] = None
    url: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.platform}: {self.event_title} (Yes: ${self.yes_price:.2f}, No: ${self.no_price:.2f})"


@dataclass
class ArbitrageOpportunity:
    """Represents a detected arbitrage opportunity between two markets."""
    polymarket_market: Market
    kalshi_market: Market
    match_score: float  # Fuzzy match score (0-100)
    
    # Optimal betting strategy
    bet_polymarket_side: str  # "yes" or "no"
    bet_kalshi_side: str      # "yes" or "no"
    bet_polymarket_amount: float
    bet_kalshi_amount: float
    total_investment: float
    
    # Expected returns for each outcome
    profit_if_yes: float
    profit_if_no: float
    min_profit: float
    roi_percent: float  # Return on investment
    
    timestamp: datetime
    
    def to_json(self) -> dict:
        """Convert to JSON-serializable dict for alerts."""
        return {
            "event": self.polymarket_market.event_title,
            "match_score": round(self.match_score, 2),
            "polymarket_yes_prob": round(self.polymarket_market.yes_price, 4),
            "polymarket_no_prob": round(self.polymarket_market.no_price, 4),
            "kalshi_yes_prob": round(self.kalshi_market.yes_price / 100, 4),
            "kalshi_no_prob": round(self.kalshi_market.no_price / 100, 4),
            "recommendation": (
                f"Bet ${self.bet_polymarket_amount:.2f} on {self.bet_polymarket_side.upper()} (Polymarket), "
                f"${self.bet_kalshi_amount:.2f} on {self.bet_kalshi_side.upper()} (Kalshi). "
                f"Profit: ${self.profit_if_yes:.2f} if Yes, ${self.profit_if_no:.2f} if No."
            ),
            "total_investment": round(self.total_investment, 2),
            "min_profit": round(self.min_profit, 2),
            "roi_percent": round(self.roi_percent, 2),
            "timestamp": self.timestamp.isoformat(),
            "link_poly": self.polymarket_market.url or "N/A",
            "link_kalshi": self.kalshi_market.url or "N/A",
        }
    
    def __str__(self) -> str:
        return (
            f"ARBITRAGE FOUND!\n"
            f"Event: {self.polymarket_market.event_title}\n"
            f"Match Score: {self.match_score:.1f}%\n"
            f"Strategy: Bet ${self.bet_polymarket_amount:.2f} on {self.bet_polymarket_side.upper()} (Polymarket), "
            f"${self.bet_kalshi_amount:.2f} on {self.bet_kalshi_side.upper()} (Kalshi)\n"
            f"Total Investment: ${self.total_investment:.2f}\n"
            f"Min Profit: ${self.min_profit:.2f} (ROI: {self.roi_percent:.2f}%)\n"
            f"Polymarket: {self.polymarket_market.url}\n"
            f"Kalshi: {self.kalshi_market.url}"
        )

