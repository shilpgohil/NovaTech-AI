"""
User Learning System
Learns from user interactions to improve responses and build dynamic knowledge
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from src.config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserQuery:
    """User query data structure"""
    query: str
    response: str
    confidence: float
    query_type: str
    timestamp: str
    user_rating: Optional[int] = None
    feedback: Optional[str] = None
    response_time: Optional[float] = None

@dataclass
class LearningPattern:
    """Learning pattern data structure"""
    pattern: str
    frequency: int
    success_rate: float
    common_responses: List[str]
    last_updated: str
    confidence_threshold: float

class UserLearningSystem:
    """Manages user learning and interaction patterns"""
    
    def __init__(self):
        self.learning_file = Path("knowledge_base/user_learning.json")
        self.queries_file = Path("knowledge_base/user_queries.json")
        self.patterns_file = Path("knowledge_base/learning_patterns.json")
        
        # Initialize data structures
        self.user_queries: List[UserQuery] = []
        self.learning_patterns: List[LearningPattern] = []
        self.faq_entries: Dict[str, Any] = {}
        
        # Load existing data
        self._load_data()
        
        # Learning settings
        self.max_queries_stored = config.MAX_USER_QUERIES_STORED
        self.learning_confidence_threshold = config.LEARNING_CONFIDENCE_THRESHOLD
        self.pattern_min_frequency = 3
        self.success_rating_threshold = 4  # Out of 5
    
    def _load_data(self):
        """Load existing learning data from files"""
        try:
            # Load user queries
            if self.queries_file.exists():
                with open(self.queries_file, 'r', encoding='utf-8') as f:
                    queries_data = json.load(f)
                    self.user_queries = [UserQuery(**q) for q in queries_data]
                    logger.info(f"Loaded {len(self.user_queries)} user queries")
            
            # Load learning patterns
            if self.patterns_file.exists():
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
                    self.learning_patterns = [LearningPattern(**p) for p in patterns_data]
                    logger.info(f"Loaded {len(self.learning_patterns)} learning patterns")
            
            # Load FAQ entries
            if self.learning_file.exists():
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    self.faq_entries = json.load(f)
                    logger.info(f"Loaded {len(self.faq_entries)} FAQ entries")
            
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")
            self._initialize_default_data()
    
    def _initialize_default_data(self):
        """Initialize default learning data structure"""
        self.faq_entries = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "faq_entries": [],
            "learning_stats": {
                "total_queries": 0,
                "successful_responses": 0,
                "patterns_identified": 0,
                "faq_entries_generated": 0
            }
        }
    
    def record_query(self, query: str, response: str, confidence: float, 
                    query_type: str, response_time: float = None) -> str:
        """Record a user query and response for learning"""
        try:
            # Create user query record
            user_query = UserQuery(
                query=query,
                response=response,
                confidence=confidence,
                query_type=query_type,
                timestamp=datetime.now().isoformat(),
                response_time=response_time
            )
            
            # Add to queries list
            self.user_queries.append(user_query)
            
            # Maintain max queries limit
            if len(self.user_queries) > self.max_queries_stored:
                self.user_queries = self.user_queries[-self.max_queries_stored:]
            
            # Analyze for learning patterns
            self._analyze_query_pattern(user_query)
            
            # Save data
            self._save_data()
            
            logger.info(f"Recorded user query: {query[:50]}...")
            return "Query recorded for learning"
            
        except Exception as e:
            logger.error(f"Error recording query: {e}")
            return "Error recording query"
    
    def record_feedback(self, query: str, rating: int, feedback: str = None) -> str:
        """Record user feedback for a query"""
        try:
            # Find the most recent matching query
            for user_query in reversed(self.user_queries):
                if user_query.query.lower().strip() == query.lower().strip():
                    user_query.user_rating = rating
                    user_query.feedback = feedback
                    
                    # Update learning patterns
                    self._update_pattern_success_rate(user_query)
                    
                    logger.info(f"Recorded feedback: {rating}/5 for query: {query[:50]}...")
                    return "Feedback recorded successfully"
            
            return "Query not found for feedback"
            
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            return "Error recording feedback"
    
    def _analyze_query_pattern(self, user_query: UserQuery):
        """Analyze query for learning patterns"""
        try:
            # Extract key words from query
            key_words = self._extract_key_words(user_query.query)
            
            # Find or create pattern
            pattern = self._find_or_create_pattern(key_words)
            
            # Update pattern with this query
            pattern.frequency += 1
            pattern.common_responses.append(user_query.response)
            
            # Keep only top 5 responses
            if len(pattern.common_responses) > 5:
                pattern.common_responses = pattern.common_responses[-5:]
            
            pattern.last_updated = datetime.now().isoformat()
            
            # Update confidence threshold based on success
            if user_query.user_rating and user_query.user_rating >= self.success_rating_threshold:
                pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1) + 1) / pattern.frequency
            else:
                pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1)) / pattern.frequency
            
            logger.info(f"Updated pattern: {pattern.pattern} (freq: {pattern.frequency})")
            
        except Exception as e:
            logger.error(f"Error analyzing query pattern: {e}")
    
    def _extract_key_words(self, query: str) -> str:
        """Extract key words from query for pattern matching"""
        # Simple key word extraction (can be enhanced with NLP)
        words = query.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'what', 'when', 'where', 'why', 'how', 'who', 'which', 'that', 'this', 'these', 'those'}
        
        key_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return sorted key words as pattern
        return " ".join(sorted(key_words))
    
    def _find_or_create_pattern(self, key_words: str) -> LearningPattern:
        """Find existing pattern or create new one"""
        for pattern in self.learning_patterns:
            if pattern.pattern == key_words:
                return pattern
        
        # Create new pattern
        new_pattern = LearningPattern(
            pattern=key_words,
            frequency=0,
            success_rate=0.0,
            common_responses=[],
            last_updated=datetime.now().isoformat(),
            confidence_threshold=self.learning_confidence_threshold
        )
        
        self.learning_patterns.append(new_pattern)
        return new_pattern
    
    def _update_pattern_success_rate(self, user_query: UserQuery):
        """Update pattern success rate based on user feedback"""
        if user_query.user_rating is None:
            return
        
        # Find matching pattern
        key_words = self._extract_key_words(user_query.query)
        for pattern in self.learning_patterns:
            if pattern.pattern == key_words:
                # Update success rate
                if user_query.user_rating >= self.success_rating_threshold:
                    pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1) + 1) / pattern.frequency
                else:
                    pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1)) / pattern.frequency
                
                # Adjust confidence threshold
                if pattern.success_rate > 0.8:
                    pattern.confidence_threshold = min(0.9, pattern.confidence_threshold + 0.05)
                elif pattern.success_rate < 0.5:
                    pattern.confidence_threshold = max(0.3, pattern.confidence_threshold - 0.05)
                
                break
    
    def generate_faq_entries(self) -> List[Dict[str, Any]]:
        """Generate FAQ entries from successful patterns"""
        try:
            faq_entries = []
            
            for pattern in self.learning_patterns:
                if (pattern.frequency >= self.pattern_min_frequency and 
                    pattern.success_rate >= 0.7):
                    
                    # Find best response for this pattern
                    best_response = self._find_best_response(pattern)
                    
                    if best_response:
                        faq_entry = {
                            "question": pattern.pattern,
                            "answer": best_response,
                            "confidence": pattern.success_rate,
                            "frequency": pattern.frequency,
                            "last_updated": pattern.last_updated,
                            "source": "user_learning"
                        }
                        faq_entries.append(faq_entry)
            
            # Update FAQ entries
            self.faq_entries["faq_entries"] = faq_entries
            self.faq_entries["last_updated"] = datetime.now().isoformat()
            self.faq_entries["learning_stats"]["faq_entries_generated"] = len(faq_entries)
            
            logger.info(f"Generated {len(faq_entries)} FAQ entries from learning")
            return faq_entries
            
        except Exception as e:
            logger.error(f"Error generating FAQ entries: {e}")
            return []
    
    def _find_best_response(self, pattern: LearningPattern) -> Optional[str]:
        """Find the best response for a pattern"""
        if not pattern.common_responses:
            return None
        
        # For now, return the most recent response
        # This could be enhanced with sentiment analysis or other metrics
        return pattern.common_responses[-1]
    
    def get_learning_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """Get learning-based recommendations for a query"""
        try:
            recommendations = []
            key_words = self._extract_key_words(query)
            
            # Find similar patterns
            for pattern in self.learning_patterns:
                if (pattern.frequency >= self.pattern_min_frequency and 
                    pattern.success_rate >= 0.6):
                    
                    # Calculate similarity (simple word overlap for now)
                    similarity = self._calculate_similarity(key_words, pattern.pattern)
                    
                    if similarity > 0.3:  # 30% similarity threshold
                        recommendation = {
                            "pattern": pattern.pattern,
                            "similarity": similarity,
                            "success_rate": pattern.success_rate,
                            "frequency": pattern.frequency,
                            "suggested_response": pattern.common_responses[-1] if pattern.common_responses else None
                        }
                        recommendations.append(recommendation)
            
            # Sort by similarity and success rate
            recommendations.sort(key=lambda x: (x["similarity"], x["success_rate"]), reverse=True)
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error getting learning recommendations: {e}")
            return []
    
    def _calculate_similarity(self, query_words: str, pattern_words: str) -> float:
        """Calculate similarity between query and pattern"""
        query_set = set(query_words.split())
        pattern_set = set(pattern_words.split())
        
        if not query_set or not pattern_set:
            return 0.0
        
        intersection = query_set.intersection(pattern_set)
        union = query_set.union(pattern_set)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning system statistics"""
        try:
            total_queries = len(self.user_queries)
            successful_responses = sum(1 for q in self.user_queries if q.user_rating and q.user_rating >= self.success_rating_threshold)
            patterns_identified = len(self.patterns)
            
            stats = {
                "total_queries": total_queries,
                "successful_responses": successful_responses,
                "success_rate": (successful_responses / total_queries * 100) if total_queries > 0 else 0,
                "patterns_identified": patterns_identified,
                "faq_entries_generated": len(self.faq_entries.get("faq_entries", [])),
                "learning_patterns": [
                    {
                        "pattern": p.pattern,
                        "frequency": p.frequency,
                        "success_rate": p.success_rate,
                        "confidence_threshold": p.confidence_threshold
                    }
                    for p in self.learning_patterns[:10]  # Top 10 patterns
                ],
                "recent_queries": [
                    {
                        "query": q.query[:50] + "..." if len(q.query) > 50 else q.query,
                        "rating": q.user_rating,
                        "timestamp": q.timestamp
                    }
                    for q in self.user_queries[-10:]  # Last 10 queries
                ]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting learning stats: {e}")
            return {}
    
    def _save_data(self):
        """Save learning data to files"""
        try:
            # Save user queries
            queries_data = [asdict(q) for q in self.user_queries]
            with open(self.queries_file, 'w', encoding='utf-8') as f:
                json.dump(queries_data, f, indent=2, ensure_ascii=False)
            
            # Save learning patterns
            patterns_data = [asdict(p) for p in self.learning_patterns]
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, indent=2, ensure_ascii=False)
            
            # Save FAQ entries
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.faq_entries, f, indent=2, ensure_ascii=False)
            
            logger.info("Learning data saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
    
    def export_learning_data(self) -> Dict[str, Any]:
        """Export learning data for analysis"""
        return {
            "user_queries": [asdict(q) for q in self.user_queries],
            "learning_patterns": [asdict(p) for p in self.learning_patterns],
            "faq_entries": self.faq_entries,
            "stats": self.get_learning_stats()
        }
    
    def reset_learning_data(self) -> str:
        """Reset all learning data (for testing/debugging)"""
        try:
            self.user_queries = []
            self.learning_patterns = []
            self._initialize_default_data()
            self._save_data()
            
            logger.info("Learning data reset successfully")
            return "Learning data reset successfully"
            
        except Exception as e:
            logger.error(f"Error resetting learning data: {e}")
            return f"Error resetting learning data: {e}" 