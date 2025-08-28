"""
Configuration Management
Settings for the company assistant with dynamic knowledge capabilities
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass, field

# Load environment variables from .env file
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass  # dotenv not available


@dataclass
class AssistantConfig:
    """Configuration for the company assistant with dynamic knowledge"""
    
    # Core API Keys
    GEMINI_API_KEY: str = os.getenv("GOOGLE_GEMINI_API_KEY", "")
    
    # Dynamic Knowledge API Keys
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    GNEWS_API_KEY: str = os.getenv("GNEWS_API_KEY", "")
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    SEC_API_KEY: str = os.getenv("SEC_API_KEY", "")
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    REDDIT_SECRET_KEY: str = os.getenv("REDDIT_SECRET_KEY", "")
    
    # Legacy API Keys (kept for compatibility)
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
    TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "1024"))
    TOP_P: float = float(os.getenv("GEMINI_TOP_P", "0.8"))
    TOP_K: int = int(os.getenv("GEMINI_TOP_K", "40"))
    
    # LangChain Configuration
    LANGCHAIN_CHUNK_SIZE: int = int(os.getenv("LANGCHAIN_CHUNK_SIZE", "800"))
    LANGCHAIN_CHUNK_OVERLAP: int = int(os.getenv("LANGCHAIN_CHUNK_OVERLAP", "100"))
    LANGCHAIN_MAX_TOKENS: int = int(os.getenv("LANGCHAIN_MAX_TOKENS", "2048"))
    LANGCHAIN_TEMPERATURE: float = float(os.getenv("LANGCHAIN_TEMPERATURE", "0.3"))
    
    # LangGraph Configuration
    LANGGRAPH_MAX_ITERATIONS: int = int(os.getenv("LANGGRAPH_MAX_ITERATIONS", "10"))
    LANGGRAPH_MEMORY_SIZE: int = int(os.getenv("LANGGRAPH_MEMORY_SIZE", "5"))
    LANGGRAPH_CONVERSATION_TIMEOUT: int = int(os.getenv("LANGGRAPH_CONVERSATION_TIMEOUT", "300"))
    
    # Vector Database Configuration
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "faiss")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./vector_db")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    VECTOR_SIMILARITY_THRESHOLD: float = float(os.getenv("VECTOR_SIMILARITY_THRESHOLD", "0.7"))
    
    # HuggingFace Configuration
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")
    
    # Processing Thresholds
    ADVANCED_PROCESSING_CONFIDENCE_THRESHOLD: float = 0.5
    VECTOR_SEARCH_TOP_K: int = 5
    VECTOR_SEARCH_SIMILARITY_THRESHOLD: float = 0.3
    
    # Query Types for Company Information
    COMPANY_QUERY_TYPES: List[str] = field(default_factory=lambda: [
        "company_info", "products", "leadership", "partners", 
        "casual_chat", "contact_info", "news", "market_data", 
        "industry_trends", "user_learning"
    ])
    
    # File Processing Limits
    MAX_FILE_SIZE_MB: int = 10
    SUPPORTED_IMAGE_FORMATS: List[str] = field(default_factory=lambda: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"])
    SUPPORTED_DOCUMENT_FORMATS: List[str] = field(default_factory=lambda: [".pdf", ".docx", ".txt", ".md", ".csv", ".json", ".py", ".js", ".html"])
    
    # Cache Settings (in seconds)
    GITHUB_CACHE_TTL: int = 1800  # 30 minutes
    WEATHER_CACHE_TTL: int = 1800  # 30 minutes
    NEWS_CACHE_TTL: int = 3600    # 1 hour
    TECH_TRENDS_CACHE_TTL: int = 7200  # 2 hours
    
    # Dynamic Knowledge Settings
    DYNAMIC_UPDATE_INTERVAL: int = 3600  # 1 hour (3600 seconds)
    MANUAL_UPDATE_ENABLED: bool = True
    USER_LEARNING_ENABLED: bool = True
    MAX_USER_QUERIES_STORED: int = 1000
    LEARNING_CONFIDENCE_THRESHOLD: float = 0.7
    
    # Admin Authentication
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "NovaTech2024!")
    ADMIN_UPDATE_CONFIRMATION_REQUIRED: bool = True
    ADMIN_UPDATE_CONFIRMATION_COUNT: int = 2
    
    # Update Options
    UPDATE_OPTIONS: List[str] = field(default_factory=lambda: ["news", "market", "industry", "all", "learning"])
    
    # API Rate Limits (requests per hour)
    NEWS_API_RATE_LIMIT: int = 100  # 100 requests/day = ~4/hour
    GNEWS_RATE_LIMIT: int = 100     # 100 requests/day = ~4/hour
    ALPHA_VANTAGE_RATE_LIMIT: int = 25  # 500 requests/day = ~25/hour
    FINNHUB_RATE_LIMIT: int = 60    # 60 requests/minute
    TWITTER_RATE_LIMIT: int = 300   # 300 requests/15min
    
    # CLI Commands
    EXIT_COMMANDS: List[str] = field(default_factory=lambda: ["exit", "quit", "bye", "goodbye", "q"])
    STATS_COMMANDS: List[str] = field(default_factory=lambda: ["stats", "statistics", "info", "analytics"])
    UPDATE_COMMANDS: List[str] = field(default_factory=lambda: ["update", "refresh", "sync", "reload", "force_update"])
    
    # Knowledge base files
    KNOWLEDGE_BASE_FILES: Dict[str, str] = field(default_factory=lambda: {
        "company_info": "knowledge_base/company_info.json",
        "leadership": "knowledge_base/leadership.json",
        "products": "knowledge_base/products.json",
        "partners": "knowledge_base/partners.json",
        "faq": "knowledge_base/faq.json",
        "marketing": "knowledge_base/marketing.json",
        # Dynamic knowledge files
        "news": "knowledge_base/news.json",
        "market_data": "knowledge_base/market_data.json",
        "industry_trends": "knowledge_base/industry_trends.json",
        "user_learning": "knowledge_base/user_learning.json"
    })




# Global configuration instance
config = AssistantConfig()


def get_model_config() -> Dict[str, Any]:
    """Get model configuration"""
    return {
        "model": config.MODEL_NAME,
        "generation_config": {
            "temperature": config.TEMPERATURE,
            "max_output_tokens": config.MAX_OUTPUT_TOKENS,
            "top_p": config.TOP_P,
            "top_k": config.TOP_K,
        },
        "safety_settings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
    }


def is_exit_command(command: str) -> bool:
    """Check if command is an exit command"""
    return command.lower().strip() in config.EXIT_COMMANDS


def is_stats_command(command: str) -> bool:
    """Check if command is a stats command"""
    return command.lower().strip() in config.STATS_COMMANDS


def is_reset_command(command: str) -> bool:
    """Check if command is a reset command"""
    return command.lower().strip() in ["reset", "clear", "restart"]


def is_update_command(command: str) -> bool:
    """Check if command is an update command"""
    return command.lower().strip() in config.UPDATE_COMMANDS


def get_error_message(error_type: str, details: str = "") -> str:
    """Get error message"""
    error_messages = {
        "api_key_missing": "I'm sorry, but I'm having trouble connecting to my AI services at the moment. This usually happens when the API key isn't set up properly.",
        "file_too_large": f"I'm afraid that file is too large for me to process. The maximum size I can handle is {config.MAX_FILE_SIZE_MB}MB. Could you try with a smaller file?",
        "unsupported_format": "I'm sorry, but I don't recognise that file format. I can work with most common document and image formats though.",
        "network_error": "I'm having trouble connecting to the internet right now. Could you check your connection and try again?",
        "processing_error": "I'm sorry, but I ran into an issue while processing your request. Could you try asking again?",
        "vector_search_error": "I'm having a bit of trouble searching through my knowledge base, but I'll do my best to help you with what I know.",
        "external_api_error": "Some of my external services are temporarily unavailable, but I can still help you with the information I have.",
    }
    
    base_message = error_messages.get(error_type, "I'm sorry, but something unexpected happened. Could you try again?")
    return f"{base_message}\n{details}" if details else base_message


def validate_environment() -> Dict[str, bool]:
    """Validate environment setup"""
    validation = {
        "gemini_api": bool(config.GEMINI_API_KEY),
        "news_api": bool(config.NEWS_API_KEY),
        "gnews_api": bool(config.GNEWS_API_KEY),
        "alpha_vantage_api": bool(config.ALPHA_VANTAGE_API_KEY),
        "finnhub_api": bool(config.FINNHUB_API_KEY),
        "sec_api": bool(config.SEC_API_KEY),
        "twitter_api": bool(config.TWITTER_API_KEY),
        "reddit_api": bool(config.REDDIT_SECRET_KEY),
        "github_token": bool(config.GITHUB_TOKEN),
        "weather_api": bool(config.WEATHER_API_KEY),
    }
    return validation


def get_welcome_message() -> str:
    """Get welcome message"""
    return """
🏢 Hello there! I'm NovaTech Solutions' AI assistant with DYNAMIC KNOWLEDGE capabilities! I'm here to help you learn all about our company, products, and services.

I can tell you about our SaaS products (NovaCRM, NovaHR, NovaDesk, NovaAnalytics), our leadership team, strategic partners, company mission and values, pricing information, and much more. I can also help with FAQ, support information, and marketing content.

🚀 NEW FEATURES:
• Real-time company news and market updates
• Industry trends and competitor analysis
• Learning from our conversations to improve
• Hourly knowledge updates (automatic)
• Manual knowledge refresh on demand

I understand casual language perfectly, so feel free to ask me anything naturally. You might say something like "what products do you offer?" or "who's your CEO?" and I'll understand exactly what you mean.

💡 SPECIAL COMMANDS:
• 'stats' - See conversation statistics
• 'update' - Force immediate knowledge refresh
• 'news' - Get latest company news
• 'market' - Check market data
• 'exit' - When you're ready to finish

What would you like to know about NovaTech Solutions?
"""


def get_processing_status_message(stage: str) -> str:
    """Get status message"""
    messages = {
        "normalizing": "Let me understand what you're asking...",
        "searching": "Looking through my knowledge about NovaTech...",
        "analyzing": "Thinking about this...",
        "generating": "Putting together a response for you...",
        "complete": "Here's what I found for you!"
    }
    return messages.get(stage, "Working on that for you...")


# Knowledge base paths
KNOWLEDGE_BASE_DIR = "knowledge_base"


def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    validation = validate_environment()
    return {
        "version": "2.0.0",
        "model": config.MODEL_NAME,
        "api_status": validation,
        "knowledge_base_files": list(config.KNOWLEDGE_BASE_FILES.keys()),
        "supported_formats": {
            "images": config.SUPPORTED_IMAGE_FORMATS,
            "documents": config.SUPPORTED_DOCUMENT_FORMATS
        }
    } 