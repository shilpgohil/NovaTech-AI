"""
NovaTech AI Backend Server
FastAPI server integrating with dynamic knowledge system
"""

import os
import sys
import logging
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from pydantic import BaseModel  # type: ignore
import uvicorn  # type: ignore

# Load environment variables from .env file
try:
    from dotenv import load_dotenv  # type: ignore
    # Load from env_local.txt instead of .env
    load_dotenv("env_local.txt")
    
    # The API key is now handled centrally in src/config.py
    # No need to set it here - it's automatically loaded from environment
        
except ImportError:
    print("Warning: python-dotenv not installed. API keys will be loaded from environment variables.")

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Now import modules with error handling
try:
    from fastapi.middleware.cors import CORSMiddleware  # type: ignore
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    logger.warning("FastAPI CORS middleware not available. CORS will be disabled.")

try:
    from src.utils.dynamic_integration import get_dynamic_integration
    from src.integrations.simple_gemini import simple_gemini_client
    from src.integrations.langchain_gemini import langchain_gemini_client
    from src.utils.langchain_knowledge_manager import langchain_knowledge_manager
    from src.utils.langgraph_conversation_manager import langgraph_conversation_manager
    from src.utils.admin_auth import AdminAuth
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="NovaTech AI Backend",
    description="AI-powered company assistant with dynamic knowledge",
    version="1.0.0"
)

# Add CORS middleware for frontend
if CORS_AVAILABLE:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            # Development
            "http://localhost:3000", 
            "http://localhost:3001", 
            "http://localhost:3002", 
            "http://127.0.0.1:3000", 
            "http://127.0.0.1:3001", 
            "http://127.0.0.1:3002",
            # Production - Add your Render domains here after deployment
            # Example: "https://your-frontend-service.onrender.com"
            # Allow all origins in development (remove in production)
            "*"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.warning("CORS middleware not available. Cross-origin requests may be blocked.")

# Initialize components
dynamic_integration = get_dynamic_integration()
admin_auth = AdminAuth()

# Pydantic models
class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class AdminUpdateRequest(BaseModel):
    update_type: str
    admin_key: str

class ChatMessage(BaseModel):
    type: str
    content: str
    timestamp: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "NovaTech AI Backend Server",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "test": "/test",
            "api_docs": "/docs",
            "news": "/api/dynamic/news",
            "market": "/api/dynamic/market",
            "trends": "/api/dynamic/trends",
            "social": "/api/dynamic/social"
        }
    }

# Test endpoint for frontend connection
@app.get("/test")
async def test_endpoint():
    return {
        "status": "success",
        "message": "Backend connection test successful",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "backend": "online",
            "dynamic_system": "active",
            "ai_service": "active" if simple_gemini_client.is_initialized else "inactive"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "backend": "online",
            "database": "connected",
            "ai_service": "active" if simple_gemini_client.is_initialized else "inactive"
        }
    }

# AI endpoints
@app.post("/api/ai/ai-response")
async def ai_response(request: MessageRequest):
    try:
        response = simple_gemini_client.generate_response(request.message)
        return {
            "status": "success",
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"AI response error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/company-info")
async def company_info(request: MessageRequest):
    try:
        response = simple_gemini_client.generate_response(request.message)
        return {
            "status": "success",
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Company info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# LangChain Enhanced AI Endpoints
@app.post("/api/langchain/chat")
async def langchain_chat(request: MessageRequest):
    """Enhanced chat using LangChain with conversation memory"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id if request.session_id else f"session_{datetime.now().timestamp()}"
        
        # Use LangChain Gemini with conversation memory for context-aware responses
        response = langchain_gemini_client.chat_with_memory(request.message, session_id)
        
        return {
            "status": "success",
            "response": response,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/langchain/response")
async def langchain_response(request: MessageRequest):
    """Get AI response using LangChain knowledge retrieval"""
    try:
        # Generate a default session ID if none provided
        session_id = getattr(request, 'session_id', None) or f"session_{datetime.now().timestamp()}"
        response = langchain_gemini_client.generate_response(request.message, session_id)
        
        return {
            "status": "success",
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"LangChain response error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/langchain/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation details and statistics"""
    try:
        conversation_stats = langgraph_conversation_manager.get_conversation_stats(session_id)
        
        if not conversation_stats:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "status": "success",
            "conversation": conversation_stats,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/langchain/conversation/{session_id}/context")
async def get_conversation_context(session_id: str):
    """Get conversation context for a specific session"""
    try:
        conversation = langgraph_conversation_manager.get_conversation(session_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get recent conversation context
        recent_context = conversation.get_recent_context(max_messages=10)
        
        return {
            "status": "success",
            "session_id": session_id,
            "conversation_context": recent_context,
            "current_state": conversation.current_state.value if hasattr(conversation.current_state, 'value') else str(conversation.current_state),
            "user_intent": conversation.user_intent,
            "message_count": len(conversation.conversation_history),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation context error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/langchain/conversations")
async def get_all_conversations():
    """Get all active conversations"""
    try:
        conversations = langgraph_conversation_manager.get_all_conversations_stats()
        
        return {
            "status": "success",
            "conversations": conversations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Get conversations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/langchain/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear a specific conversation"""
    try:
        success = langgraph_conversation_manager.clear_conversation(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "status": "success",
            "message": f"Conversation {session_id} cleared",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/langchain/knowledge/update")
async def update_knowledge(request: dict):
    """Update knowledge base for a specific category"""
    try:
        category = request.get("category")
        data = request.get("data")
        
        if not category or not data:
            raise HTTPException(status_code=400, detail="Category and data are required")
        
        langchain_knowledge_manager.update_knowledge(category, data)
        
        return {
            "status": "success",
            "message": f"Knowledge updated for category: {category}",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update knowledge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/langchain/knowledge/stats")
async def get_knowledge_stats():
    """Get knowledge manager statistics"""
    try:
        stats = langchain_knowledge_manager.get_stats()
        
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Get knowledge stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/langchain/knowledge/reload")
async def reload_knowledge():
    """Reload and rechunk all knowledge"""
    try:
        langchain_knowledge_manager.load_and_chunk_knowledge()
        
        return {
            "status": "success",
            "message": "Knowledge base reloaded and rechunked",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Reload knowledge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/langchain/stats")
async def get_langchain_stats():
    """Get comprehensive LangChain system statistics"""
    try:
        stats = langchain_gemini_client.get_stats()
        
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Get LangChain stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/langchain/reset")
async def reset_langchain_system():
    """Reset all LangChain systems"""
    try:
        langchain_gemini_client.reset_stats()
        
        return {
            "status": "success",
            "message": "LangChain system reset successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Reset LangChain system error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Dynamic knowledge endpoints
@app.get("/api/dynamic/news")
async def get_news():
    try:
        news_data = dynamic_integration.get_news(5)
        return news_data
    except Exception as e:
        logger.error(f"News API error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "articles": []
        }

@app.get("/api/dynamic/market")
async def get_market_data():
    try:
        market_data = dynamic_integration.get_market_data()
        return market_data
    except Exception as e:
        logger.error(f"Market API error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "stock_quote": {}
        }

@app.get("/api/dynamic/trends")
async def get_industry_trends():
    try:
        trends_data = dynamic_integration.get_industry_trends(5)
        return trends_data
    except Exception as e:
        logger.error(f"Trends API error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "trends": []
        }

@app.get("/api/dynamic/social")
async def get_social_sentiment():
    try:
        reddit_data = dynamic_integration.get_reddit_sentiment()
        return reddit_data
    except Exception as e:
        logger.error(f"Social API error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": {}
        }

# Admin endpoints
@app.post("/api/admin/update")
async def admin_update(request: AdminUpdateRequest):
    try:
        # Validate admin key
        if not admin_auth.verify_admin_key(request.admin_key):
            raise HTTPException(status_code=401, detail="Invalid admin key")
        
        # Perform update
        update_result = dynamic_integration.force_update(request.update_type)
        
        return {
            "status": "success",
            "message": f"{request.update_type} update completed",
            "results": update_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Admin update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/status")
async def admin_status():
    try:
        # Get system status
        system_status = {
            "backend": "online",
            "database": "connected",
            "ai_service": "active" if simple_gemini_client.is_initialized else "inactive",
            "dynamic_system": "active",
            "last_update": dynamic_integration.knowledge_manager.last_update.isoformat() if dynamic_integration.knowledge_manager.last_update else "unknown",
            "timestamp": datetime.now().isoformat()
        }
        
        return system_status
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {
            "backend": "online",
            "database": "error",
            "ai_service": "error",
            "dynamic_system": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# WebSocket endpoint for real-time chat
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = ChatMessage.parse_raw(data)
            
            # Process message and generate response
            try:
                if message_data.type == "message":
                    # Get AI response
                    response = simple_gemini_client.generate_response(message_data.content)
                    
                    # Send response back
                    await manager.send_personal_message(
                        ChatMessage(
                            type="message",
                            content=response,
                            timestamp=datetime.now().isoformat()
                        ).json(),
                        websocket
                    )
            except Exception as e:
                logger.error(f"WebSocket message processing error: {e}")
                await manager.send_personal_message(
                    ChatMessage(
                        type="error",
                        content="Sorry, I encountered an error processing your message.",
                        timestamp=datetime.now().isoformat()
                    ).json(),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Chat endpoints
@app.post("/api/chat/messages")
async def send_message(request: MessageRequest):
    try:
        # Process message and generate response
        response = simple_gemini_client.generate_response(request.message)
        
        return {
            "status": "success",
            "message": {
                "id": datetime.now().timestamp(),
                "type": "bot",
                "content": response,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Chat message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/channels")
async def get_channels():
    return {
        "status": "success",
        "channels": [
            {"id": 1, "name": "General", "description": "General company discussions"},
            {"id": 2, "name": "Engineering", "description": "Technical discussions"},
            {"id": 3, "name": "Marketing", "description": "Marketing and sales"},
            {"id": 4, "name": "Sales", "description": "Sales team communications"},
            {"id": 5, "name": "HR", "description": "Human resources"}
        ]
    }

if __name__ == "__main__":
    logger.info("Starting NovaTech AI Backend Server...")
    # Use environment variable for port, default to 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting NovaTech AI Backend Server on {host}:{port}")
    uvicorn.run(
        "backend_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    ) 