"""
Dynamic Knowledge Integration
Main integration point for all dynamic knowledge systems
"""

import logging
from typing import Dict, Any, Optional
from src.utils.dynamic_knowledge_manager import DynamicKnowledgeManager
from src.utils.scheduler import get_scheduler
from src.utils.user_learning import UserLearningSystem
from src.config import config
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicKnowledgeIntegration:
    """Main integration class for dynamic knowledge systems"""
    
    def __init__(self):
        self.knowledge_manager = DynamicKnowledgeManager()
        self.scheduler = get_scheduler()
        self.learning_system = UserLearningSystem()
        
        # Connect components
        self._connect_components()
        
        # Start systems
        self._start_systems()
        
        logger.info("Dynamic Knowledge Integration initialized successfully")
    
    def _connect_components(self):
        """Connect all dynamic knowledge components"""
        try:
            # Connect scheduler to knowledge manager
            self.scheduler.connect_knowledge_manager(self.knowledge_manager)
            
            # Add scheduler callback for learning system
            self.scheduler.add_update_callback(self._on_scheduled_update)
            
            logger.info("Dynamic knowledge components connected successfully")
            
        except Exception as e:
            logger.error(f"Error connecting components: {e}")
    
    def _start_systems(self):
        """Start all dynamic knowledge systems"""
        try:
            # Start the scheduler
            self.scheduler.start_scheduler()
            
            # Start background updates in knowledge manager
            self.knowledge_manager.start_background_updates()
            
            logger.info("Dynamic knowledge systems started successfully")
            
        except Exception as e:
            logger.error(f"Error starting systems: {e}")
    
    def _on_scheduled_update(self, task_name: str, result: Any):
        """Handle scheduled update callbacks"""
        try:
            logger.info(f"Scheduled task '{task_name}' completed with result: {result}")
            
            # Handle different task types
            if task_name == "hourly_knowledge_update":
                self._handle_knowledge_update(result)
            elif task_name == "daily_cleanup":
                self._handle_cleanup(result)
            elif task_name == "weekly_learning_analysis":
                self._handle_learning_analysis(result)
                
        except Exception as e:
            logger.error(f"Error handling scheduled update: {e}")
    
    def _handle_knowledge_update(self, result: Any):
        """Handle knowledge update results"""
        try:
            if result.get('status') == 'success':
                logger.info("Knowledge update completed successfully")
                # Could trigger additional actions here
            else:
                logger.warning(f"Knowledge update had issues: {result}")
                
        except Exception as e:
            logger.error(f"Error handling knowledge update: {e}")
    
    def _handle_cleanup(self, result: Any):
        """Handle cleanup results"""
        try:
            if result.get('status') == 'success':
                logger.info("Cleanup completed successfully")
            else:
                logger.warning(f"Cleanup had issues: {result}")
                
        except Exception as e:
            logger.error(f"Error handling cleanup: {e}")
    
    def _handle_learning_analysis(self, result: Any):
        """Handle learning analysis results"""
        try:
            if result.get('status') == 'success':
                logger.info("Learning analysis completed successfully")
                # Generate new FAQ entries
                self.learning_system.generate_faq_entries()
            else:
                logger.warning(f"Learning analysis had issues: {result}")
                
        except Exception as e:
            logger.error(f"Error handling learning analysis: {e}")
    
    def force_update(self, update_type: str = "all") -> Dict[str, Any]:
        """Force an immediate knowledge update with specific type"""
        try:
            logger.info(f"Manual update requested for: {update_type}")
            return self.knowledge_manager.force_update(update_type)
        except Exception as e:
            logger.error(f"Error in force update: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_news(self, limit: int = 5) -> Dict[str, Any]:
        """Get latest news summary"""
        try:
            news_articles = self.knowledge_manager.get_news_summary(limit)
            return {
                "status": "success",
                "articles": news_articles,
                "total": len(news_articles),
                "sources": ["NewsAPI", "GNews", "Finnhub"]
            }
            
        except Exception as e:
            logger.error(f"Error getting news: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_market_data(self) -> Dict[str, Any]:
        """Get market data summary"""
        try:
            market_summary = self.knowledge_manager.get_market_summary()
            return {
                "status": "success",
                "data": market_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_industry_trends(self, limit: int = 5) -> Dict[str, Any]:
        """Get industry trends summary"""
        try:
            trends_summary = self.knowledge_manager.get_trends_summary(limit)
            return {
                "status": "success",
                "data": trends_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting industry trends: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def record_user_interaction(self, query: str, response: str, confidence: float, 
                               query_type: str, response_time: float = None) -> str:
        """Record a user interaction for learning"""
        try:
            result = self.learning_system.record_query(
                query, response, confidence, query_type, response_time
            )
            return result
            
        except Exception as e:
            logger.error(f"Error recording user interaction: {e}")
            return f"Error recording interaction: {e}"
    
    def record_feedback(self, query: str, rating: int, feedback: str = None) -> str:
        """Record user feedback for learning"""
        try:
            result = self.learning_system.record_feedback(query, rating, feedback)
            return result
            
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            return f"Error recording feedback: {e}"
    
    def get_learning_recommendations(self, query: str) -> Dict[str, Any]:
        """Get learning-based recommendations for a query"""
        try:
            recommendations = self.learning_system.get_learning_recommendations(query)
            return {
                "status": "success",
                "recommendations": recommendations,
                "count": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error getting learning recommendations: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            status = {
                "dynamic_knowledge": self.knowledge_manager.get_knowledge_summary(),
                "scheduler": self.scheduler.get_task_status(),
                "learning": self.learning_system.get_learning_stats(),
                "apis": self.knowledge_manager.api_manager.get_update_status()
            }
            
            return {
                "status": "success",
                "data": status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_dynamic_response(self, query: str, query_type: str) -> Dict[str, Any]:
        """Get a dynamic response based on current knowledge"""
        try:
            response_data = {}
            
            # Get relevant news if asking about company updates
            if any(word in query.lower() for word in ['news', 'update', 'latest', 'recent']):
                news_data = self.get_news(3)
                if news_data.get('status') == 'success':
                    response_data['news'] = news_data
            
            # Get market data if asking about financials
            if any(word in query.lower() for word in ['stock', 'market', 'price', 'financial']):
                market_data = self.get_market_data()
                if market_data.get('status') == 'success':
                    response_data['market_data'] = market_data
            
            # Get industry trends if asking about industry
            if any(word in query.lower() for word in ['industry', 'trend', 'competitor', 'market']):
                trends_data = self.get_industry_trends(3)
                if trends_data.get('status') == 'success':
                    response_data['industry_trends'] = trends_data
            
            # Get learning recommendations
            learning_recs = self.get_learning_recommendations(query)
            if learning_recs.get('status') == 'success' and learning_recs.get('recommendations'):
                response_data['learning_recommendations'] = learning_recs
            
            return {
                "status": "success",
                "query": query,
                "query_type": query_type,
                "dynamic_data": response_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dynamic response: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_reddit_sentiment(self) -> Dict[str, Any]:
        """Get Reddit sentiment data for NovaTech Solutions"""
        try:
            # Get industry intelligence which includes Reddit data
            intelligence = self.knowledge_manager.get_industry_intelligence()
            
            if intelligence and intelligence.get('market_sentiment'):
                reddit_data = intelligence['market_sentiment']
                return {
                    "status": "success",
                    "data": reddit_data
                }
            else:
                return {
                    "status": "success",
                    "data": {
                        "posts_found": 0,
                        "total_score": 0,
                        "total_comments": 0,
                        "average_score": 0,
                        "sentiment": "neutral"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting Reddit sentiment: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def shutdown(self):
        """Clean shutdown of all systems"""
        try:
            logger.info("Shutting down dynamic knowledge integration...")
            
            # Shutdown knowledge manager
            self.knowledge_manager.shutdown()
            
            # Shutdown scheduler
            self.scheduler.shutdown()
            
            logger.info("Dynamic knowledge integration shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Global integration instance
dynamic_integration = DynamicKnowledgeIntegration()

def get_dynamic_integration() -> DynamicKnowledgeIntegration:
    """Get the global dynamic knowledge integration instance"""
    return dynamic_integration

def initialize_dynamic_knowledge():
    """Initialize the dynamic knowledge system"""
    try:
        integration = get_dynamic_integration()
        logger.info("Dynamic knowledge system initialized successfully")
        return integration
    except Exception as e:
        logger.error(f"Error initializing dynamic knowledge: {e}")
        return None

def shutdown_dynamic_knowledge():
    """Shutdown the dynamic knowledge system"""
    try:
        integration = get_dynamic_integration()
        integration.shutdown()
        logger.info("Dynamic knowledge system shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down dynamic knowledge: {e}") 