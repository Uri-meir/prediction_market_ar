"""
Configuration module for arbitrage detection system.
Loads settings from environment variables with sensible defaults.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the arbitrage detection system."""
    
    # Polymarket Configuration
    POLYMARKET_API_URL: str = os.getenv("POLYMARKET_API_URL", "https://gamma-api.polymarket.com")
    
    # PredictIt Configuration
    PREDICTIT_API_URL: str = os.getenv("PREDICTIT_API_URL", "https://www.predictit.org/api/marketdata/all")
    
    # Kalshi Configuration (kept for backward compatibility)
    KALSHI_API_URL: str = os.getenv("KALSHI_API_URL", "https://trading-api.kalshi.com/trade-api/v2")
    KALSHI_EMAIL: Optional[str] = os.getenv("KALSHI_EMAIL")
    KALSHI_PASSWORD: Optional[str] = os.getenv("KALSHI_PASSWORD")
    KALSHI_API_KEY: Optional[str] = os.getenv("KALSHI_API_KEY")
    
    # Email Alert Configuration
    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    EMAIL_SMTP_HOST: str = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
    EMAIL_SMTP_PORT: int = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM")
    EMAIL_TO: Optional[str] = os.getenv("EMAIL_TO")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")
    
    # Telegram Alert Configuration (Optional)
    TELEGRAM_ENABLED: bool = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")
    
    # Arbitrage Configuration
    MIN_PROFIT_USD: float = float(os.getenv("MIN_PROFIT_USD", "100"))
    SCAN_INTERVAL_MINUTES: int = int(os.getenv("SCAN_INTERVAL_MINUTES", "5"))
    
    # Platform fees (as decimal, e.g., 0.02 = 2%)
    # Polymarket typically charges ~2% on profits
    POLYMARKET_FEE: float = float(os.getenv("POLYMARKET_FEE", "0.02"))
    
    # PredictIt charges ~10% on profits
    PREDICTIT_FEE: float = float(os.getenv("PREDICTIT_FEE", "0.10"))
    
    # Kalshi charges ~7% on profits (varies by contract)
    KALSHI_FEE: float = float(os.getenv("KALSHI_FEE", "0.07"))
    
    # Matching Configuration
    FUZZY_MATCH_THRESHOLD: int = int(os.getenv("FUZZY_MATCH_THRESHOLD", "85"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        errors = []
        
        if cls.EMAIL_ENABLED:
            if not cls.EMAIL_FROM:
                errors.append("EMAIL_FROM is required when EMAIL_ENABLED=true")
            if not cls.EMAIL_TO:
                errors.append("EMAIL_TO is required when EMAIL_ENABLED=true")
            if not cls.EMAIL_PASSWORD:
                errors.append("EMAIL_PASSWORD is required when EMAIL_ENABLED=true")
        
        if cls.TELEGRAM_ENABLED:
            if not cls.TELEGRAM_BOT_TOKEN:
                errors.append("TELEGRAM_BOT_TOKEN is required when TELEGRAM_ENABLED=true")
            if not cls.TELEGRAM_CHAT_ID:
                errors.append("TELEGRAM_CHAT_ID is required when TELEGRAM_ENABLED=true")
        
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {err}" for err in errors))


# Validate configuration on import
Config.validate()

