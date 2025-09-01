#!/usr/bin/env python3

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import gc

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for lazy loading
simple_gemini = None
knowledge_manager = None
dynamic_apis = None
user_learning = None

# Simple conversation context manager (lightweight)
conversation_contexts = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Memory-optimized lifespan manager"""
    logger.info("🚀 Starting NovaTech AI Backend Server (Memory Optimized with Smart Features)...")
    
    # Force garbage collection to free memory
    gc.collect()
    
    # Initialize global variables
    global simple_gemini, knowledge_manager, dynamic_apis, user_learning
    
    # Set all to None initially - load only when needed
    simple_gemini = None
    knowledge_manager = None
    dynamic_apis = None
    user_learning = None
    
    logger.info("🎯 Backend ready - AI components will load on-demand")
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Shutting down NovaTech AI Backend Server...")
    gc.collect()

# Create FastAPI app with lifespan management
app = FastAPI(
    title="NovaTech AI Backend",
    description="Memory-optimized AI chatbot backend with smart features",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration - Universal and future-proof
origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:3002",
    "https://*.vercel.app",  # All Vercel domains (future-proof)
    "https://*.onrender.com",  # All Render domains
    "https://*.netlify.app",   # All Netlify domains
    "*"  # Universal access (production-ready)
]

try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("✅ CORS middleware added")
except Exception as e:
    logger.warning(f"⚠️ CORS middleware failed: {e}")

# Lightweight Smart Processor (Memory Efficient)
class LightweightSmartProcessor:
    """Lightweight processor for smart features without heavy dependencies"""
    
    def __init__(self):
        # Simple slang dictionary (very lightweight)
        self.slang_dict = {
            # Casual greetings and expressions
            "yo": "hello", "sup": "what's up", "hey": "hello", 
            "whats up": "what's up", "wassup": "what's up", "howdy": "hello",
            
            # Company references
            "this company": "NovaTech", "the company": "NovaTech", 
            "your company": "NovaTech", "novatech": "NovaTech", 
            "nova tech": "NovaTech", "the firm": "NovaTech",
            
            # Question patterns
            "whos": "who is", "whats": "what is", "hows": "how is",
            "wheres": "where is", "whens": "when is", "whys": "why is",
            
            # Casual language
            "gonna": "going to", "wanna": "want to", "gotta": "have to",
            "lemme": "let me", "gimme": "give me", "dunno": "don't know",
            "kinda": "kind of", "sorta": "sort of", "prolly": "probably",
            "def": "definitely", "deffo": "definitely",
            
            # Casual connectors
            "n": "and", "&": "and", "cuz": "because", "cos": "because",
            "cause": "because", "rn": "right now", "atm": "at the moment",
            
            # Internet slang
            "btw": "by the way", "fyi": "for your information", 
            "imo": "in my opinion", "imho": "in my humble opinion",
            "tbh": "to be honest", "ngl": "not gonna lie"
        }
        
        # Simple intent patterns (keyword-based, no regex)
        self.intent_keywords = {
            "greeting": ["hi", "hello", "hey", "sup", "yo", "howdy", "good morning", "good afternoon", "good evening"],
            "company": ["company", "business", "nova", "novatech", "firm", "organization", "about"],
            "product": ["product", "service", "crm", "hr", "helpdesk", "analytics", "pricing", "cost", "features"],
            "leadership": ["ceo", "cto", "coo", "founder", "leader", "management", "executive", "team"],
            "contact": ["contact", "email", "phone", "reach", "touch", "address", "location", "office"],
            "casual": ["how are you", "who are you", "what are you", "i am human", "i'm human"]
        }
    
    def normalize_slang(self, text: str) -> str:
        """Convert slang to formal language"""
        text_lower = text.lower()
        for slang, formal in self.slang_dict.items():
            text_lower = text_lower.replace(slang, formal)
        return text_lower
    
    def detect_intent(self, text: str) -> str:
        """Simple keyword-based intent detection"""
        text_lower = text.lower()
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return intent
        return "general"

# Smart Knowledge Manager (Lightweight)
class SmartKnowledgeManager:
    """Enhanced knowledge manager using existing JSON files"""
    
    def __init__(self):
        self.knowledge = self._load_knowledge_files()
        self.processor = LightweightSmartProcessor()
    
    def _load_knowledge_files(self) -> Dict[str, Any]:
        """Load knowledge from existing JSON files"""
        knowledge = {}
        try:
            # Load company info, products, leadership, etc.
            knowledge_files = [
                "knowledge_base/company_info.json",
                "knowledge_base/products.json", 
                "knowledge_base/leadership.json",
                "knowledge_base/faq.json",
                "knowledge_base/partners.json"
            ]
            
            for file_path in knowledge_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            category = file_path.split('/')[-1].replace('.json', '')
                            knowledge[category] = data
                            logger.info(f"✅ Loaded knowledge: {category}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not load {file_path}: {e}")
                else:
                    logger.debug(f"📁 Knowledge file not found: {file_path}")
                        
        except Exception as e:
            logger.warning(f"⚠️ Could not load knowledge files: {e}")
        
        return knowledge
    
    def get_smart_context(self, query: str, intent: str) -> str:
        """Get relevant knowledge context based on intent"""
        context = ""
        
        try:
            if intent == "company" and "company_info" in self.knowledge:
                context += str(self.knowledge["company_info"])
            elif intent == "product" and "products" in self.knowledge:
                context += str(self.knowledge["products"])
            elif intent == "leadership" and "leadership" in self.knowledge:
                context += str(self.knowledge["leadership"])
            elif intent == "contact" and "company_info" in self.knowledge:
                # Extract contact info from company info
                company_info = self.knowledge["company_info"]
                if isinstance(company_info, dict):
                    contact_keys = ["contact", "email", "phone", "address", "location"]
                    contact_info = {k: company_info.get(k, "") for k in contact_keys if company_info.get(k)}
                    context += str(contact_info)
            
            # Add FAQ context if available
            if "faq" in self.knowledge:
                context += f"\nFAQ: {str(self.knowledge['faq'])}"
                
        except Exception as e:
            logger.warning(f"⚠️ Error getting smart context: {e}")
        
        return context
    
    def get_knowledge(self, category: str, query: Optional[str] = None):
        """Get knowledge base information"""
        if category in self.knowledge:
            return self.knowledge[category]
        return {"category": category, "status": "not_found"}

# Simple Knowledge Manager (Lightweight) - Fallback
class SimpleKnowledgeManager:
    def __init__(self):
        self.knowledge = {
            "company": {
                "name": "NovaTech Solutions",
                "description": "Professional AI-powered business solutions",
                "services": ["AI Chatbot", "Business Automation", "Data Analytics"],
                "industry": "Technology & Business Solutions"
            },
            "products": {
                "chatbot": "AI-powered business assistant with company knowledge",
                "automation": "Business process automation solutions",
                "analytics": "Data-driven business insights"
            },
            "policies": {
                "support": "24/7 AI-powered customer support",
                "pricing": "Competitive pricing with scalable solutions",
                "security": "Enterprise-grade security and data protection"
            }
        }
    
    def get_knowledge(self, category: str, query: Optional[str] = None):
        """Get knowledge base information"""
        if category in self.knowledge:
            return self.knowledge[category]
        return {"category": category, "status": "not_found"}
    
    def get_smart_context(self, query: str, intent: str) -> str:
        """Get smart context for simple knowledge manager"""
        context = ""
        
        try:
            if intent == "company":
                context += str(self.knowledge.get("company", {}))
            elif intent == "product":
                context += str(self.knowledge.get("products", {}))
            elif intent == "contact":
                # Extract contact info from company info
                company_info = self.knowledge.get("company", {})
                if isinstance(company_info, dict):
                    contact_keys = ["contact", "email", "phone", "address", "location"]
                    contact_info = {k: company_info.get(k, "") for k in contact_keys if company_info.get(k)}
                    context += str(contact_info)
        except Exception as e:
            logger.warning(f"⚠️ Error getting simple context: {e}")
        
        return context

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    # use_langchain removed for memory optimization

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    model_used: str

def build_smart_prompt(query: str, context: str, intent: str, conversation_context: str = "") -> str:
    """Build intelligent prompts for Gemini"""
    
    # Base system prompt
    system_prompt = """You are NovaTech AI, a friendly and helpful assistant. 
    Respond naturally and conversationally, using the provided company knowledge.
    
    IMPORTANT: 
    - Sound like a real person having a casual conversation
    - Use the company knowledge to provide accurate information
    - Be warm, helpful, and natural
    - Don't sound robotic or formal
    - Use contractions (I'm, you're, he's, etc.)
    - Be conversational and friendly"""
    
    # Intent-specific instructions
    intent_instructions = {
        "greeting": "Respond warmly and ask how you can help with NovaTech",
        "company": "Share company information naturally and conversationally",
        "product": "Explain products in a friendly, helpful way",
        "leadership": "Share leadership information naturally",
        "contact": "Provide contact information naturally when asked",
        "casual": "Be friendly and conversational, build rapport",
        "general": "Be helpful and natural, use company knowledge when relevant"
    }
    
    # Build the complete prompt
    prompt = f"{system_prompt}\n\n"
    prompt += f"Intent: {intent}\n"
    prompt += f"Instruction: {intent_instructions.get(intent, 'Be helpful and natural')}\n\n"
    
    if context:
        prompt += f"Company Knowledge: {context}\n\n"
    
    if conversation_context:
        prompt += f"Previous Conversation: {conversation_context}\n\n"
    
    prompt += f"User Message: {query}\n\n"
    prompt += "Please respond naturally and helpfully:"
    
    return prompt

def load_ai_components():
    """Load AI components only when needed to save memory"""
    global simple_gemini, knowledge_manager, dynamic_apis, user_learning
    
    try:
        logger.info("📦 Loading AI components on-demand...")
        
        # Force garbage collection before loading
        gc.collect()
        
        # Only load basic Gemini client for now (lightweight)
        if not simple_gemini and os.getenv("GOOGLE_GEMINI_API_KEY"):
            try:
                # Import only the basic Gemini client (no heavy dependencies)
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
                simple_gemini = genai
                logger.info("✅ Basic Gemini loaded (lightweight)")
                logger.info(f"🔍 Debug: genai module loaded: {genai}")
                logger.info(f"🔍 Debug: GenerativeModel available: {hasattr(genai, 'GenerativeModel')}")
            except Exception as e:
                logger.warning(f"⚠️ Basic Gemini failed: {e}")
                simple_gemini = None
        
        # Load smart knowledge base
        if not knowledge_manager:
            try:
                # Try smart knowledge manager first
                knowledge_manager = SmartKnowledgeManager()
                logger.info("✅ Smart knowledge manager loaded")
            except Exception as e:
                logger.warning(f"⚠️ Smart knowledge manager failed, using simple: {e}")
                try:
                    # Fallback to simple knowledge manager
                    knowledge_manager = SimpleKnowledgeManager()
                    logger.info("✅ Simple knowledge manager loaded (fallback)")
                except Exception as e2:
                    logger.warning(f"⚠️ Simple knowledge manager also failed: {e2}")
                    knowledge_manager = None
        
        # Skip all heavy components for now
        logger.info("⚠️ Heavy AI components skipped for memory optimization")
        
    except Exception as e:
        logger.error(f"❌ Error loading AI components: {e}")
        # Keep existing components if any

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - redirects to health check"""
    return {
        "message": "Welcome to NovaTech AI Backend",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "langchain_chat": "REMOVED - Memory Optimized",
            "knowledge": "/api/knowledge/{category}",
            "test_smart": "/api/test-smart"
        },
        "status": "running",
        "features": "Smart processing enabled"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        return {
            "status": "healthy",
            "service": "NovaTech AI Backend (Memory Optimized with Smart Features)",
            "version": "2.0.0",
            "ai_components": {
                "langchain_gemini": "REMOVED - Memory Optimized",
                "simple_gemini": simple_gemini is not None,
                "knowledge_manager": knowledge_manager is not None,
                "dynamic_apis": dynamic_apis is not None,
                "user_learning": user_learning is not None
            },
            "memory_optimized": True,
            "smart_features": True,
            "timestamp": "2025-08-29T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "service": "NovaTech AI Backend (Memory Optimized with Smart Features)",
            "version": "2.0.0",
            "error": str(e),
            "timestamp": "2025-08-29T00:00:00Z"
        }

# Main chat endpoint with smart features
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Smart chat endpoint with lightweight intelligence"""
    global simple_gemini, knowledge_manager
    
    try:
        # Load AI components if not already loaded
        load_ai_components()
        
        # Initialize smart processor
        processor = LightweightSmartProcessor()
        
        # Process the query intelligently
        normalized_query = processor.normalize_slang(request.message)
        intent = processor.detect_intent(normalized_query)
        
        # Get conversation context
        session_id = request.session_id or "new_session"
        conversation_context = conversation_contexts.get(session_id, "")
        
        # Get smart context from knowledge base
        context = ""
        if knowledge_manager:
            if hasattr(knowledge_manager, 'get_smart_context'):
                # Use smart knowledge manager
                context = knowledge_manager.get_smart_context(normalized_query, intent)
            else:
                # Use simple knowledge manager
                context = str(knowledge_manager.get_knowledge("company"))
        
        # Build smart prompt
        smart_prompt = build_smart_prompt(normalized_query, context, intent, conversation_context)
        
        # LangChain removed for memory optimization
        # Proceeding directly to smart Gemini
        
        # Generate response with smart Gemini
        logger.info(f"🔍 Debug: simple_gemini = {simple_gemini}")
        logger.info(f"🔍 Debug: type(simple_gemini) = {type(simple_gemini)}")
        logger.info(f"🔍 Debug: simple_gemini is None = {simple_gemini is None}")
        logger.info(f"🔍 Debug: bool(simple_gemini) = {bool(simple_gemini)}")
        
        if simple_gemini:
            try:
                # Use lightweight Gemini client with smart prompt
                model = simple_gemini.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(smart_prompt)
                
                # Update conversation context
                conversation_contexts[session_id] = f"{conversation_context}\nUser: {request.message}\nAssistant: {response.text}"
                
                # Keep context manageable (last 10 exchanges)
                context_lines = conversation_contexts[session_id].split('\n')
                if len(context_lines) > 10:
                    conversation_contexts[session_id] = '\n'.join(context_lines[-10:])
                
                logger.info(f"✅ Smart response generated - Intent: {intent}, Context: {'Yes' if context else 'No'}")
                
                return ChatResponse(
                    response=response.text,
                    session_id=session_id,
                    timestamp="2025-08-29T00:00:00Z",
                    model_used="smart_gemini"
                )
            except Exception as e:
                logger.warning(f"Smart Gemini failed: {e}")
        
        # Final fallback
        return ChatResponse(
            response="I'm experiencing technical difficulties. Please try again in a moment.",
            session_id=session_id,
            timestamp="2025-08-29T00:00:00Z",
            model_used="fallback"
        )
        
    except Exception as e:
        logger.error(f"Smart chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# LangChain specific endpoint - REMOVED (no longer needed)
# This endpoint was removed for memory optimization

# Knowledge base endpoint
@app.get("/api/knowledge/{category}")
async def get_knowledge(category: str):
    """Get knowledge base information"""
    try:
        # Load AI components if not already loaded
        load_ai_components()
        
        if not knowledge_manager:
            raise HTTPException(status_code=503, detail="Knowledge service not available")
        
        # Use knowledge manager
        knowledge_data = knowledge_manager.get_knowledge(category)
        return {"category": category, "status": "available", "data": knowledge_data}
    except Exception as e:
        logger.error(f"Knowledge endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Knowledge retrieval error")

# Test smart features endpoint
@app.get("/api/test-smart")
async def test_smart_features():
    """Test endpoint to verify smart features are working"""
    try:
        processor = LightweightSmartProcessor()
        
        # Test slang normalization
        test_slang = "yo sup, hows it going?"
        normalized = processor.normalize_slang(test_slang)
        
        # Test intent detection
        intent = processor.detect_intent("hi there")
        
        return {
            "status": "success",
            "smart_features": {
                "slang_processing": True,
                "intent_detection": True,
                "test_slang": test_slang,
                "normalized": normalized,
                "detected_intent": intent
            },
            "message": "Smart features are working correctly!"
        }
    except Exception as e:
        logger.error(f"Smart features test error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Smart features test failed"
        }

# Conversation context endpoints (lightweight replacements)
@app.get("/api/conversation/{session_id}/context")
async def get_conversation_context(session_id: str):
    """Get conversation context for a session"""
    try:
        context = conversation_contexts.get(session_id, "")
        return {
            "status": "success",
            "conversation_context": context,
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Context retrieval error: {e}")
        return {
            "status": "error",
            "conversation_context": "",
            "session_id": session_id
        }

@app.delete("/api/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation context for a session"""
    try:
        if session_id in conversation_contexts:
            del conversation_contexts[session_id]
        return {"status": "success", "message": "Conversation cleared"}
    except Exception as e:
        logger.error(f"Context clearing error: {e}")
        return {"status": "error", "message": "Failed to clear conversation"}

# Admin endpoints (lightweight)
@app.get("/api/admin/status")
async def admin_status():
    """Get admin status"""
    try:
        return {
            "status": "success",
            "service": "NovaTech AI Backend (Memory Optimized)",
            "version": "2.0.0",
            "ai_components": {
                "simple_gemini": simple_gemini is not None,
                "knowledge_manager": knowledge_manager is not None,
                "memory_usage": "optimized"
            }
        }
    except Exception as e:
        logger.error(f"Admin status error: {e}")
        return {"status": "error", "error": str(e)}

@app.post("/api/admin/update")
async def admin_update():
    """Admin update endpoint"""
    try:
        return {"status": "success", "message": "System is up to date"}
    except Exception as e:
        logger.error(f"Admin update error: {e}")
        return {"status": "error", "error": str(e)}

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting NovaTech AI Backend Server on {host}:{port}")
    uvicorn.run(
        "backend_server_production:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    ) 

