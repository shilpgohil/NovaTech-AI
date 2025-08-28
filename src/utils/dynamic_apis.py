"""
Dynamic Knowledge API Integrations
Real API calls to external services for live data
"""

import requests
import logging
import time
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
    """NewsAPI.org integration"""
    
    def __init__(self):
        self.api_key = config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        self.rate_limit = config.NEWS_API_RATE_LIMIT
        self.last_request = 0
        
    def get_company_news(self, company_name: str = "NovaTech", days: int = 7) -> List[NewsArticle]:
        """Get company news from NewsAPI.org"""
        if not self.api_key:
            logger.warning("NewsAPI.org key not configured")
            return [NewsArticle(
                title="API Key Missing",
                description="NewsAPI.org key not configured. Please add NEWS_API_KEY to your environment variables.",
                url="",
                published_at=datetime.now().isoformat(),
                source="System"
            )]
            
        try:
            # Rate limiting
            self._check_rate_limit()
            
            # More specific search for NovaTech Solutions
            if company_name.lower() == "novatech":
                # Use exact company name and exclude common false positives
                query = '"NovaTech Solutions" OR "NovaTech Solutions Inc" OR "NovaTech CRM" OR "NovaTech HR" OR "NovaTech SaaS" -VinFast -Novatech -Vingroup'
            else:
                query = f'"{company_name}" OR "{company_name} Solutions" OR "{company_name} Inc"'
            
            params = {
                'q': query,
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 20,
                'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            }
            
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            if data.get('status') == 'ok' and data.get('articles'):
                for article in data['articles'][:10]:  # Limit to 10 articles
                    # Filter out articles that are clearly not about NovaTech Solutions
                    title = article.get('title', '').lower()
                    description = article.get('description', '').lower()
                    
                    # Skip articles that are clearly about other companies
                    if any(exclude in title or exclude in description for exclude in ['vinfast', 'vingroup', 'vietnam', 'ev maker']):
                        continue
                    
                    # Only include articles that are likely about NovaTech Solutions
                    if any(keyword in title or keyword in description for keyword in ['novatech', 'saas', 'crm', 'hr', 'helpdesk', 'business software']):
                        articles.append(NewsArticle(
                            title=article.get('title', ''),
                            description=article.get('description', ''),
                            url=article.get('url', ''),
                            published_at=article.get('publishedAt', ''),
                            source=article.get('source', {}).get('name', 'Unknown'),
                            content=article.get('content', '')
                        ))
                    
            logger.info(f"NewsAPI.org: Retrieved {len(articles)} relevant articles")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI.org request failed: {e}")
            return [NewsArticle(
                title="API Rate Limit Exceeded",
                description="NewsAPI.org rate limit exceeded or service unavailable. Please try again later.",
                url="",
                published_at=datetime.now().isoformat(),
                source="System"
            )]
        except Exception as e:
            logger.error(f"NewsAPI.org error: {e}")
            return [NewsArticle(
                title="API Error",
                description=f"NewsAPI.org error: {str(e)}. Please check your configuration.",
                url="",
                published_at=datetime.now().isoformat(),
                source="System"
            )]
    
    def _check_rate_limit(self):
        """Simple rate limiting"""
        current_time = time.time()
        if current_time - self.last_request < (3600 / self.rate_limit):
            time.sleep(0.1)  # Small delay
        self.last_request = current_time

class GNewsAPI:
    """GNews API integration"""
    
    def __init__(self):
        self.api_key = config.GNEWS_API_KEY
        self.base_url = "https://gnews.io/api/v4"
        self.rate_limit = config.GNEWS_RATE_LIMIT
        self.last_request = 0
        
    def get_company_news(self, company_name: str = "NovaTech", days: int = 7) -> List[NewsArticle]:
        """Get company news from GNews"""
        if not self.api_key:
            logger.warning("GNews key not configured")
            return [NewsArticle(
                title="API Key Missing",
                description="GNews API key not configured. Please add GNEWS_API_KEY to your environment variables.",
                url="",
                published_at=datetime.now().isoformat(),
                source="System"
            )]
            
        try:
            # Rate limiting
            self._check_rate_limit()
            
            # More specific search for NovaTech Solutions
            if company_name.lower() == "novatech":
                query = '"NovaTech Solutions" OR "NovaTech CRM" OR "NovaTech HR" OR "NovaTech SaaS"'
            else:
                query = f'"{company_name}"'
            
            params = {
                'q': query,
                'token': self.api_key,
                'lang': 'en',
                'country': 'us',
                'max': 10,
                'sortby': 'publishedAt'
            }
            
            response = requests.get(f"{self.base_url}/search", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            if data.get('articles'):
                for article in data['articles']:
                    # Filter out articles that are clearly not about NovaTech Solutions
                    title = article.get('title', '').lower()
                    description = article.get('description', '').lower()
                    
                    # Skip articles that are clearly about other companies
                    if any(exclude in title or exclude in description for exclude in ['vinfast', 'vingroup', 'vietnam', 'ev maker']):
                        continue
                    
                    # Only include articles that are likely about NovaTech Solutions
                    if any(keyword in title or keyword in description for keyword in ['novatech', 'saas', 'crm', 'hr', 'helpdesk', 'business software']):
                        articles.append(NewsArticle(
                            title=article.get('title', ''),
                            description=article.get('description', ''),
                            url=article.get('url', ''),
                            published_at=article.get('publishedAt', ''),
                            source=article.get('source', {}).get('name', 'Unknown'),
                            content=article.get('content', '')
                        ))
                    
            logger.info(f"GNews: Retrieved {len(articles)} relevant articles")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GNews request failed: {e}")
            return [NewsArticle(
                title="API Rate Limit Exceeded",
                description="GNews API rate limit exceeded or service unavailable. Please try again later.",
                url="",
                published_at=datetime.now().isoformat(),
                source="System"
            )]
        except Exception as e:
            logger.error(f"GNews error: {e}")
            return [NewsArticle(
                title="API Error",
                description=f"GNews API error: {str(e)}. Please check your configuration.",
                url="",
                published_at=datetime.now().isoformat(),
                source="System"
            )]
    
    def _check_rate_limit(self):
        """Simple rate limiting"""
        current_time = time.time()
        if current_time - self.last_request < (3600 / self.rate_limit):
            time.sleep(0.1)
        self.last_request = current_time

class AlphaVantageAPI:
    """Alpha Vantage API integration for stock data"""
    
    def __init__(self):
        self.api_key = config.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit = config.ALPHA_VANTAGE_RATE_LIMIT
        self.last_request = 0
        
    def get_stock_quote(self, symbol: str = "NVTA") -> Optional[MarketData]:
        """Get real-time stock quote"""
        if not self.api_key:
            logger.warning("Alpha Vantage key not configured")
            return MarketData(
                symbol=symbol,
                price=0.0,
                change=0.0,
                change_percent=0.0,
                volume=0,
                timestamp=datetime.now().isoformat()
            )
            
        try:
            # Rate limiting
            self._check_rate_limit()
            
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                return MarketData(
                    symbol=quote.get('01. symbol', symbol),
                    price=float(quote.get('05. price', 0)),
                    change=float(quote.get('09. change', 0)),
                    change_percent=float(quote.get('10. change percent', '0%').replace('%', '')),
                    volume=int(quote.get('06. volume', 0)),
                    timestamp=datetime.now().isoformat()
                )
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Alpha Vantage request failed: {e}")
            return MarketData(
                symbol=symbol,
                price=0.0,
                change=0.0,
                change_percent=0.0,
                volume=0,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Alpha Vantage error: {e}")
            return MarketData(
                symbol=symbol,
                price=0.0,
                change=0.0,
                change_percent=0.0,
                volume=0,
                timestamp=datetime.now().isoformat()
            )
    
    def _check_rate_limit(self):
        """Alpha Vantage has strict rate limits"""
        current_time = time.time()
        if current_time - self.last_request < (3600 / self.rate_limit):
            time.sleep(1)  # Longer delay for Alpha Vantage
        self.last_request = current_time

class FinnhubAPI:
    """Finnhub API integration for market data"""
    
    def __init__(self):
        self.api_key = config.FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
        self.rate_limit = config.FINNHUB_RATE_LIMIT
        self.last_request = 0
        
    def get_stock_quote(self, symbol: str = "NVTA") -> Optional[MarketData]:
        """Get real-time stock quote from Finnhub"""
        if not self.api_key:
            logger.warning("Finnhub key not configured")
            return MarketData(
                symbol=symbol,
                price=0.0,
                change=0.0,
                change_percent=0.0,
                volume=0,
                timestamp=datetime.now().isoformat()
            )
            
        try:
            # Rate limiting
            self._check_rate_limit()
            
            params = {
                'symbol': symbol,
                'token': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/quote", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'c' in data and data['c'] > 0:  # Current price exists
                return MarketData(
                    symbol=symbol,
                    price=data.get('c', 0),
                    change=data.get('d', 0),
                    change_percent=data.get('dp', 0),
                    volume=data.get('v', 0),
                    timestamp=datetime.now().isoformat()
                )
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Finnhub request failed: {e}")
            return MarketData(
                symbol=symbol,
                price=0.0,
                change=0.0,
                change_percent=0.0,
                volume=0,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Finnhub error: {e}")
            return MarketData(
                symbol=symbol,
                price=0.0,
                change=0.0,
                change_percent=0.0,
                volume=0,
                timestamp=datetime.now().isoformat()
)
    
    def get_market_sentiment(self, symbol: str = "NVTA") -> Dict[str, Any]:
        """Get market sentiment data"""
        if not self.api_key:
            return {}
            
        try:
            self._check_rate_limit()
            
            params = {
                'symbol': symbol,
                'token': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/news-sentiment", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'sentiment_score': data.get('sentiment', 0),
                'buzz': data.get('buzz', 0),
                'company_news_score': data.get('companyNewsScore', 0),
                'sector_average_bullish_percent': data.get('sectorAverageBullishPercent', 0)
            }
            
        except Exception as e:
            logger.error(f"Finnhub sentiment error: {e}")
            return {}
    
    def _check_rate_limit(self):
        """Finnhub rate limiting"""
        current_time = time.time()
        if current_time - self.last_request < (60 / self.rate_limit):
            time.sleep(0.1)
        self.last_request = current_time

class RedditAPI:
    """Reddit API integration for social sentiment"""
    
    def __init__(self):
        self.client_id = config.REDDIT_SECRET_KEY  # Using as client ID for simplicity
        self.base_url = "https://www.reddit.com"
        self.rate_limit = 60  # Reddit's rate limit
        self.last_request = 0
        
    def get_company_sentiment(self, company_name: str = "NovaTech") -> Dict[str, Any]:
        """Get Reddit sentiment for company (limited without OAuth)"""
        try:
            self._check_rate_limit()
            
            # Simple search without OAuth (limited)
            params = {
                'q': company_name,
                'restrict_sr': 'on',
                't': 'week',
                'sort': 'hot'
            }
            
            headers = {
                'User-Agent': 'NovaTech-Bot/1.0'
            }
            
            response = requests.get(f"{self.base_url}/search.json", params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and 'children' in data['data']:
                posts = data['data']['children'][:5]  # Top 5 posts
                total_score = sum(post['data'].get('score', 0) for post in posts)
                total_comments = sum(post['data'].get('num_comments', 0) for post in posts)
                
                return {
                    'posts_found': len(posts),
                    'total_score': total_score,
                    'total_comments': total_comments,
                    'average_score': total_score / len(posts) if posts else 0,
                    'sentiment': 'positive' if total_score > 0 else 'neutral' if total_score == 0 else 'negative'
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Reddit API error: {e}")
            return {}
    
    def _check_rate_limit(self):
        """Reddit rate limiting"""
        current_time = time.time()
        if current_time - self.last_request < (60 / self.rate_limit):
            time.sleep(1)
        self.last_request = current_time

class SECAPI:
    """SEC EDGAR API integration for company filings"""
    
    def __init__(self):
        self.api_key = config.SEC_API_KEY
        self.base_url = "https://api.sec.gov"
        self.rate_limit = 10  # SEC API rate limit
        self.last_request = 0
        
    def get_company_filings(self, company_name: str = "NovaTech", cik: str = None) -> List[Dict[str, Any]]:
        """Get recent SEC filings for company"""
        if not self.api_key:
            logger.warning("SEC API key not configured")
            return []
            
        try:
            self._check_rate_limit()
            
            # Search for company CIK if not provided
            if not cik:
                cik = self._search_company_cik(company_name)
                if not cik:
                    return []
            
            # Get recent filings
            headers = {
                'User-Agent': 'NovaTech Solutions (shilp@novatech.com)',
                'Accept-Encoding': 'gzip, deflate',
                'Host': 'api.sec.gov'
            }
            
            response = requests.get(
                f"{self.base_url}/submissions/CIK{cik.zfill(10)}.json",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            filings = []
            
            if 'filings' in data and 'recent' in data['filings']:
                for filing in data['filings']['recent'][:5]:  # Last 5 filings
                    filings.append({
                        'accessionNumber': filing.get('accessionNumber'),
                        'form': filing.get('form'),
                        'filingDate': filing.get('filingDate'),
                        'description': filing.get('primaryDocument')
                    })
            
            logger.info(f"SEC API: Retrieved {len(filings)} filings")
            return filings
            
        except Exception as e:
            logger.error(f"SEC API error: {e}")
            return []
    
    def _search_company_cik(self, company_name: str) -> Optional[str]:
        """Search for company CIK number"""
        try:
            self._check_rate_limit()
            
            headers = {
                'User-Agent': 'NovaTech Solutions (shilp@novatech.com)',
                'Accept-Encoding': 'gzip, deflate',
                'Host': 'api.sec.gov'
            }
            
            # Search in company tickers
            response = requests.get(
                f"{self.base_url}/files/company_tickers.json",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Search for company by name
            for cik, company_info in data.items():
                if company_name.lower() in company_info.get('title', '').lower():
                    return cik
            
            return None
            
        except Exception as e:
            logger.error(f"SEC CIK search error: {e}")
            return None
    
    def _check_rate_limit(self):
        """SEC API rate limiting"""
        current_time = time.time()
        if current_time - self.last_request < (60 / self.rate_limit):
            time.sleep(6)  # SEC requires 6 second delay
        self.last_request = current_time

class DynamicAPIManager:
    """Main API manager orchestrating all external API calls"""
    
    def __init__(self):
        self.news_api = NewsAPI()
        self.gnews_api = GNewsAPI()
        self.alpha_vantage_api = AlphaVantageAPI()
        self.finnhub_api = FinnhubAPI()
        self.reddit_api = RedditAPI()
        self.sec_api = SECAPI()
        
        self.last_update = None
        self.update_interval = config.DYNAMIC_UPDATE_INTERVAL
        
        logger.info("Dynamic API Manager initialized with all APIs")
    
    def get_all_news(self, company_name: str = "NovaTech") -> List[NewsArticle]:
        """Get news from all available sources"""
        all_articles = []
        
        # Get news from NewsAPI.org
        try:
            newsapi_articles = self.news_api.get_company_news(company_name)
            all_articles.extend(newsapi_articles)
        except Exception as e:
            logger.error(f"NewsAPI.org error: {e}")
        
        # Get news from GNews
        try:
            gnews_articles = self.gnews_api.get_company_news(company_name)
            all_articles.extend(gnews_articles)
        except Exception as e:
            logger.error(f"GNews error: {e}")
        
        # Remove duplicates and sort by date
        unique_articles = self._deduplicate_articles(all_articles)
        unique_articles.sort(key=lambda x: x.published_at, reverse=True)
        
        logger.info(f"Retrieved {len(unique_articles)} unique news articles")
        return unique_articles
    
    def get_market_data(self) -> Dict[str, Any]:
        """Get comprehensive market data"""
        market_data = {
            'stock_quote': None,
            'market_trends': [],
            'industry_sentiment': {}
        }
        
        # Try Alpha Vantage first
        try:
            stock_quote = self.alpha_vantage_api.get_stock_quote("NVTA")
            if stock_quote:
                market_data['stock_quote'] = stock_quote
                logger.info(f"Alpha Vantage: Stock quote retrieved for NVTA")
        except Exception as e:
            logger.error(f"Alpha Vantage stock quote error: {e}")
        
        # Fallback to Finnhub if Alpha Vantage fails
        if not market_data['stock_quote']:
            try:
                stock_quote = self.finnhub_api.get_stock_quote("NVTA")
                if stock_quote:
                    market_data['stock_quote'] = stock_quote
                    logger.info(f"Finnhub: Stock quote retrieved for NVTA")
            except Exception as e:
                logger.error(f"Finnhub stock quote error: {e}")
        
        # Get market sentiment from Finnhub
        try:
            sentiment = self.finnhub_api.get_market_sentiment("NVTA")
            if sentiment:
                market_data['industry_sentiment'] = sentiment
        except Exception as e:
            logger.error(f"Finnhub sentiment error: {e}")
        
        return market_data
    
    def get_industry_intelligence(self) -> Dict[str, Any]:
        """Get industry intelligence and trends"""
        intelligence = {
            'sec_filings': [],
            'market_sentiment': {},
            'trending_topics': []
        }
        
        # Get SEC filings
        try:
            filings = self.sec_api.get_company_filings("NovaTech")
            intelligence['sec_filings'] = filings
        except Exception as e:
            logger.error(f"SEC API error: {e}")
        
        # Get Reddit sentiment
        try:
            reddit_sentiment = self.reddit_api.get_company_sentiment("NovaTech")
            intelligence['market_sentiment'] = reddit_sentiment
        except Exception as e:
            logger.error(f"Reddit API error: {e}")
        
        return intelligence
    
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # Simple deduplication based on title
            title_key = article.title.lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
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