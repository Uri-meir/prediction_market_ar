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
    
    def __init__(self, polymarket_fee: float = None, predictit_fee: float = None,
                 min_profit: float = None):
        """
        Initialize arbitrage calculator.
        
        Args:
            polymarket_fee: Fee rate for Polymarket (0.02 = 2%)
            predictit_fee: Fee rate for PredictIt (0.10 = 10%)
            min_profit: Minimum profit required in USD
        """
        self.polymarket_fee = polymarket_fee or Config.POLYMARKET_FEE
        self.predictit_fee = predictit_fee or Config.PREDICTIT_FEE
        self.min_profit = min_profit or Config.MIN_PROFIT_USD
    
    def _get_platform_fee(self, platform: str) -> float:
        """Get fee for a platform by name."""
        if platform == "polymarket":
            return self.polymarket_fee
        elif platform == "predictit":
            return self.predictit_fee
        elif platform == "kalshi":
            return Config.KALSHI_FEE  # For backward compatibility
        else:
            logger.warning(f"Unknown platform {platform}, using 0.05 (5%) as default")
            return 0.05
    
    def check_arbitrage(self, poly_market: Market, platform2_market: Market,
                       match_score: float) -> Optional[ArbitrageOpportunity]:
        """
        Check if arbitrage opportunity exists between two matched markets.
        
        Strategy: Try all 4 combinations:
        1. YES on Polymarket, NO on Platform 2
        2. NO on Polymarket, YES on Platform 2
        3. YES on both (shouldn't have arb)
        4. NO on both (shouldn't have arb)
        
        Returns the best arbitrage opportunity if one exists.
        """
        opportunities = []
        
        # Strategy 1: YES on Polymarket, NO on Platform 2
        opp1 = self._calculate_arbitrage(
            poly_market, platform2_market, match_score,
            poly_side="yes", platform2_side="no"
        )
        if opp1:
            opportunities.append(opp1)
        
        # Strategy 2: NO on Polymarket, YES on Platform 2
        opp2 = self._calculate_arbitrage(
            poly_market, platform2_market, match_score,
            poly_side="no", platform2_side="yes"
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
    
    def _calculate_arbitrage(self, poly_market: Market, platform2_market: Market,
                           match_score: float, poly_side: str, 
                           platform2_side: str) -> Optional[ArbitrageOpportunity]:
        """
        Calculate arbitrage for a specific betting strategy.
        
        Args:
            poly_market: Polymarket market
            platform2_market: Second platform market (PredictIt, Kalshi, etc.)
            match_score: Fuzzy match score
            poly_side: "yes" or "no" - which side to bet on Polymarket
            platform2_side: "yes" or "no" - which side to bet on platform 2
            
        Returns:
            ArbitrageOpportunity if profitable, None otherwise
        """
        # Get prices (both platforms use 0-1 after conversion)
        poly_price = poly_market.yes_price if poly_side == "yes" else poly_market.no_price
        platform2_price = platform2_market.yes_price if platform2_side == "yes" else platform2_market.no_price
        
        # Check for invalid prices
        if poly_price <= 0 or poly_price >= 1 or platform2_price <= 0 or platform2_price >= 1:
            return None
        
        # Get fees for both platforms
        poly_fee = self.polymarket_fee
        platform2_fee = self._get_platform_fee(platform2_market.platform)
        
        # Calculate effective returns after fees
        # When you win a bet, payout = investment / price, profit = payout - investment
        # After fees: net_profit = (payout - investment) * (1 - fee)
        
        # For a $1 bet on Polymarket at price p:
        # If win: payout = $1/p, profit before fee = $(1/p - 1), after fee = $(1/p - 1)*(1-f)
        # Effective multiplier: 1 + (1/p - 1)*(1-f) = 1 + (1-p)*(1-f)/p
        
        # Simplified: effective return = (1 - fee) / price
        poly_effective_return = (1 - poly_fee) / poly_price
        platform2_effective_return = (1 - platform2_fee) / platform2_price
        
        # Arbitrage exists if combined returns > 1
        combined_return = 1 / poly_effective_return + 1 / platform2_effective_return
        
        if combined_return >= 1:
            # No arbitrage for this strategy
            return None
        
        # Calculate optimal bet distribution
        # We want to allocate capital such that profit is equal in both outcomes
        # Let x = amount bet on Polymarket, y = amount bet on Platform 2
        # Total investment = x + y
        
        # Outcome 1: Polymarket side wins
        # Profit = x * poly_effective_return - (x + y) = x * (poly_effective_return - 1) - y
        
        # Outcome 2: Platform 2 side wins
        # Profit = y * platform2_effective_return - (x + y) = y * (platform2_effective_return - 1) - x
        
        # For equal profit:
        # x * (poly_effective_return - 1) - y = y * (platform2_effective_return - 1) - x
        # x * poly_effective_return = y * platform2_effective_return
        # x / y = platform2_effective_return / poly_effective_return
        
        # Given a target minimum profit P, we need:
        # x * (poly_effective_return - 1) - y >= P
        # Solving the system of equations for equal profits at minimum P:
        
        # We'll use a target investment amount and calculate from there
        # Start with a base investment that aims for the minimum profit
        
        # For equal profits: ratio of bets
        ratio = platform2_effective_return / poly_effective_return
        
        # Let's say we bet $1 on Platform 2, then bet $ratio on Polymarket
        # Total investment = ratio + 1
        # Profit if Polymarket wins = ratio * poly_effective_return - (ratio + 1)
        # Profit if Platform 2 wins = 1 * platform2_effective_return - (ratio + 1)
        
        # These should be equal:
        unit_profit_poly = ratio * poly_effective_return - (ratio + 1)
        unit_profit_platform2 = platform2_effective_return - (ratio + 1)
        
        # The actual profit per dollar of total investment:
        unit_total_investment = ratio + 1
        unit_profit = min(unit_profit_poly, unit_profit_platform2)
        
        if unit_profit <= 0:
            return None
        
        # Scale up to meet minimum profit requirement
        scale_factor = self.min_profit / unit_profit
        
        poly_bet = ratio * scale_factor
        platform2_bet = scale_factor
        total_investment = unit_total_investment * scale_factor
        
        # Calculate actual profits for each outcome
        profit_if_poly_wins = poly_bet * poly_effective_return - total_investment
        profit_if_platform2_wins = platform2_bet * platform2_effective_return - total_investment
        
        # Determine which outcome corresponds to YES/NO
        if poly_side == "yes" and platform2_side == "no":
            profit_if_yes = profit_if_poly_wins
            profit_if_no = profit_if_platform2_wins
        elif poly_side == "no" and platform2_side == "yes":
            profit_if_yes = profit_if_platform2_wins
            profit_if_no = profit_if_poly_wins
        else:
            # Shouldn't happen with our strategy, but handle it
            profit_if_yes = min(profit_if_poly_wins, profit_if_platform2_wins)
            profit_if_no = min(profit_if_poly_wins, profit_if_platform2_wins)
        
        min_profit = min(profit_if_yes, profit_if_no)
        roi_percent = (min_profit / total_investment) * 100
        
        # Determine platform 2 side label
        platform2_name = platform2_market.platform
        platform2_side_label = "predictit" if platform2_name == "predictit" else platform2_name
        
        return ArbitrageOpportunity(
            polymarket_market=poly_market,
            kalshi_market=platform2_market,  # Using kalshi_market field for now (legacy)
            match_score=match_score,
            bet_polymarket_side=poly_side,
            bet_kalshi_side=platform2_side,  # Using kalshi_side field for now (legacy)
            bet_polymarket_amount=poly_bet,
            bet_kalshi_amount=platform2_bet,  # Using kalshi_amount field for now (legacy)
            total_investment=total_investment,
            profit_if_yes=profit_if_yes,
            profit_if_no=profit_if_no,
            min_profit=min_profit,
            roi_percent=roi_percent,
            timestamp=datetime.utcnow()
        )

