"""
Dynamic Knowledge Manager
Orchestrates hourly updates, manual triggers, and integrates all dynamic knowledge systems
"""

import json
import logging
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from src.config import config
from src.utils.dynamic_apis import DynamicAPIManager
from src.utils.user_learning import UserLearningSystem
from src.utils.linkedin_integrator import linkedin_integrator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicKnowledgeManager:
    """Main manager for dynamic knowledge updates and learning"""
    
    def __init__(self):
        self.api_manager = DynamicAPIManager()
        self.learning_system = UserLearningSystem()
        
        # Knowledge base files
        self.knowledge_base_dir = Path("knowledge_base")
        self.news_file = self.knowledge_base_dir / "news.json"
        self.market_data_file = self.knowledge_base_dir / "market_data.json"
        self.industry_trends_file = self.knowledge_base_dir / "industry_trends.json"
        self.linkedin_file = self.knowledge_base_dir / "linkedin_cache.json"
        
        # Update settings
        self.update_interval = config.DYNAMIC_UPDATE_INTERVAL
        self.last_update = None
        self.update_thread = None
        self.is_running = False
        
        # Initialize knowledge files
        self._initialize_knowledge_files()
        
        # Start background update thread
        self.start_background_updates()
    
    def _initialize_knowledge_files(self):
        """Initialize knowledge base files if they don't exist"""
        try:
            self.knowledge_base_dir.mkdir(exist_ok=True)
            
            # Initialize news file
            if not self.news_file.exists():
                initial_news = {
                    "version": "1.0",
                    "last_updated": datetime.now().isoformat(),
                    "articles": [],
                    "sources": ["NewsAPI", "GNews", "Finnhub"],
                    "total_articles": 0
                }
                with open(self.news_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_news, f, indent=2, ensure_ascii=False)
            
            # Initialize market data file
            if not self.market_data_file.exists():
                initial_market = {
                    "version": "1.0",
                    "last_updated": datetime.now().isoformat(),
                    "stock_quotes": {},
                    "market_trends": [],
                    "industry_sentiment": [],
                    "sources": ["AlphaVantage", "Finnhub", "Reddit"]
                }
                with open(self.market_data_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_market, f, indent=2, ensure_ascii=False)
            
            # Initialize industry trends file
            if not self.industry_trends_file.exists():
                initial_trends = {
                    "version": "1.0",
                    "last_updated": datetime.now().isoformat(),
                    "trends": [],
                    "sec_filings": [],
                    "trending_topics": [],
                    "sources": ["SEC", "AlphaVantage", "Reddit"]
                }
                with open(self.industry_trends_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_trends, f, indent=2, ensure_ascii=False)
            
            logger.info("Knowledge base files initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing knowledge files: {e}")
    
    def start_background_updates(self):
        """Start background thread for automatic updates"""
        if not self.is_running:
            self.is_running = True
            self.update_thread = threading.Thread(target=self._background_update_loop, daemon=True)
            self.update_thread.start()
            logger.info("Background update thread started")
    
    def stop_background_updates(self):
        """Stop background update thread"""
        self.is_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
            logger.info("Background update thread stopped")
    
    def _background_update_loop(self):
        """Background loop for automatic updates"""
        while self.is_running:
            try:
                if self.api_manager.should_update():
                    logger.info("Background update triggered")
                    self._perform_update()
                
                # Sleep for a shorter interval to check more frequently
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in background update loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def force_update(self, update_type: str = "all") -> Dict[str, Any]:
        """Force an immediate knowledge update with specific type"""
        try:
            logger.info(f"Manual update triggered for: {update_type}")
            
            # Perform selective update based on type
            if update_type == "all":
                return self._perform_update()
            elif update_type == "news":
                return self._perform_news_update_only()
            elif update_type == "market":
                return self._perform_market_update_only()
            elif update_type == "industry":
                return self._perform_industry_update_only()
            elif update_type == "learning":
                return self._perform_learning_update_only()
            else:
                return {
                    "status": "error",
                    "message": f"Unknown update type: {update_type}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in force update: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _perform_news_update_only(self) -> Dict[str, Any]:
        """Update only news data"""
        try:
            start_time = time.time()
            
            # Update news only
            logger.info("Updating news data only...")
            news_result = self._update_news()
            
            update_time = time.time() - start_time
            self.last_update = datetime.now()
            self.api_manager.last_update = self.last_update
            
            logger.info(f"News-only update completed in {update_time:.2f} seconds")
            
            return {
                "status": "success",
                "update_type": "news",
                "update_time": update_time,
                "timestamp": self.last_update.isoformat(),
                "results": {
                    "news": news_result
                }
            }
            
        except Exception as e:
            logger.error(f"Error performing news update: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _perform_market_update_only(self) -> Dict[str, Any]:
        """Update only market data"""
        try:
            start_time = time.time()
            
            # Update market data only
            logger.info("Updating market data only...")
            market_result = self._update_market_data()
            
            update_time = time.time() - start_time
            self.last_update = datetime.now()
            self.api_manager.last_update = self.last_update
            
            logger.info(f"Market-only update completed in {update_time:.2f} seconds")
            
            return {
                "status": "success",
                "update_type": "market",
                "update_time": update_time,
                "timestamp": self.last_update.isoformat(),
                "results": {
                    "market_data": market_result
                }
            }
            
        except Exception as e:
            logger.error(f"Error performing market update: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _perform_industry_update_only(self) -> Dict[str, Any]:
        """Update only industry trends"""
        try:
            start_time = time.time()
            
            # Update industry trends only
            logger.info("Updating industry trends only...")
            trends_result = self._update_industry_trends()
            
            update_time = time.time() - start_time
            self.last_update = datetime.now()
            self.api_manager.last_update = self.last_update
            
            logger.info(f"Industry-only update completed in {update_time:.2f} seconds")
            
            return {
                "status": "success",
                "update_type": "industry",
                "update_time": update_time,
                "timestamp": self.last_update.isoformat(),
                "results": {
                    "industry_trends": trends_result
                }
            }
            
        except Exception as e:
            logger.error(f"Error performing industry update: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _perform_learning_update_only(self) -> Dict[str, Any]:
        """Update only learning data"""
        try:
            start_time = time.time()
            
            # Generate FAQ entries from learning only
            logger.info("Updating learning data only...")
            faq_result = self.learning_system.generate_faq_entries()
            
            update_time = time.time() - start_time
            self.last_update = datetime.now()
            
            logger.info(f"Learning-only update completed in {update_time:.2f} seconds")
            
            return {
                "status": "success",
                "update_type": "learning",
                "update_time": update_time,
                "timestamp": self.last_update.isoformat(),
                "results": {
                    "faq_generation": {
                        "entries_generated": len(faq_result),
                        "status": "success"
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error performing learning update: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _perform_update(self) -> Dict[str, Any]:
        """Perform the actual knowledge update"""
        try:
            start_time = time.time()
            update_results = {}
            
            # Update news
            logger.info("Updating news data...")
            news_result = self._update_news()
            update_results["news"] = news_result
            
            # Update market data
            logger.info("Updating market data...")
            market_result = self._update_market_data()
            update_results["market_data"] = market_result
            
            # Update industry trends
            logger.info("Updating industry trends...")
            trends_result = self._update_industry_trends()
            update_results["industry_trends"] = trends_result
            
            # Generate FAQ entries from learning
            logger.info("Generating FAQ entries from learning...")
            faq_result = self.learning_system.generate_faq_entries()
            update_results["faq_generation"] = {
                "entries_generated": len(faq_result),
                "status": "success"
            }
            
            # Update timestamp
            self.last_update = datetime.now()
            self.api_manager.last_update = self.last_update
            
            update_time = time.time() - start_time
            
            logger.info(f"Knowledge update completed in {update_time:.2f} seconds")
            
            return {
                "status": "success",
                "update_time": update_time,
                "timestamp": self.last_update.isoformat(),
                "results": update_results
            }
            
        except Exception as e:
            logger.error(f"Error performing update: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _update_news(self) -> Dict[str, Any]:
        """Update news data from all sources"""
        try:
            # Get news from all APIs
            articles = self.api_manager.get_all_news("NovaTech")
            
            if articles:
                # Convert to JSON-serializable format
                news_data = []
                for article in articles:
                    news_data.append({
                        'title': article.title,
                        'description': article.description,
                        'url': article.url,
                        'published_at': article.published_at,
                        'source': article.source,
                        'content': article.content,
                        'retrieved_at': datetime.now().isoformat()
                    })
                
                # Save to file
                with open(self.news_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'last_updated': datetime.now().isoformat(),
                        'total_articles': len(news_data),
                        'articles': news_data
                    }, f, indent=2, ensure_ascii=False)
                
                logger.info(f"News updated: {len(news_data)} articles")
                return {
                    'status': 'success',
                    'articles_updated': len(news_data),
                    'sources': ['NewsAPI', 'GNews', 'Finnhub']
                }
            else:
                logger.warning("No news articles retrieved")
                return {
                    'status': 'warning',
                    'message': 'API rate limits exceeded or services unavailable. Please check your API keys or try again later.',
                    'articles_updated': 0,
                    'error_type': 'api_limit'
                }
                
        except Exception as e:
            logger.error(f"Error updating news: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'articles_updated': 0
            }
    
    def _update_market_data(self) -> Dict[str, Any]:
        """Update market data from financial APIs"""
        try:
            # Get market data from APIs
            market_data = self.api_manager.get_market_data()
            
            if market_data:
                # Convert to JSON-serializable format
                json_data = {
                    'last_updated': datetime.now().isoformat(),
                    'stock_quote': None,
                    'market_trends': market_data.get('market_trends', []),
                    'industry_sentiment': market_data.get('industry_sentiment', {})
                }
                
                # Handle stock quote
                if market_data.get('stock_quote'):
                    stock = market_data['stock_quote']
                    json_data['stock_quote'] = {
                        'symbol': stock.symbol,
                        'price': stock.price,
                        'change': stock.change,
                        'change_percent': stock.change_percent,
                        'volume': stock.volume,
                        'market_cap': stock.market_cap,
                        'timestamp': stock.timestamp
                    }
                
                # Save to file
                with open(self.market_data_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                
                stock_updated = 1 if market_data.get('stock_quote') else 0
                trends_updated = len(market_data.get('market_trends', []))
                sentiment_updated = 1 if market_data.get('industry_sentiment') else 0
                
                logger.info(f"Market data updated: stock={stock_updated}, trends={trends_updated}, sentiment={sentiment_updated}")
                return {
                    'status': 'success',
                    'stock_quotes_updated': stock_updated,
                    'market_trends_updated': trends_updated,
                    'industry_sentiment_updated': sentiment_updated
                }
            else:
                logger.warning("No market data retrieved")
                return {
                    'status': 'warning',
                    'message': 'No market data found',
                    'stock_quotes_updated': 0,
                    'market_trends_updated': 0,
                    'industry_sentiment_updated': 0
                }
                
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'stock_quotes_updated': 0,
                'market_trends_updated': 0,
                'industry_sentiment_updated': 0
            }
    
    def _update_industry_trends(self) -> Dict[str, Any]:
        """Update industry trends and intelligence"""
        try:
            # Get industry intelligence from APIs
            intelligence = self.api_manager.get_industry_intelligence()
            
            if intelligence:
                # Convert to JSON-serializable format
                json_data = {
                    'last_updated': datetime.now().isoformat(),
                    'sec_filings': intelligence.get('sec_filings', []),
                    'market_sentiment': intelligence.get('market_sentiment', {}),
                    'trending_topics': intelligence.get('trending_topics', [])
                }
                
                # Save to file
                with open(self.industry_trends_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                
                sec_updated = len(intelligence.get('sec_filings', []))
                trends_updated = len(intelligence.get('trending_topics', []))
                sentiment_updated = 1 if intelligence.get('market_sentiment') else 0
                
                logger.info(f"Industry trends updated: SEC={sec_updated}, trends={trends_updated}, sentiment={sentiment_updated}")
                return {
                    'status': 'success',
                    'sec_filings_updated': sec_updated,
                    'trends_updated': trends_updated,
                    'trending_topics_updated': trends_updated
                }
            else:
                logger.warning("No industry intelligence retrieved")
                return {
                    'status': 'warning',
                    'message': 'No industry intelligence found',
                    'sec_filings_updated': 0,
                    'trends_updated': 0,
                    'trending_topics_updated': 0
                }
                
        except Exception as e:
            logger.error(f"Error updating industry trends: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'sec_filings_updated': 0,
                'trends_updated': 0,
                'trending_topics_updated': 0
            }
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary of current knowledge state"""
        try:
            summary = {
                "last_update": self.last_update.isoformat() if self.last_update else None,
                "next_update_in": self._get_next_update_in(),
                "update_interval": self.update_interval,
                "background_updates": self.is_running,
                "knowledge_files": {}
            }
            
            # Get file sizes and last modified times
            for file_path in [self.news_file, self.market_data_file, self.industry_trends_file]:
                if file_path.exists():
                    stat = file_path.stat()
                    summary["knowledge_files"][file_path.name] = {
                        "size_bytes": stat.st_size,
                        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "exists": True
                    }
                else:
                    summary["knowledge_files"][file_path.name] = {
                        "exists": False
                    }
            
            # Get API status
            summary["api_status"] = self.api_manager.get_update_status()
            
            # Get learning stats
            summary["learning_stats"] = self.learning_system.get_learning_stats()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting knowledge summary: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _get_next_update_in(self) -> int:
        """Get seconds until next update"""
        if self.last_update is None:
            return 0
        
        time_since_update = (datetime.now() - self.last_update).total_seconds()
        return max(0, self.update_interval - time_since_update)
    
    def get_news_summary(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get summary of latest news"""
        try:
            if not self.news_file.exists():
                return []
            
            with open(self.news_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            articles = news_data.get('articles', [])
            return articles[:limit]
            
        except Exception as e:
            logger.error(f"Error getting news summary: {e}")
            return []
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get summary of market data"""
        try:
            if not self.market_data_file.exists():
                return {}
            
            with open(self.market_data_file, 'r', encoding='utf-8') as f:
                market_data = json.load(f)
            
            return {
                "stock_quotes": market_data.get('stock_quote', {}),
                "market_trends_count": len(market_data.get('market_trends', [])),
                "industry_sentiment_count": len(market_data.get('industry_sentiment', {})),
                "last_updated": market_data.get('last_updated')
            }
            
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {}
    
    def get_trends_summary(self, limit: int = 5) -> Dict[str, Any]:
        """Get summary of industry trends"""
        try:
            if not self.industry_trends_file.exists():
                return {}
            
            with open(self.industry_trends_file, 'r', encoding='utf-8') as f:
                trends_data = json.load(f)
            
            return {
                "sec_filings": trends_data.get('sec_filings', [])[:limit],
                "trends": trends_data.get('trends', [])[:limit],
                "trending_topics": trends_data.get('trending_topics', [])[:limit],
                "last_updated": trends_data.get('last_updated')
            }
            
        except Exception as e:
            logger.error(f"Error getting trends summary: {e}")
            return {}
    
    def get_industry_intelligence(self) -> Dict[str, Any]:
        """Get industry intelligence and trends data"""
        try:
            intelligence = {
                'sec_filings': [],
                'market_sentiment': {},
                'trending_topics': []
            }
            
            # Get SEC filings
            try:
                filings = self.api_manager.get_industry_intelligence()
                if filings:
                    intelligence['sec_filings'] = filings.get('sec_filings', [])
                    intelligence['market_sentiment'] = filings.get('market_sentiment', {})
                    intelligence['trending_topics'] = filings.get('trending_topics', [])
            except Exception as e:
                logger.error(f"Error getting industry intelligence: {e}")
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Error in get_industry_intelligence: {e}")
            return {
                'sec_filings': [],
                'market_sentiment': {},
                'trending_topics': []
            }
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to prevent file bloat"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean up old news articles
            if self.news_file.exists():
                with open(self.news_file, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
                
                # Filter out old articles
                old_articles = []
                for article in news_data.get('articles', []):
                    try:
                        article_date = datetime.fromisoformat(article.get('published_at', ''))
                        if article_date > cutoff_date:
                            old_articles.append(article)
                    except:
                        # Keep articles with invalid dates
                        old_articles.append(article)
                
                news_data["articles"] = old_articles
                news_data["total_articles"] = len(old_articles)
                
                with open(self.news_file, 'w', encoding='utf-8') as f:
                    json.dump(news_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Cleaned up news data, kept {len(old_articles)} recent articles")
            
            # Similar cleanup for other files could be added here
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def shutdown(self):
        """Clean shutdown of the manager"""
        try:
            self.stop_background_updates()
            self._save_data()
            logger.info("Dynamic knowledge manager shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def _save_data(self):
        """Save any pending data"""
        try:
            self.learning_system._save_data()
        except Exception as e:
            logger.error(f"Error saving data during shutdown: {e}") 