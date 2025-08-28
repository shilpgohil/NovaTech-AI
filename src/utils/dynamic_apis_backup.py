"""
Dynamic Knowledge API Integrations
Handles all external API calls for real-time data updates
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from src.config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """News article data structure"""
    title: str
    description: str
    url: str
    published_at: str
    source: str
    content: str = ""

@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    timestamp: str = ""

@dataclass
class IndustryTrend:
    """Industry trend data structure"""
    topic: str
    sentiment: str
    mentions: int
    source: str
    timestamp: str = ""

class NewsAPI:
    """NewsAPI.org integration for company news"""
    
    def __init__(self):
        self.api_key = config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        self.rate_limit = config.NEWS_API_RATE_LIMIT
        self.requests_made = 0
        self.last_reset = datetime.now()
    
    def get_company_news(self, company_name: str = "NovaTech", days: int = 7) -> List[NewsArticle]:
        """Get company-related news articles"""
        try:
            if self._check_rate_limit():
                return []
            
            # Search for company mentions
            query = f'"{company_name}" OR "NovaTech" OR "SaaS" OR "CRM" OR "HR software"'
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.api_key,
                'pageSize': 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('articles', []):
                articles.append(NewsArticle(
                    title=article.get('title', ''),
                    description=article.get('description', ''),
                    url=article.get('url', ''),
                    published_at=article.get('publishedAt', ''),
                    source=article.get('source', {}).get('name', ''),
                    content=article.get('content', '')
                ))
            
            self.requests_made += 1
            logger.info(f"NewsAPI: Retrieved {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        if (now - self.last_reset).days >= 1:
            self.requests_made = 0
            self.last_reset = now
        
        return self.requests_made >= self.rate_limit

class GNewsAPI:
    """GNews API integration for additional news sources"""
    
    def __init__(self):
        self.api_key = config.GNEWS_API_KEY
        self.base_url = "https://gnews.io/api/v4"
        self.rate_limit = config.GNEWS_RATE_LIMIT
        self.requests_made = 0
        self.last_reset = datetime.now()
    
    def get_tech_news(self, keywords: List[str] = None) -> List[NewsArticle]:
        """Get technology and industry news"""
        try:
            if self._check_rate_limit():
                return []
            
            if keywords is None:
                keywords = ["artificial intelligence", "SaaS", "CRM", "HR software", "business technology"]
            
            query = " OR ".join(keywords)
            url = f"{self.base_url}/search"
            params = {
                'q': query,
                'lang': 'en',
                'country': 'us',
                'max': 10,
                'apikey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('articles', []):
                articles.append(NewsArticle(
                    title=article.get('title', ''),
                    description=article.get('description', ''),
                    url=article.get('url', ''),
                    published_at=article.get('publishedAt', ''),
                    source=article.get('source', {}).get('name', ''),
                    content=article.get('content', '')
                ))
            
            self.requests_made += 1
            logger.info(f"GNews: Retrieved {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"GNews error: {e}")
            return []
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        if (now - self.last_reset).days >= 1:
            self.requests_made = 0
            self.last_reset = now
        
        return self.requests_made >= self.rate_limit

class AlphaVantageAPI:
    """Alpha Vantage API for financial market data"""
    
    def __init__(self):
        self.api_key = config.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit = config.ALPHA_VANTAGE_RATE_LIMIT
        self.requests_made = 0
        self.last_reset = datetime.now()
    
    def get_stock_quote(self, symbol: str = "NVTA") -> Optional[MarketData]:
        """Get real-time stock quote"""
        try:
            if self._check_rate_limit():
                return None
            
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            quote = data.get('Global Quote', {})
            
            if quote:
                market_data = MarketData(
                    symbol=symbol,
                    price=float(quote.get('05. price', 0)),
                    change=float(quote.get('09. change', 0)),
                    change_percent=float(quote.get('10. change percent', '0%').replace('%', '')),
                    volume=int(quote.get('06. volume', 0)),
                    timestamp=datetime.now().isoformat()
                )
                
                self.requests_made += 1
                logger.info(f"AlphaVantage: Retrieved stock data for {symbol}")
                return market_data
            
            return None
            
        except Exception as e:
            logger.error(f"AlphaVantage error: {e}")
            return None
    
    def get_market_sentiment(self, keywords: List[str] = None) -> List[IndustryTrend]:
        """Get market sentiment analysis"""
        try:
            if self._check_rate_limit():
                return []
            
            if keywords is None:
                keywords = ["SaaS", "CRM", "HR software", "business technology"]
            
            trends = []
            for keyword in keywords[:5]:  # Limit to 5 keywords to stay within rate limits
                params = {
                    'function': 'NEWS_SENTIMENT',
                    'tickers': 'NVTA',
                    'topics': keyword,
                    'apikey': self.api_key
                }
                
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                feed = data.get('feed', [])
                
                for item in feed[:3]:  # Top 3 articles per keyword
                    trends.append(IndustryTrend(
                        topic=keyword,
                        sentiment=item.get('overall_sentiment_label', 'neutral'),
                        mentions=item.get('relevance_score', 0),
                        source=item.get('source', ''),
                        timestamp=datetime.now().isoformat()
                    ))
                
                self.requests_made += 1
                time.sleep(0.1)  # Rate limiting
            
            logger.info(f"AlphaVantage: Retrieved {len(trends)} market trends")
            return trends
            
        except Exception as e:
            logger.error(f"AlphaVantage sentiment error: {e}")
            return []
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        if (now - self.last_reset).days >= 1:
            self.requests_made = 0
            self.last_reset = now
        
        return self.requests_made >= self.rate_limit

class FinnhubAPI:
    """Finnhub API for additional financial data"""
    
    def __init__(self):
        self.api_key = config.FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
        self.rate_limit = config.FINNHUB_RATE_LIMIT
        self.requests_made = 0
        self.last_reset = datetime.now()
    
    def get_company_news(self, symbol: str = "NVTA") -> List[NewsArticle]:
        """Get company-specific news from Finnhub"""
        try:
            if self._check_rate_limit():
                return []
            
            url = f"{self.base_url}/company-news"
            params = {
                'symbol': symbol,
                'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'to': datetime.now().strftime('%Y-%m-%d'),
                'token': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data[:10]:  # Top 10 articles
                articles.append(NewsArticle(
                    title=article.get('headline', ''),
                    description=article.get('summary', ''),
                    url=article.get('url', ''),
                    published_at=datetime.fromtimestamp(article.get('datetime', 0)).isoformat(),
                    source=article.get('source', ''),
                    content=article.get('summary', '')
                ))
            
            self.requests_made += 1
            logger.info(f"Finnhub: Retrieved {len(articles)} company news articles")
            return articles
            
        except Exception as e:
            logger.error(f"Finnhub error: {e}")
            return []
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        if (now - self.last_reset).days >= 1:
            self.requests_made = 0
            self.last_reset = now
        
        return self.requests_made >= self.rate_limit

class RedditAPI:
    """Reddit API for industry trends and discussions"""
    
    def __init__(self):
        self.secret_key = config.REDDIT_SECRET_KEY
        self.base_url = "https://www.reddit.com"
        self.user_agent = "NovaTechBot/1.0"
    
    def get_industry_discussions(self, subreddits: List[str] = None) -> List[IndustryTrend]:
        """Get industry discussions from relevant subreddits"""
        try:
            if subreddits is None:
                subreddits = ["SaaS", "CRM", "startups", "business", "technology"]
            
            trends = []
            headers = {'User-Agent': self.user_agent}
            
            for subreddit in subreddits[:3]:  # Limit to 3 subreddits
                url = f"{self.base_url}/r/{subreddit}/hot.json"
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                for post in posts[:5]:  # Top 5 posts
                    post_data = post.get('data', {})
                    trends.append(IndustryTrend(
                        topic=subreddit,
                        sentiment='positive' if post_data.get('score', 0) > 10 else 'neutral',
                        mentions=post_data.get('score', 0),
                        source=f"r/{subreddit}",
                        timestamp=datetime.now().isoformat()
                    ))
                
                time.sleep(1)  # Be respectful to Reddit
            
            logger.info(f"Reddit: Retrieved {len(trends)} industry trends")
            return trends
            
        except Exception as e:
            logger.error(f"Reddit error: {e}")
            return []

class SECAPI:
    """SEC EDGAR API for company filings and financial data"""
    
    def __init__(self):
        self.api_key = config.SEC_API_KEY
        self.base_url = "https://api.sec.gov"
        self.headers = {
            'User-Agent': 'NovaTech Solutions (contact@novatech.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'api.sec.gov'
        }
    
    def get_company_filings(self, cik: str = "0001234567") -> List[Dict[str, Any]]:
        """Get recent company filings from SEC"""
        try:
            url = f"{self.base_url}/submissions/CIK{cik.zfill(10)}.json"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            filings = data.get('filings', {}).get('recent', {})
            
            recent_filings = []
            for i in range(min(5, len(filings.get('form', []))):
                filing = {
                    'form': filings.get('form', [])[i],
                    'filingDate': filings.get('filingDate', [])[i],
                    'accessionNumber': filings.get('accessionNumber', [])[i],
                    'primaryDocument': filings.get('primaryDocument', [])[i]
                }
                recent_filings.append(filing)
            
            logger.info(f"SEC: Retrieved {len(recent_filings)} company filings")
            return recent_filings
            
        except Exception as e:
            logger.error(f"SEC API error: {e}")
            return []

class DynamicAPIManager:
    """Manages all dynamic API integrations"""
    
    def __init__(self):
        self.news_api = NewsAPI()
        self.gnews_api = GNewsAPI()
        self.alpha_vantage = AlphaVantageAPI()
        self.finnhub = FinnhubAPI()
        self.reddit = RedditAPI()
        self.sec = SECAPI()
        
        self.last_update = None
        self.update_interval = config.DYNAMIC_UPDATE_INTERVAL
    
    def get_all_news(self, company_name: str = "NovaTech") -> List[NewsArticle]:
        """Get news from all available sources"""
        all_news = []
        
        # Company-specific news
        company_news = self.news_api.get_company_news(company_name)
        all_news.extend(company_news)
        
        # Industry news
        industry_news = self.gnews_api.get_tech_news()
        all_news.extend(industry_news)
        
        # Financial news
        financial_news = self.finnhub.get_company_news()
        all_news.extend(financial_news)
        
        # Remove duplicates and sort by date
        unique_news = self._deduplicate_news(all_news)
        return sorted(unique_news, key=lambda x: x.published_at, reverse=True)
    
    def get_market_data(self) -> Dict[str, Any]:
        """Get comprehensive market data"""
        market_data = {
            'stock_quote': None,
            'market_trends': [],
            'industry_sentiment': []
        }
        
        # Stock quote
        stock_quote = self.alpha_vantage.get_stock_quote()
        if stock_quote:
            market_data['stock_quote'] = stock_quote
        
        # Market trends
        market_trends = self.alpha_vantage.get_market_sentiment()
        market_data['market_trends'] = market_trends
        
        # Industry discussions
        industry_trends = self.reddit.get_industry_discussions()
        market_data['industry_sentiment'] = industry_trends
        
        return market_data
    
    def get_industry_intelligence(self) -> Dict[str, Any]:
        """Get industry intelligence and trends"""
        intelligence = {
            'sec_filings': [],
            'market_sentiment': [],
            'trending_topics': []
        }
        
        # SEC filings
        sec_filings = self.sec.get_company_filings()
        intelligence['sec_filings'] = sec_filings
        
        # Market sentiment
        market_sentiment = self.alpha_vantage.get_market_sentiment()
        intelligence['market_sentiment'] = market_sentiment
        
        # Reddit trends
        reddit_trends = self.reddit.get_industry_discussions()
        intelligence['trending_topics'] = reddit_trends
        
        return intelligence
    
    def _deduplicate_news(self, news_list: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate news articles based on title similarity"""
        seen_titles = set()
        unique_news = []
        
        for article in news_list:
            # Simple deduplication based on title
            title_key = article.title.lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(article)
        
        return unique_news
    
    def should_update(self) -> bool:
        """Check if it's time for an update"""
        if self.last_update is None:
            return True
        
        time_since_update = (datetime.now() - self.last_update).total_seconds()
        return time_since_update >= self.update_interval
    
    def force_update(self) -> bool:
        """Force an immediate update"""
        self.last_update = None
        return True
    
    def get_update_status(self) -> Dict[str, Any]:
        """Get current update status"""
        return {
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'next_update_in': self._get_next_update_in(),
            'update_interval': self.update_interval,
            'apis_available': {
                'news_api': bool(config.NEWS_API_KEY),
                'gnews': bool(config.GNEWS_API_KEY),
                'alpha_vantage': bool(config.ALPHA_VANTAGE_API_KEY),
                'finnhub': bool(config.FINNHUB_API_KEY),
                'reddit': bool(config.REDDIT_SECRET_KEY),
                'sec': bool(config.SEC_API_KEY)
            }
        }
    
    def _get_next_update_in(self) -> int:
        """Get seconds until next update"""
        if self.last_update is None:
            return 0
        
        time_since_update = (datetime.now() - self.last_update).total_seconds()
        return max(0, self.update_interval - time_since_update) 