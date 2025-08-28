"""
Admin Authentication Module
Handles secure manual updates with admin verification
"""

import logging
from typing import Dict, Any, Optional, List
from src.config import config

logger = logging.getLogger(__name__)

class AdminAuth:
    """Admin authentication and update management"""
    
    def __init__(self):
        self.secret_key = config.ADMIN_SECRET_KEY
        self.confirmation_required = config.ADMIN_UPDATE_CONFIRMATION_REQUIRED
        self.confirmation_count = config.ADMIN_UPDATE_CONFIRMATION_COUNT
        self.update_options = config.UPDATE_OPTIONS
        
    def verify_admin_key(self, provided_key: str) -> bool:
        """Verify if the provided key matches admin secret"""
        return provided_key.strip() == self.secret_key
    
    def get_update_options(self) -> List[str]:
        """Get available update options"""
        return self.update_options.copy()
    
    def format_update_options(self) -> str:
        """Format update options for display"""
        options = self.get_update_options()
        formatted = []
        for option in options:
            if option == "all":
                formatted.append("• 'all' - Update everything")
            elif option == "news":
                formatted.append("• 'news' - Update company news only")
            elif option == "market":
                formatted.append("• 'market' - Update market data only")
            elif option == "industry":
                formatted.append("• 'industry' - Update industry trends only")
            elif option == "learning":
                formatted.append("• 'learning' - Update user learning only")
        
        return "\n".join(formatted)
    
    def validate_update_option(self, option: str) -> bool:
        """Validate if the update option is valid"""
        return option.lower() in self.update_options
    
    def get_confirmation_prompt(self, update_type: str) -> str:
        """Get confirmation prompt for update"""
        if update_type == "all":
            return f"⚠️  WARNING: You are about to update ALL knowledge sources.\nThis will refresh news, market data, industry trends, and learning data.\n\nType '{self.secret_key}' to confirm: "
        else:
            return f"⚠️  You are about to update {update_type.upper()} data.\nType '{self.secret_key}' to confirm: "
    
    def require_confirmation(self, update_type: str, user_input: str) -> bool:
        """Check if user confirmation is required and valid"""
        if not self.confirmation_required:
            return True
            
        # Check if user provided the admin key
        if not self.verify_admin_key(user_input):
            return False
            
        return True
    
    def get_update_summary(self, update_type: str) -> str:
        """Get summary of what will be updated"""
        if update_type == "all":
            return "🔄 **Full System Update**\n• Company news from all sources\n• Market data and stock quotes\n• Industry trends and SEC filings\n• User learning and FAQ generation"
        elif update_type == "news":
            return "📰 **News Update**\n• Company news from NewsAPI.org\n• Company news from GNews\n• Remove duplicates and sort by date"
        elif update_type == "market":
            return "💰 **Market Data Update**\n• Stock quotes from Alpha Vantage\n• Market sentiment from Finnhub\n• Financial trends and analysis"
        elif update_type == "industry":
            return "📈 **Industry Trends Update**\n• SEC filings and company documents\n• Market sentiment analysis\n• Industry intelligence data"
        elif update_type == "learning":
            return "🧠 **Learning Update**\n• Generate new FAQ entries\n• Analyze user interaction patterns\n• Update learning recommendations"
        else:
            return "❓ **Unknown Update Type**" 