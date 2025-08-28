"""
Knowledge Loader
Loading and managing knowledge base data
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from ..config import KNOWLEDGE_BASE_FILES, config

# Set up logging
logger = logging.getLogger(__name__)


class KnowledgeLoader:
    """Knowledge base data manager"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._last_modified: Dict[str, float] = {}
        
    def load_all_knowledge(self) -> Dict[str, Any]:
        """Load all knowledge base files into memory"""
        knowledge = {}
        
        for category, file_path in KNOWLEDGE_BASE_FILES.items():
            try:
                data = self.load_knowledge_file(category)
                if data:
                    knowledge[category] = data
                    logger.info(f"SUCCESS: Loaded {category} knowledge")
                else:
                    logger.warning(f"WARNING: Empty or invalid data in {category}")
            except Exception as e:
                logger.error(f"ERROR: Failed to load {category}: {str(e)}")
                knowledge[category] = {}
        
        return knowledge
    
    def load_knowledge_file(self, category: str) -> Optional[Dict[str, Any]]:
        """Load a specific knowledge base file with caching"""
        if category not in KNOWLEDGE_BASE_FILES:
            logger.error(f"Unknown knowledge category: {category}")
            return None
        
        file_path = KNOWLEDGE_BASE_FILES[category]
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"Knowledge file not found: {file_path}")
            return None
        
        # Check if cached version is still valid
        file_modified = os.path.getmtime(file_path)
        if (category in self._cache and 
            category in self._last_modified and 
            self._last_modified[category] >= file_modified):
            return self._cache[category]
        
        # Load fresh data
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cache the data
            self._cache[category] = data
            self._last_modified[category] = file_modified
            
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return None
    
    def get_company_info(self) -> Dict[str, Any]:
        """Get company information"""
        data = self.load_knowledge_file("company_info") or {}
        # Ensure we have the expected structure
        if not data:
            return {
                "company_name": "NovaTech Solutions Pvt. Ltd.",
                "industry": "SaaS",
                "headquarters": "Bengaluru, India",
                "mission": "To empower businesses through intelligent software",
                "contact": {},
                "core_values": ["Innovation", "Customer First", "Integrity"]
            }
        return data
    
    def get_leadership(self) -> Dict[str, Any]:
        """Get leadership information"""
        return self.load_knowledge_file("leadership") or {}
    
    def get_products(self) -> Dict[str, Any]:
        """Get products information"""
        return self.load_knowledge_file("products") or {}
    
    def get_partners(self) -> Dict[str, Any]:
        """Get partners information"""
        return self.load_knowledge_file("partners") or {}
    
    def get_faq(self) -> Dict[str, Any]:
        """Get FAQ information"""
        return self.load_knowledge_file("faq") or {}
    
    def get_marketing(self) -> Dict[str, Any]:
        """Get marketing information"""
        return self.load_knowledge_file("marketing") or {}
    
    def search_in_knowledge(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for information across knowledge base"""
        results = []
        query_lower = query.lower()
        
        # Split query into words for more flexible searching
        query_words = [word.strip() for word in query_lower.split() if len(word.strip()) > 2]
        
        # Determine which categories to search
        categories_to_search = [category] if category else KNOWLEDGE_BASE_FILES.keys()
        
        for cat in categories_to_search:
            data = self.load_knowledge_file(cat)
            if not data:
                continue
            
            # Search through the data structure
            matches = self._search_recursive(data, query_words, cat)
            results.extend(matches)
        
        return results
    
    def _search_recursive(self, data: Any, query_words: List[str], category: str, path: str = "") -> List[Dict[str, Any]]:
        """Recursively search through data structure"""
        results = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check if any query word matches key or value
                for word in query_words:
                    if (word in key.lower() or 
                        (isinstance(value, str) and word in value.lower())):
                        results.append({
                            "category": category,
                            "path": current_path,
                            "key": key,
                            "value": value,
                            "relevance": self._calculate_relevance(word, key, value)
                        })
                        break  # Found a match, no need to check other words
                
                # Recurse into nested structures
                if isinstance(value, (dict, list)):
                    results.extend(self._search_recursive(value, query_words, category, current_path))
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                results.extend(self._search_recursive(item, query_words, category, current_path))
        
        return results
    
    def _calculate_relevance(self, query: str, key: str, value: Any) -> float:
        """Calculate relevance score for search results"""
        score = 0.0
        
        # Exact matches in key get highest score
        if query == key.lower():
            score += 1.0
        elif query in key.lower():
            score += 0.7
        
        # Check value matches
        if isinstance(value, str):
            if query == value.lower():
                score += 0.8
            elif query in value.lower():
                score += 0.5
        
        return min(score, 1.0)
    
    def get_contact_info(self) -> Dict[str, Any]:
        """Get formatted contact information"""
        company = self.get_company_info()
        contact = company.get("contact", {})
        
        return {
            "company_name": company.get("company_name", "NovaTech Solutions Pvt. Ltd."),
            "email": contact.get("email", "info@novatech.com"),
            "phone": contact.get("phone", "+91 80 1234 5678"),
            "website": contact.get("website", "www.novatech.com"),
            "address": contact.get("address", "Tech Park, Whitefield, Bengaluru"),
            "headquarters": company.get("headquarters", "Bengaluru, India")
        }
    
    def get_products_summary(self) -> Dict[str, Any]:
        """Get summarized products information"""
        products_data = self.get_products()
        
        return {
            "products": products_data.get("products", []),
            "pricing_policies": products_data.get("pricing_policies", {}),
            "technology_stack": products_data.get("technology_stack", {})
        }
    
    def get_leadership_summary(self) -> Dict[str, Any]:
        """Get summarized leadership information"""
        leadership_data = self.get_leadership()
        
        return {
            "leadership": leadership_data.get("leadership", {}),
            "shareholding": leadership_data.get("shareholding", {}),
            "departments": leadership_data.get("departments", {})
        }
    
    def clear_cache(self):
        """Clear the knowledge base cache"""
        self._cache.clear()
        self._last_modified.clear()
        logger.info("Knowledge base cache cleared")
    
    def validate_knowledge_base(self) -> Dict[str, bool]:
        """Validate all knowledge base files"""
        validation = {}
        
        for category, file_path in KNOWLEDGE_BASE_FILES.items():
            try:
                if os.path.exists(file_path):
                    data = self.load_knowledge_file(category)
                    validation[category] = data is not None and len(data) > 0
                else:
                    validation[category] = False
                    logger.warning(f"Missing knowledge file: {file_path}")
            except Exception as e:
                validation[category] = False
                logger.error(f"Validation failed for {category}: {str(e)}")
        
        return validation
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        stats = {
            "total_files": len(KNOWLEDGE_BASE_FILES),
            "loaded_files": 0,
            "cached_files": len(self._cache),
            "file_sizes": {},
            "last_updated": {}
        }
        
        for category, file_path in KNOWLEDGE_BASE_FILES.items():
            if os.path.exists(file_path):
                stats["loaded_files"] += 1
                stats["file_sizes"][category] = os.path.getsize(file_path)
                stats["last_updated"][category] = os.path.getmtime(file_path)
        
        return stats


# Global knowledge loader instance
knowledge_loader = KnowledgeLoader() 