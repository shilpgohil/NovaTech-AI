"""
Gemini Client
Natural conversation system
"""

import logging
from typing import Dict, Any

try:
    import google.generativeai as genai  # type: ignore
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI not available.")

from ..config import config, get_error_message
from ..core.simple_context import context_provider

# Set up logging
logger = logging.getLogger(__name__)


class GeminiClient:
    """Gemini client for natural conversations"""
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
        
        if not GEMINI_AVAILABLE:
            logger.warning("Google Generative AI not available, client will be disabled")
            return
            
        if config.GEMINI_API_KEY:
            self._initialize_gemini()
        else:
            logger.warning("Gemini not available or API key missing")
    
    def _initialize_gemini(self):
        """Initialize Gemini with API key"""
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            
            # Use Gemini 1.5 Flash
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            self.is_initialized = True
            logger.info("Gemini initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            self.is_initialized = False
    
    def generate_response(self, query: str) -> str:
        """Generate response"""
        if not self.is_initialized:
            return get_error_message("api_key_missing")
        
        try:
            # Get context for the query
            context_data = context_provider.get_context_for_query(query)
            
            # Build prompt
            enhanced_prompt = self._build_prompt(query, context_data)
            
            # Generate response
            if not self.model:
                return get_error_message("api_key_missing")
            
            response = self.model.generate_content(enhanced_prompt)
            
            if response and response.text:
                logger.info(f"Response generated")
                return response.text
            else:
                return "I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return get_error_message("processing_error", str(e))
    
    def _build_prompt(self, query: str, context_data: Dict[str, Any]) -> str:
        """Build enhanced prompt with context"""
        
        # Extract relevant information from context without being formal
        context_info = context_data.get('context', '')
        
        system_prompt = f"""You are NovaTech AI, a friendly and helpful assistant. You're chatting with someone right now - be natural and conversational!

IMPORTANT: Sound like a real person having a casual conversation, not like a database or formal assistant.

COMMUNICATION STYLE:
• Talk like you're chatting with a friend
• Keep responses short, friendly, and natural
• Use contractions (I'm, you're, he's, etc.)
• Be warm and helpful
• Don't sound robotic or formal

ABOUT NOVATECH:
NovaTech is a SaaS company in Bengaluru that makes software for CRM, HR, Helpdesk, and Analytics. They help businesses work better with smart software.

HOW TO RESPOND:
• For greetings like "hi" or "hello": Respond warmly and ask how you can help
• For "how are you": Say you're doing great and ask about them
• For NovaTech questions: Give simple, natural answers
• For contact info: Share it naturally when asked
• If you don't know something: Say so casually and naturally
• Always be helpful and friendly

RELEVANT INFO (use this naturally in conversation, don't list it formally):
{context_info}

USER'S MESSAGE: {query}

Remember: Just be yourself and chat naturally like a helpful friend would!"""
        
        return system_prompt
    
    def clear_cache(self):
        """Clear response cache (no longer used)"""
        logger.debug("Cache clearing requested but no cache is maintained")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        context_stats = context_provider.get_stats()
        
        return {
            "is_initialized": self.is_initialized,
            "model": "gemini-1.5-flash",
            "cache_size": 0,
            "context_stats": context_stats
        }
    
    def reset_stats(self):
        """Reset statistics"""
        context_provider.clear_cache()
        logger.info("Statistics reset")


# Global Gemini client instance
simple_gemini_client = GeminiClient() 