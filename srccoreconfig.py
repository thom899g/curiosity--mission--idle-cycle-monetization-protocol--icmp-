"""
Configuration management for CURIOSITY ICMP with validation and type safety.
"""
import os
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field, validator
from dataclasses import dataclass
from decimal import Decimal
import json

class SystemConfig(BaseSettings):
    """
    Centralized configuration with validation and environment variable support.
    """
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Firebase Configuration
    firebase_project_id: str = Field(..., env="FIREBASE_PROJECT_ID")
    firebase_database_url: str = Field(..., env="FIREBASE_DATABASE_URL")
    firebase_service_account_path: str = Field(..., env="FIREBASE_SERVICE_ACCOUNT_PATH")
    
    # RPC Configuration
    infura_project_id: Optional[str] = Field(None, env="INFURA_PROJECT_ID")
    alchemy_api_key: Optional[str] = Field(None, env="ALCHEMY_API_KEY")
    quicknode_url: Optional[str] = Field(None, env="QUICKNODE_URL")
    
    # Exchange APIs
    binance_api_key: Optional[str] = Field(None, env="BINANCE_API_KEY")
    binance_secret: Optional[str] = Field(None, env="BINANCE_SECRET")
    coinbase_api_key: Optional[str] = Field(None, env="COINBASE_API_KEY")
    coinbase_secret: Optional[str] = Field(None, env="COINBASE_SECRET")
    
    # Safety Limits
    max_deployed_capital_percentage: Decimal = Field(Decimal("10"), env="MAX_DEPLOYED_CAPITAL_PERCENTAGE")
    max_strategy_exposure_percentage: Decimal = Field(Decimal("2"), env="MAX_STRATEGY_EXPOSURE_PERCENTAGE")
    daily_loss_limit_percentage: Decimal = Field(Decimal("5"), env="DAILY_LOSS_LIMIT_PERCENTAGE")
    min_profit_threshold: Decimal = Field(Decimal("0.0015"), env="MIN_PROFIT_THRESHOLD")
    
    # Telegram
    telegram_bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(None, env="TELEGRAM_CHAT_ID")
    
    # Validation
    @validator('max_deployed_capital_percentage', 'max_strategy_exposure_percentage', 'daily_loss_limit_percentage')
    def validate_percentages(cls, v):
        if not (Decimal("0") <= v <= Decimal("100")):
            raise ValueError(f"Percentage must be between 0 and 100, got {v}")
        return v
    
    @validator('min_profit_threshold')
    def validate_profit_threshold(cls, v):
        if v < Decimal("0"):
            raise ValueError(f"Profit threshold must be positive, got {v}")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        arbitrary_types_allowed = True
    
    def get_rpc_urls(self) -> Dict[str, str]:
        """Get all configured RPC URLs with fallback order."""
        urls = {}
        if self.infura_project_id:
            urls['infura'] = f"https://mainnet.infura.io/v3/{self.infura_project_id}"
        if self.alchemy_api_key:
            urls['alchemy'] = f"https://eth-mainnet.g.alchemy.com/v2/{self.alchemy_api_key}"
        if self.quicknode_url:
            urls['quicknode'] = self.quicknode_url
        return urls
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any errors."""
        errors = []
        
        # Check required files
        if not os.path.exists(self.firebase_service_account_path):
            errors.append(f"Firebase service account file not found: {self.firebase_service_account_path}")
        
        # Check at least one RPC is configured
        if not any([self.infura_project_id, self.alchemy