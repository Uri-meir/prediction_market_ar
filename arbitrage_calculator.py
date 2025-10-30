"""
Arbitrage detection and calculation logic.

For a binary market, arbitrage exists when you can bet on both outcomes
across two platforms such that you profit regardless of the outcome.

Mathematical foundation:
- Let p1 = price of YES on platform 1, p2 = price of NO on platform 2
- Let f1, f2 = fees on platforms 1 and 2
- Arbitrage exists if: (1-f1)/p1 + (1-f2)/p2 > 1

When arbitrage exists, we want to find optimal bet amounts that:
1. Guarantee profit in both outcomes
2. Meet minimum profit requirement (e.g., $100)
3. Equalize or maximize profit across both outcomes
"""
import logging
from typing import Optional
from datetime import datetime

from models import Market, ArbitrageOpportunity
from config import Config

logger = logging.getLogger(__name__)


class ArbitrageCalculator:
    """Calculate arbitrage opportunities between matched markets."""
    
    def __init__(self, polymarket_fee: float = None, kalshi_fee: float = None,
                 min_profit: float = None):
        """
        Initialize arbitrage calculator.
        
        Args:
            polymarket_fee: Fee rate for Polymarket (0.02 = 2%)
            kalshi_fee: Fee rate for Kalshi (0.07 = 7%)
            min_profit: Minimum profit required in USD
        """
        self.polymarket_fee = polymarket_fee or Config.POLYMARKET_FEE
        self.kalshi_fee = kalshi_fee or Config.KALSHI_FEE
        self.min_profit = min_profit or Config.MIN_PROFIT_USD
    
    def check_arbitrage(self, poly_market: Market, kalshi_market: Market,
                       match_score: float) -> Optional[ArbitrageOpportunity]:
        """
        Check if arbitrage opportunity exists between two matched markets.
        
        Strategy: Try all 4 combinations:
        1. YES on Polymarket, NO on Kalshi
        2. NO on Polymarket, YES on Kalshi
        3. YES on both (shouldn't have arb)
        4. NO on both (shouldn't have arb)
        
        Returns the best arbitrage opportunity if one exists.
        """
        opportunities = []
        
        # Strategy 1: YES on Polymarket, NO on Kalshi
        opp1 = self._calculate_arbitrage(
            poly_market, kalshi_market, match_score,
            poly_side="yes", kalshi_side="no"
        )
        if opp1:
            opportunities.append(opp1)
        
        # Strategy 2: NO on Polymarket, YES on Kalshi
        opp2 = self._calculate_arbitrage(
            poly_market, kalshi_market, match_score,
            poly_side="no", kalshi_side="yes"
        )
        if opp2:
            opportunities.append(opp2)
        
        # Return the opportunity with highest minimum profit
        if opportunities:
            best = max(opportunities, key=lambda x: x.min_profit)
            if best.min_profit >= self.min_profit:
                logger.info(f"ARBITRAGE FOUND: {best.polymarket_market.event_title}")
                logger.info(f"  Min profit: ${best.min_profit:.2f}, ROI: {best.roi_percent:.2f}%")
                return best
        
        return None
    
    def _calculate_arbitrage(self, poly_market: Market, kalshi_market: Market,
                           match_score: float, poly_side: str, 
                           kalshi_side: str) -> Optional[ArbitrageOpportunity]:
        """
        Calculate arbitrage for a specific betting strategy.
        
        Args:
            poly_market: Polymarket market
            kalshi_market: Kalshi market
            match_score: Fuzzy match score
            poly_side: "yes" or "no" - which side to bet on Polymarket
            kalshi_side: "yes" or "no" - which side to bet on Kalshi
            
        Returns:
            ArbitrageOpportunity if profitable, None otherwise
        """
        # Get prices (Polymarket uses 0-1, Kalshi uses 0-1 after conversion)
        poly_price = poly_market.yes_price if poly_side == "yes" else poly_market.no_price
        kalshi_price = kalshi_market.yes_price if kalshi_side == "yes" else kalshi_market.no_price
        
        # Check for invalid prices
        if poly_price <= 0 or poly_price >= 1 or kalshi_price <= 0 or kalshi_price >= 1:
            return None
        
        # Calculate effective returns after fees
        # When you win a bet, payout = investment / price, profit = payout - investment
        # After fees: net_profit = (payout - investment) * (1 - fee)
        
        # For a $1 bet on Polymarket at price p:
        # If win: payout = $1/p, profit before fee = $(1/p - 1), after fee = $(1/p - 1)*(1-f)
        # Effective multiplier: 1 + (1/p - 1)*(1-f) = 1 + (1-p)*(1-f)/p
        
        # Simplified: effective return = (1 - fee) / price
        poly_effective_return = (1 - self.polymarket_fee) / poly_price
        kalshi_effective_return = (1 - self.kalshi_fee) / kalshi_price
        
        # Arbitrage exists if combined returns > 1
        combined_return = 1 / poly_effective_return + 1 / kalshi_effective_return
        
        if combined_return >= 1:
            # No arbitrage for this strategy
            return None
        
        # Calculate optimal bet distribution
        # We want to allocate capital such that profit is equal in both outcomes
        # Let x = amount bet on Polymarket, y = amount bet on Kalshi
        # Total investment = x + y
        
        # Outcome 1: Polymarket side wins
        # Profit = x * poly_effective_return - (x + y) = x * (poly_effective_return - 1) - y
        
        # Outcome 2: Kalshi side wins
        # Profit = y * kalshi_effective_return - (x + y) = y * (kalshi_effective_return - 1) - x
        
        # For equal profit:
        # x * (poly_effective_return - 1) - y = y * (kalshi_effective_return - 1) - x
        # x * poly_effective_return = y * kalshi_effective_return
        # x / y = kalshi_effective_return / poly_effective_return
        
        # Given a target minimum profit P, we need:
        # x * (poly_effective_return - 1) - y >= P
        # Solving the system of equations for equal profits at minimum P:
        
        # We'll use a target investment amount and calculate from there
        # Start with a base investment that aims for the minimum profit
        
        # For equal profits: ratio of bets
        ratio = kalshi_effective_return / poly_effective_return
        
        # Let's say we bet $1 on Kalshi, then bet $ratio on Polymarket
        # Total investment = ratio + 1
        # Profit if Polymarket wins = ratio * poly_effective_return - (ratio + 1)
        # Profit if Kalshi wins = 1 * kalshi_effective_return - (ratio + 1)
        
        # These should be equal:
        unit_profit_poly = ratio * poly_effective_return - (ratio + 1)
        unit_profit_kalshi = kalshi_effective_return - (ratio + 1)
        
        # The actual profit per dollar of total investment:
        unit_total_investment = ratio + 1
        unit_profit = min(unit_profit_poly, unit_profit_kalshi)
        
        if unit_profit <= 0:
            return None
        
        # Scale up to meet minimum profit requirement
        scale_factor = self.min_profit / unit_profit
        
        poly_bet = ratio * scale_factor
        kalshi_bet = scale_factor
        total_investment = unit_total_investment * scale_factor
        
        # Calculate actual profits for each outcome
        profit_if_poly_wins = poly_bet * poly_effective_return - total_investment
        profit_if_kalshi_wins = kalshi_bet * kalshi_effective_return - total_investment
        
        # Determine which outcome corresponds to YES/NO
        if poly_side == "yes" and kalshi_side == "no":
            profit_if_yes = profit_if_poly_wins
            profit_if_no = profit_if_kalshi_wins
        elif poly_side == "no" and kalshi_side == "yes":
            profit_if_yes = profit_if_kalshi_wins
            profit_if_no = profit_if_poly_wins
        else:
            # Shouldn't happen with our strategy, but handle it
            profit_if_yes = min(profit_if_poly_wins, profit_if_kalshi_wins)
            profit_if_no = min(profit_if_poly_wins, profit_if_kalshi_wins)
        
        min_profit = min(profit_if_yes, profit_if_no)
        roi_percent = (min_profit / total_investment) * 100
        
        return ArbitrageOpportunity(
            polymarket_market=poly_market,
            kalshi_market=kalshi_market,
            match_score=match_score,
            bet_polymarket_side=poly_side,
            bet_kalshi_side=kalshi_side,
            bet_polymarket_amount=poly_bet,
            bet_kalshi_amount=kalshi_bet,
            total_investment=total_investment,
            profit_if_yes=profit_if_yes,
            profit_if_no=profit_if_no,
            min_profit=min_profit,
            roi_percent=roi_percent,
            timestamp=datetime.utcnow()
        )

