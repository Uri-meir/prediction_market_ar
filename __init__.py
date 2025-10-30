"""
Polymarket-Kalshi Arbitrage Detection System

An automated system for detecting risk-free arbitrage opportunities
between Polymarket and Kalshi prediction markets.

Modules:
    - config: Configuration management
    - models: Data models for markets and opportunities
    - polymarket_client: Polymarket API client
    - kalshi_client: Kalshi API client
    - market_matcher: Fuzzy matching logic
    - arbitrage_calculator: Arbitrage detection and calculation
    - alerting: Email and Telegram alerts
    - main: Main orchestration and scheduling

Usage:
    python main.py --mode once        # Single scan
    python main.py --mode scheduled   # Continuous scanning
"""

__version__ = "1.0.0"
__author__ = "Arbitrage Detection System"

