"""
Query Processor
Understanding and normalizing user input
"""

import re
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
import logging

from ..config import config
from ..utils.knowledge_loader import knowledge_loader

# Set up logging
logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query type classification"""
    COMPANY_INFO = "company_info"
    PRODUCTS = "products"
    LEADERSHIP = "leadership"
    PARTNERS = "partners"
    CASUAL_CHAT = "casual_chat"
    CONTACT_INFO = "contact_info"
    GENERAL = "general"
    FILE_ANALYSIS = "file_analysis"
    REAL_TIME = "real_time"
    UNKNOWN = "unknown"


class QueryProcessor:
    """Query processing engine"""
    
    def __init__(self):
        self.slang_dictionary = self._build_slang_dictionary()
        self.intent_patterns = self._build_intent_patterns()
        self.entity_patterns = self._build_entity_patterns()
        
    def _build_slang_dictionary(self) -> Dict[str, str]:
        """Build comprehensive slang to formal language dictionary"""
        return {
            # Casual greetings and expressions
            "yo": "hello",
            "hey": "hello", 
            "sup": "what's up",
            "whats up": "what's up",
            "wassup": "what's up",
            "howdy": "hello",
            
            # Company references
            "this company": "NovaTech",
            "the company": "NovaTech",
            "your company": "NovaTech",
            "novatech": "NovaTech",
            "nova tech": "NovaTech",
            "the firm": "NovaTech",
            "the business": "NovaTech",
            
            # Question patterns
            "whos": "who is",
            "whats": "what is",
            "hows": "how is", 
            "wheres": "where is",
            "whens": "when is",
            "why's": "why is",
            "how's": "how is",
            "what's": "what is",
            "where's": "where is",
            "when's": "when is",
            
            # Casual questions
            "can you": "can NovaTech",
            "does nova": "does NovaTech",
            "is nova": "is NovaTech",
            "has nova": "has NovaTech",
            "will nova": "will NovaTech",
            "would nova": "would NovaTech",
            
            # Technology slang
            "code": "program",
            "coding": "programming",
            "n stuff": "and other things",
            "and stuff": "and other things",
            "n things": "and other things",
            "tech stuff": "technology",
            "dev work": "development work",
            "backend stuff": "backend development",
            "frontend stuff": "frontend development",
            
            # Skills and abilities
            "good at": "skilled in",
            "know": "knowledgeable about",
            "knows": "knowledgeable about",
            "familiar with": "experienced with",
            "worked with": "experienced with",
            "used": "experienced with",
            
            # General slang
            "gonna": "going to",
            "wanna": "want to",
            "gotta": "have to",
            "lemme": "let me",
            "gimme": "give me",
            "dunno": "don't know",
            "kinda": "kind of",
            "sorta": "sort of",
            "prolly": "probably",
            "def": "definitely",
            "deffo": "definitely",
            
            # Casual connectors
            "n": "and",
            "&": "and",
            "cuz": "because",
            "cos": "because",
            "cause": "because",
            
            # Internet slang
            "rn": "right now",
            "atm": "at the moment",
            "btw": "by the way",
            "fyi": "for your information",
            "imo": "in my opinion",
            "imho": "in my humble opinion",
            "tbh": "to be honest",
            "ngl": "not gonna lie",
            
            # Abbreviations
            "info": "information",
            "deets": "details",
            "specs": "specifications",
            "exp": "experience",
            "edu": "education",
            "bg": "background",
            "cv": "resume",
            "pf": "portfolio",
            "proj": "project",
            "progs": "programs",
            "apps": "applications",
            "langs": "languages",
            "techs": "technologies",
            
            # Company/work slang
            "job": "work experience",
            "gig": "work experience",
            "work": "work experience",
            "company": "workplace",
            "employer": "workplace",
            "boss": "manager",
        }
    
    def _build_intent_patterns(self) -> Dict[QueryType, List[str]]:
        """Build regex patterns for intent recognition"""
        return {
            QueryType.CASUAL_CHAT: [
                r"^hi$",
                r"^hello$",
                r"^hey$",
                r"^sup$",
                r"^whats? up$",
                r"^howdy$",
                r"^good morning$",
                r"^good afternoon$",
                r"^good evening$",
                r"^how are you$",
                r"^who are you$",
                r"^what are you$",
                r"^i am human$",
                r"^i'm human$",
            ],
            QueryType.CONTACT_INFO: [
                r"contact.*info",
                r"how.*reach",
                r"email.*address",
                r"phone.*number", 
                r"website",
                r"office.*location",
                r"get.*touch",
                r"reach.*out",
                r"contact.*nova",
                r"email.*nova",
                r"phone.*nova",
            ],
            QueryType.PRODUCTS: [
                r"products?",
                r"services?",
                r"offerings?",
                r"nova.*crm",
                r"nova.*hr",
                r"nova.*desk",
                r"nova.*analytics",
                r"pricing",
                r"cost",
                r"price",
                r"subscription",
                r"trial",
                r"features?",
                r"what.*products",
                r"what.*services",
                r"what.*offerings",
            ],
            QueryType.LEADERSHIP: [
                r"leadership",
                r"ceo",
                r"cto",
                r"coo",
                r"management",
                r"executives?",
                r"founders?",
                r"directors?",
                r"managers?",
                r"who.*ceo",
                r"who.*cto",
                r"who.*coo",
                r"who.*leads",
                r"who.*runs",
                r"who.*manages",
                r"leadership.*team",
                r"management.*team",
            ],
            QueryType.PARTNERS: [
                r"partners?",
                r"partnerships?",
                r"strategic.*partners?",
                r"ecosystem",
                r"integrations?",
                r"collaborations?",
                r"alliances?",
                r"who.*partners",
                r"what.*partners",
                r"which.*partners",
                r"partner.*companies?",
                r"integrations?.*available",
                r"third.*party",
            ],
            QueryType.COMPANY_INFO: [
                r"company.*info",
                r"about.*nova",
                r"about.*company",
                r"mission",
                r"vision",
                r"values",
                r"culture",
                r"headquarters",
                r"office.*location",
                r"founded",
                r"established",
                r"industry",
                r"sector",
                r"what.*nova",
                r"who.*nova",
                r"tell.*me.*about.*nova",
                r"company.*background",
                r"business.*model",
                r"revenue",
                r"financials",
                r"valuation",
                r"employees",
                r"team.*size",
            ],
            QueryType.GENERAL: [
                r"what.*is.*ai",
                r"what.*is.*machine.*learning",
                r"what.*is.*python",
                r"what.*is.*programming",
                r"what.*is.*software.*development",
                r"what.*is.*data.*science",
                r"what.*is.*computer.*vision",
                r"what.*is.*deep.*learning",
                r"what.*is.*artificial.*intelligence",
                r"explain.*ai",
                r"explain.*machine.*learning",
                r"explain.*python",
                r"explain.*programming",
                r"how.*does.*ai.*work",
                r"how.*does.*machine.*learning.*work",
                r"how.*does.*python.*work",
                r"define.*ai",
                r"define.*machine.*learning",
                r"define.*python",
                r"define.*programming",
            ],
            QueryType.REAL_TIME: [
                r"current.*activity",
                r"recent.*work",
                r"latest.*projects?",
                r"github.*activity",
                r"what.*working.*on",
                r"trending",
                r"news",
                r"weather",
                r"job.*opportunities",
            ],
        }
    
    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for entity extraction"""
        return {
            "programming_languages": [
                "python", "javascript", "java", "c++", "c#", "go", "rust", "ruby", 
                "php", "swift", "kotlin", "typescript", "scala", "r", "matlab", "sql"
            ],
            "frameworks": [
                "react", "angular", "vue", "django", "flask", "spring", "express", 
                "fastapi", "rails", "laravel", "nextjs", "nuxt", "svelte"
            ],
            "technologies": [
                "aws", "docker", "kubernetes", "git", "jenkins", "terraform", 
                "mongodb", "postgresql", "mysql", "redis", "elasticsearch"
            ],
            "companies": [
                "google", "microsoft", "amazon", "apple", "facebook", "meta", 
                "netflix", "uber", "airbnb", "spotify", "github"
            ],
            "skills": [
                "machine learning", "ai", "data science", "web development", 
                "mobile development", "devops", "cloud computing", "cybersecurity"
            ]
        }
    
    def normalize_slang(self, query: str) -> str:
        """Convert slang and casual language to formal queries"""
        normalized = query.lower().strip()
        
        # Apply slang dictionary transformations
        for slang, formal in self.slang_dictionary.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(slang) + r'\b'
            normalized = re.sub(pattern, formal, normalized, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        logger.debug(f"Normalized query: '{query}' -> '{normalized}'")
        return normalized
    
    def classify_query(self, query: str) -> Tuple[QueryType, float]:
        """Classify query intent and return confidence score"""
        normalized_query = self.normalize_slang(query).lower()
        
        # Check patterns for each query type
        best_match = QueryType.UNKNOWN
        highest_score = 0.0
        
        for query_type, patterns in self.intent_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, normalized_query, re.IGNORECASE):
                    matches += 1
                    # Higher score for more specific patterns
                    pattern_score = len(pattern) / 100.0  # Longer patterns = more specific
                    score += pattern_score
            
            # Calculate final score
            if matches > 0:
                final_score = (score / len(patterns)) + (matches / len(patterns))
                if final_score > highest_score:
                    highest_score = final_score
                    best_match = query_type
                    
            # Boost confidence for company information queries
            if best_match in [QueryType.COMPANY_INFO, QueryType.CONTACT_INFO,
                            QueryType.PRODUCTS, QueryType.LEADERSHIP, QueryType.PARTNERS]:
                highest_score = min(highest_score * 1.2, 1.0)
        
        # Special handling for exact matches
        if normalized_query in ["hi", "hello", "hey", "sup", "whats up", "howdy"]:
            best_match = QueryType.CASUAL_CHAT
            highest_score = 1.0
        
        # Special handling for "who are you" type questions
        if any(phrase in normalized_query for phrase in ["who are you", "what are you"]):
            best_match = QueryType.CASUAL_CHAT
            highest_score = 0.8
        
        logger.debug(f"Query classification: {best_match.value} (confidence: {highest_score:.2f})")
        return best_match, highest_score
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract relevant entities from the query"""
        normalized_query = self.normalize_slang(query).lower()
        entities = {}
        
        for entity_type, entity_list in self.entity_patterns.items():
            found_entities = []
            
            for entity in entity_list:
                if entity.lower() in normalized_query:
                    found_entities.append(entity)
            
            if found_entities:
                entities[entity_type] = found_entities
        
        logger.debug(f"Extracted entities: {entities}")
        return entities
    
    def search_knowledge_base(self, query: str, query_type: QueryType) -> Tuple[List[Dict[str, Any]], float]:
        """Search knowledge base and return results with confidence score"""
        normalized_query = self.normalize_slang(query)
        
        # Determine which knowledge categories to search based on query type
        category_mapping = {
            QueryType.CONTACT_INFO: "company_info",
            QueryType.PRODUCTS: "products", 
            QueryType.LEADERSHIP: "leadership",
            QueryType.PARTNERS: "partners",
            QueryType.COMPANY_INFO: "company_info",
            QueryType.CASUAL_CHAT: None,  # Search all categories
        }
        
        category = category_mapping.get(query_type)
        results = knowledge_loader.search_in_knowledge(normalized_query, category)
        
        # Calculate overall confidence based on results
        if not results:
            confidence = 0.0
        else:
            # Average relevance of top results
            top_results = sorted(results, key=lambda x: x.get("relevance", 0), reverse=True)[:3]
            confidence = sum(r.get("relevance", 0) for r in top_results) / len(top_results)
        
        logger.debug(f"Knowledge search found {len(results)} results (confidence: {confidence:.2f})")
        return results, confidence
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Main query processing pipeline"""
        logger.info(f"Processing query: '{query}'")
        
        # Step 1: Normalize slang
        normalized_query = self.normalize_slang(query)
        
        # Step 2: Classify intent
        query_type, classification_confidence = self.classify_query(normalized_query)
        
        # Step 3: Extract entities
        entities = self.extract_entities(normalized_query)
        
        # Step 4: Search knowledge base
        knowledge_results, knowledge_confidence = self.search_knowledge_base(normalized_query, query_type)
        
        # Step 5: Calculate overall confidence for routing
        overall_confidence = (classification_confidence + knowledge_confidence) / 2
        
        # Determine processing route
        should_use_advanced = (
            overall_confidence >= config.ADVANCED_PROCESSING_CONFIDENCE_THRESHOLD and
            query_type.value in config.COMPANY_QUERY_TYPES
        )
        
        result = {
            "original_query": query,
            "normalized_query": normalized_query,
            "query_type": query_type,
            "classification_confidence": classification_confidence,
            "knowledge_confidence": knowledge_confidence,
            "overall_confidence": overall_confidence,
            "entities": entities,
            "knowledge_results": knowledge_results,
            "should_use_advanced": should_use_advanced,
            "processing_route": "advanced" if should_use_advanced else "gemini"
        }
        
        logger.info(f"Query processed - Route: {result['processing_route']}, "
                   f"Confidence: {overall_confidence:.2f}, Type: {query_type.value}")
        
        return result
    
    def get_contextual_keywords(self, query: str) -> List[str]:
        """Extract contextual keywords for enhanced search"""
        normalized = self.normalize_slang(query).lower()
        
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have",
            "has", "had", "do", "does", "did", "will", "would", "could", "should",
            "what", "who", "where", "when", "why", "how"
        }
        
        # Extract meaningful words
        words = re.findall(r'\b\w+\b', normalized)
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def suggest_related_queries(self, query: str, query_type: QueryType) -> List[str]:
        """Suggest related queries based on the current query"""
        suggestions = []
        
        if query_type == QueryType.PRODUCTS:
            suggestions.extend([
                "What products does NovaTech offer?",
                "What is NovaCRM pricing?",
                "What features does NovaHR have?",
                "What integrations are available?"
            ])
        elif query_type == QueryType.LEADERSHIP:
            suggestions.extend([
                "Who is the CEO of NovaTech?",
                "What is the leadership team structure?",
                "Who are the founders?",
                "What departments does NovaTech have?"
            ])
        elif query_type == QueryType.CONTACT_INFO:
            suggestions.extend([
                "How can I contact NovaTech?",
                "What is NovaTech's email address?",
                "Where is NovaTech's headquarters?",
                "What are NovaTech's office locations?"
            ])
        elif query_type == QueryType.COMPANY_INFO:
            suggestions.extend([
                "What is NovaTech's mission?",
                "What are NovaTech's core values?",
                "What is NovaTech's revenue?",
                "How many employees does NovaTech have?"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions


# Global query processor instance
query_processor = QueryProcessor() 