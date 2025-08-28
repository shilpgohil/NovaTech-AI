"""
Context Provider
Context retrieval for conversations
"""

import re
from typing import Dict, Any, List, Optional
import logging

from ..utils.knowledge_loader import knowledge_loader

# Set up logging
logger = logging.getLogger(__name__)


class ContextProvider:
    """Context provider for conversations"""
    
    def __init__(self):
        self._cache = {}
        self._query_keywords = {
            "products": ["product", "nova", "crm", "hr", "desk", "analytics", "pricing"],
            "leadership": ["ceo", "cto", "leadership", "management", "founder", "executive"],
            "partners": ["partner", "integration", "ecosystem", "collaboration"],
            "company": ["company", "novatech", "mission", "vision", "values"],
            "marketing": ["marketing", "campaign", "webinar", "case study", "whitepaper"],
            "support": ["support", "help", "faq", "documentation", "training"],
            "financial": ["revenue", "valuation", "funding", "investor", "financial"],
            "contact": ["contact", "phone", "email", "reach", "get in touch", "call", "message"]
        }
    
    def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """Get relevant context for a query"""
        query_lower = query.lower()
        
        # Check cache first
        cache_key = query_lower.strip()
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Determine relevant data categories
        relevant_categories = self._identify_relevant_categories(query_lower)
        
        # Gather context data
        context_data = {}
        for category in relevant_categories:
            data = self._get_category_data(category)
            if data:
                context_data[category] = data
        
        # Format context for Gemini
        formatted_context = self._format_context_for_gemini(context_data, query)
        
        # Cache result
        self._cache[cache_key] = formatted_context
        
        return formatted_context
    
    def _identify_relevant_categories(self, query: str) -> List[str]:
        """Identify which knowledge categories are relevant to the query"""
        relevant_categories = []
        
        # Check for specific keywords
        for category, keywords in self._query_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    relevant_categories.append(category)
                    break
        
        # If no specific matches, include general categories
        if not relevant_categories:
            if any(word in query for word in ["product", "nova", "crm", "hr", "desk", "analytics"]):
                relevant_categories.extend(["products"])
            elif any(word in query for word in ["leadership", "ceo", "cto", "management"]):
                relevant_categories.extend(["leadership"])
            elif any(word in query for word in ["partner", "integration", "ecosystem"]):
                relevant_categories.extend(["partners"])
            elif any(word in query for word in ["company", "novatech", "mission", "vision"]):
                relevant_categories.extend(["company"])
            elif any(word in query for word in ["contact", "phone", "email", "reach", "get in touch", "call", "message"]):
                relevant_categories.extend(["contact"])
            else:
                # Default to all categories for general queries
                relevant_categories = ["company", "products", "leadership", "partners"]
        
        return list(set(relevant_categories))  # Remove duplicates
    
    def _get_category_data(self, category: str) -> Dict[str, Any]:
        """Get data for a specific category"""
        try:
            if category == "products":
                products_data = knowledge_loader.get_products()
                return {
                    "products": products_data.get("products", []),
                    "pricing_policies": products_data.get("pricing_policies", {}),
                    "technology_stack": products_data.get("technology_stack", {})
                }
            elif category == "leadership":
                leadership_data = knowledge_loader.get_leadership()
                return {
                    "leadership": leadership_data.get("leadership", {}),
                    "shareholding": leadership_data.get("shareholding", {}),
                    "departments": leadership_data.get("departments", {})
                }
            elif category == "partners":
                partners_data = knowledge_loader.get_partners()
                return {
                    "strategic_partners": partners_data.get("strategic_partners", []),
                    "sectors_served": partners_data.get("sectors_served", []),
                    "customer_personas": partners_data.get("customer_personas", [])
                }
            elif category == "company":
                company_data = knowledge_loader.get_company_info()
                return {
                    "company_info": company_data,
                    "financials": company_data.get("financials", {}),
                    "culture": company_data.get("culture", [])
                }
            elif category == "marketing":
                marketing_data = knowledge_loader.get_marketing()
                return {
                    "marketing_assets": marketing_data.get("marketing_assets", {}),
                    "webinars": marketing_data.get("webinars", []),
                    "case_studies": marketing_data.get("case_studies", [])
                }
            elif category == "support":
                faq_data = knowledge_loader.get_faq()
                return {
                    "general_faq": faq_data.get("general_faq", []),
                    "product_specific_faq": faq_data.get("product_specific_faq", []),
                    "technical_faq": faq_data.get("technical_faq", [])
                }
            elif category == "contact":
                return knowledge_loader.get_company_info().get("contact", {})
            else:
                return {}
        except Exception as e:
            logger.warning(f"Failed to get data for category {category}: {e}")
            return {}
    
    def _format_context_for_gemini(self, context_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Format context data for Gemini consumption"""
        if not context_data:
            return {
                "context": "No specific information available for this query.",
                "raw_data": {},
                "query": query
            }
        
        # Create a structured context string
        context_parts = []
        raw_data = {}
        
        for category, data in context_data.items():
            if data:
                context_parts.append(f"\n{category.replace('_', ' ').title()}:")
                raw_data[category] = data
                
                # Add relevant data points
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            context_parts.append(f"- {key}: {value}")
                        elif isinstance(value, list):
                            context_parts.append(f"- {key}: {', '.join(str(v) for v in value[:3])}")
                        else:
                            context_parts.append(f"- {key}: {value}")
                elif isinstance(data, list):
                    for item in data[:3]:  # Limit to 3 items
                        context_parts.append(f"- {item}")
        
        context_string = "\n".join(context_parts) if context_parts else "General information available."
        
        return {
            "context": context_string,
            "raw_data": raw_data,
            "query": query,
            "categories": list(context_data.keys())
        }
    
    def clear_cache(self):
        """Clear the context cache"""
        self._cache.clear()
        logger.debug("Context cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context provider statistics"""
        return {
            "cache_size": len(self._cache),
            "query_keywords": len(self._query_keywords),
            "status": "active"
        }


# Global context provider instance
context_provider = ContextProvider() 