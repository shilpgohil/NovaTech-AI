"""
NovaTech AI Chatbot Package
AI-powered company assistant with dynamic knowledge system
"""

__version__ = "1.0.0"
__author__ = "NovaTech Solutions"
__email__ = "info@novatech.com"

# Add src to Python path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import main components
try:
    from src.config import config
    from src.integrations.simple_gemini import simple_gemini_client
    from src.integrations.langchain_gemini import langchain_gemini_client
except ImportError:
    # Allow imports to fail during development
    pass 