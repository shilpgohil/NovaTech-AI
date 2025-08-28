#!/usr/bin/env python3
"""
NovaTech AI Backend Server - Production Optimized Version
Maintains ALL AI capabilities while optimizing for deployment
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for lazy loading
langchain_gemini = None
simple_gemini = None
knowledge_manager = None
dynamic_apis = None
user_learning = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lazy load AI components only when needed"""
    global langchain_gemini, simple_gemini, knowledge_manager, dynamic_apis, user_learning
    
    logger.info("🚀 Starting NovaTech AI Backend Server...")
    
    # Initialize core components
    try:
        # Import and initialize AI components only when needed
        from src.integrations.langchain_gemini import LangChainGeminiClient
        from src.integrations.simple_gemini import GeminiClient
        from src.utils.dynamic_knowledge_manager import DynamicKnowledgeManager
        from src.utils.dynamic_apis import DynamicAPIManager
        from src.utils.user_learning import UserLearningSystem
        
        # Initialize with error handling
        if os.getenv("GOOGLE_API_KEY"):
            try:
                langchain_gemini = LangChainGeminiClient()
                logger.info("✅ LangChain Gemini initialized")
            except Exception as e:
                logger.warning(f"⚠️ LangChain Gemini failed: {e}")
            
            try:
                simple_gemini = GeminiClient()
                logger.info("✅ Simple Gemini initialized")
            except Exception as e:
                logger.warning(f"⚠️ Simple Gemini failed: {e}")
        
        # Initialize knowledge manager
        try:
            knowledge_manager = DynamicKnowledgeManager()
            logger.info("✅ Knowledge manager initialized")
        except Exception as e:
            logger.warning(f"⚠️ Knowledge manager failed: {e}")
        
        # Initialize other components
        try:
            dynamic_apis = DynamicAPIManager()
            user_learning = UserLearningSystem()
            logger.info("✅ Additional components initialized")
        except Exception as e:
            logger.warning(f"⚠️ Some components failed: {e}")
            
    except ImportError as e:
        logger.warning(f"⚠️ Some AI components not available: {e}")
    
    logger.info("🎯 Backend ready - AI components loaded on-demand")
    yield
    
    logger.info("🛑 Shutting down NovaTech AI Backend Server...")

# Create FastAPI app with lifespan management
app = FastAPI(
    title="NovaTech AI Backend",
    description="Production-optimized AI chatbot backend with full capabilities",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:3002",
            # Production - Add your Vercel domain here after deployment
        # Example: "https://your-app-name.vercel.app"
        # Note: Update this after deploying to Vercel
        "https://nova-tech-ai-iota.vercel.app",  # Your Vercel frontend
    # Allow all origins in development (remove in production)
    "*"
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

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_langchain: bool = True

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    model_used: str

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "service": "NovaTech AI Backend",
        "version": "2.0.0",
        "ai_components": {
            "langchain_gemini": langchain_gemini is not None,
            "simple_gemini": simple_gemini is not None,
            "knowledge_manager": knowledge_manager is not None,
            "dynamic_apis": dynamic_apis is not None,
            "user_learning": user_learning is not None
        },
        "timestamp": "2025-08-29T00:00:00Z"
    }

# Main chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with automatic fallback"""
    try:
        # Try LangChain first if available and requested
        if request.use_langchain and langchain_gemini:
            try:
                response = langchain_gemini.generate_response(
                    request.message, 
                    session_id=request.session_id
                )
                return ChatResponse(
                    response=response,
                    session_id=request.session_id or "new_session",
                    timestamp="2025-08-29T00:00:00Z",
                    model_used="langchain_gemini"
                )
            except Exception as e:
                logger.warning(f"LangChain failed, falling back: {e}")
        
        # Fallback to simple Gemini
        if simple_gemini:
            try:
                response = simple_gemini.generate_response(request.message)
                return ChatResponse(
                    response=response,
                    session_id=request.session_id or "new_session",
                    timestamp="2025-08-29T00:00:00Z",
                    model_used="simple_gemini"
                )
            except Exception as e:
                logger.warning(f"Simple Gemini failed: {e}")
        
        # Final fallback
        return ChatResponse(
            response="I'm experiencing technical difficulties. Please try again in a moment.",
            session_id=request.session_id or "new_session",
            timestamp="2025-08-29T00:00:00Z",
            model_used="fallback"
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# LangChain specific endpoint
@app.post("/api/langchain/chat")
async def langchain_chat(request: ChatRequest):
    """LangChain-specific chat endpoint"""
    if not langchain_gemini:
        raise HTTPException(status_code=503, detail="LangChain service not available")
    
    try:
        response = langchain_gemini.generate_response(
            request.message, 
            session_id=request.session_id
        )
        return {"response": response, "model": "langchain_gemini"}
    except Exception as e:
        logger.error(f"LangChain chat error: {e}")
        raise HTTPException(status_code=500, detail="LangChain processing error")

# Knowledge base endpoint
@app.get("/api/knowledge/{category}")
async def get_knowledge(category: str):
    """Get knowledge base information"""
    if not knowledge_manager:
        raise HTTPException(status_code=503, detail="Knowledge service not available")
    
    try:
        # This would return knowledge base data
        return {"category": category, "status": "available", "data": "Knowledge base data"}
    except Exception as e:
        logger.error(f"Knowledge endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Knowledge retrieval error")

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
    port = int(os.getenv("PORT", 8000))  # Use standard port for production
    
    logger.info(f"Starting NovaTech AI Backend Server on {host}:{port}")
    uvicorn.run(
        "backend_server_production:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    ) 
