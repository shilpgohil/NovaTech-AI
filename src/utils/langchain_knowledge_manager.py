"""
LangChain Knowledge Manager
Advanced knowledge management using LangChain for NovaTech chatbot
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

from ..config import config

logger = logging.getLogger(__name__)

class LangChainKnowledgeManager:
    """Advanced knowledge management using LangChain"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.LANGCHAIN_CHUNK_SIZE,
            chunk_overlap=config.LANGCHAIN_CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        
        self.vector_store = None
        self.knowledge_chunks: Dict[str, List[Document]] = {}
        self.last_updated: Dict[str, datetime] = {}
        
        # Initialize vector database path
        self.vector_db_path = Path(config.VECTOR_DB_PATH)
        self.vector_db_path.mkdir(exist_ok=True)
        
    def load_and_chunk_knowledge(self, knowledge_base_path: str = "./knowledge_base") -> None:
        """Load knowledge files and create chunks with embeddings"""
        knowledge_path = Path(knowledge_base_path)
        
        if not knowledge_path.exists():
            logger.error(f"Knowledge base path not found: {knowledge_base_path}")
            return
        
        # Process each JSON file in the knowledge base
        for json_file in knowledge_path.glob("*.json"):
            category = json_file.stem
            logger.info(f"Processing knowledge category: {category}")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert to text format for chunking
                text_content = self._convert_json_to_text(data, category)
                
                # Create chunks
                chunks = self.text_splitter.split_text(text_content)
                
                # Convert to LangChain Documents
                documents = [
                    Document(
                        page_content=chunk,
                        metadata={
                            "category": category,
                            "source": str(json_file),
                            "chunk_id": f"{category}_{i}",
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    for i, chunk in enumerate(chunks)
                ]
                
                self.knowledge_chunks[category] = documents
                self.last_updated[category] = datetime.now()
                
                logger.info(f"Created {len(documents)} chunks for {category}")
                
            except Exception as e:
                logger.error(f"Error processing {category}: {str(e)}")
        
        # Create vector store from all chunks
        self._create_vector_store()
    
    def _convert_json_to_text(self, data: Any, category: str) -> str:
        """Convert JSON data to searchable text format"""
        if category == "company_info":
            return self._convert_company_info_to_text(data)
        elif category == "products":
            return self._convert_products_to_text(data)
        elif category == "leadership":
            return self._convert_leadership_to_text(data)
        elif category == "faq":
            return self._convert_faq_to_text(data)
        else:
            return self._convert_generic_to_text(data, category)
    
    def _convert_company_info_to_text(self, data: Dict[str, Any]) -> str:
        """Convert company info to searchable text"""
        text_parts = []
        
        if "company_name" in data:
            text_parts.append(f"Company Name: {data['company_name']}")
        
        if "industry" in data:
            text_parts.append(f"Industry: {data['industry']}")
        
        if "headquarters" in data:
            text_parts.append(f"Headquarters: {data['headquarters']}")
        
        if "mission" in data:
            text_parts.append(f"Mission: {data['mission']}")
        
        if "core_values" in data:
            text_parts.append(f"Core Values: {', '.join(data['core_values'])}")
        
        if "contact" in data:
            for key, value in data["contact"].items():
                text_parts.append(f"Contact {key}: {value}")
        
        return "\n".join(text_parts)
    
    def _convert_products_to_text(self, data: Dict[str, Any]) -> str:
        """Convert products to searchable text"""
        text_parts = []
        
        if "products" in data:
            for product in data["products"]:
                product_text = f"Product: {product.get('name', 'Unknown')}"
                product_text += f"\nCategory: {product.get('category', 'Unknown')}"
                product_text += f"\nDescription: {product.get('description', 'No description')}"
                
                if "pricing" in product:
                    product_text += f"\nPricing: {product['pricing']}"
                
                if "features" in product:
                    features = ", ".join(product["features"])
                    product_text += f"\nFeatures: {features}"
                
                text_parts.append(product_text)
        
        return "\n\n".join(text_parts)
    
    def _convert_leadership_to_text(self, data: Dict[str, Any]) -> str:
        """Convert leadership to searchable text"""
        text_parts = []
        
        if "leadership_team" in data:
            for leader in data["leadership_team"]:
                leader_text = f"Leader: {leader.get('name', 'Unknown')}"
                leader_text += f"\nPosition: {leader.get('position', 'Unknown')}"
                leader_text += f"\nDepartment: {leader.get('department', 'Unknown')}"
                
                if "bio" in leader:
                    leader_text += f"\nBio: {leader['bio']}"
                
                text_parts.append(leader_text)
        
        return "\n\n".join(text_parts)
    
    def _convert_faq_to_text(self, data: Dict[str, Any]) -> str:
        """Convert FAQ to searchable text"""
        text_parts = []
        
        if "faqs" in data:
            for faq in data["faqs"]:
                faq_text = f"Question: {faq.get('question', 'Unknown')}"
                faq_text += f"\nAnswer: {faq.get('answer', 'No answer available')}"
                
                if "category" in faq:
                    faq_text += f"\nCategory: {faq['category']}"
                
                text_parts.append(faq_text)
        
        return "\n\n".join(text_parts)
    
    def _convert_generic_to_text(self, data: Any, category: str) -> str:
        """Convert generic JSON data to text"""
        if isinstance(data, dict):
            text_parts = []
            for key, value in data.items():
                if isinstance(value, (str, int, float)):
                    text_parts.append(f"{key}: {value}")
                elif isinstance(value, list):
                    text_parts.append(f"{key}: {', '.join(map(str, value))}")
                elif isinstance(value, dict):
                    text_parts.append(f"{key}: {json.dumps(value, indent=2)}")
            return "\n".join(text_parts)
        else:
            return str(data)
    
    def _create_vector_store(self) -> None:
        """Create FAISS vector store from all knowledge chunks"""
        try:
            all_documents = []
            for category_chunks in self.knowledge_chunks.values():
                all_documents.extend(category_chunks)
            
            if all_documents:
                self.vector_store = FAISS.from_documents(
                    all_documents, 
                    self.embeddings
                )
                
                # Save vector store
                self.vector_store.save_local(str(self.vector_db_path))
                logger.info(f"Vector store created with {len(all_documents)} documents")
            else:
                logger.warning("No documents to create vector store")
                
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
    
    def search_knowledge(self, query: str, top_k: int = None) -> List[Document]:
        """Search knowledge base using vector similarity"""
        if not self.vector_store:
            logger.warning("Vector store not initialized")
            return []
        
        try:
            top_k = top_k or config.VECTOR_SEARCH_TOP_K
            results = self.vector_store.similarity_search(
                query, 
                k=top_k,
                score_threshold=config.VECTOR_SIMILARITY_THRESHOLD
            )
            
            logger.info(f"Found {len(results)} relevant documents for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    def get_context_for_query(self, query: str) -> str:
        """Get relevant context for a query"""
        relevant_docs = self.search_knowledge(query)
        
        if not relevant_docs:
            return "No specific context available for this query."
        
        # Combine relevant context
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(doc.page_content)
        
        return "\n\n".join(context_parts)
    
    def update_knowledge(self, category: str, new_data: Dict[str, Any]) -> None:
        """Update knowledge for a specific category"""
        try:
            # Convert new data to text and chunks
            text_content = self._convert_json_to_text(new_data, category)
            chunks = self.text_splitter.split_text(text_content)
            
            # Create new documents
            documents = [
                Document(
                    page_content=chunk,
                    metadata={
                        "category": category,
                        "source": "dynamic_update",
                        "chunk_id": f"{category}_update_{i}",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                for i, chunk in enumerate(chunks)
            ]
            
            # Update chunks
            self.knowledge_chunks[category] = documents
            self.last_updated[category] = datetime.now()
            
            # Recreate vector store
            self._create_vector_store()
            
            logger.info(f"Updated knowledge for category: {category}")
            
        except Exception as e:
            logger.error(f"Error updating knowledge for {category}: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge manager statistics"""
        total_chunks = sum(len(chunks) for chunks in self.knowledge_chunks.values())
        
        return {
            "total_categories": len(self.knowledge_chunks),
            "total_chunks": total_chunks,
            "vector_store_initialized": self.vector_store is not None,
            "last_updated": {cat: time.isoformat() for cat, time in self.last_updated.items()},
            "chunk_size": config.LANGCHAIN_CHUNK_SIZE,
            "chunk_overlap": config.LANGCHAIN_CHUNK_OVERLAP
        }
    
    def clear_cache(self) -> None:
        """Clear all cached knowledge"""
        self.knowledge_chunks.clear()
        self.last_updated.clear()
        self.vector_store = None
        
        # Remove vector database files
        if self.vector_db_path.exists():
            import shutil
            shutil.rmtree(self.vector_db_path)
            self.vector_db_path.mkdir(exist_ok=True)
        
        logger.info("Knowledge cache cleared")

# Global instance
langchain_knowledge_manager = LangChainKnowledgeManager() 