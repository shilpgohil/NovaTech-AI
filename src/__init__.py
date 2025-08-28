"""
NovaTech AI Chatbot - Enhanced with LangChain and LangGraph
"""

__version__ = "2.0.0"
__author__ = "NovaTech Solutions"

# Import core modules
from . import config
from . import core
from . import integrations
from . import utils

# Import LangChain and LangGraph modules
from .utils.langchain_knowledge_manager import langchain_knowledge_manager
from .utils.langgraph_conversation_manager import langgraph_conversation_manager
from .integrations.langchain_gemini import langchain_gemini_client

__all__ = [
    "config",
    "core", 
    "integrations",
    "utils",
    "langchain_knowledge_manager",
    "langgraph_conversation_manager", 
    "langchain_gemini_client"
] 