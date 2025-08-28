"""
LangChain Enhanced Gemini Integration
Advanced AI integration using LangChain for NovaTech chatbot
"""

import logging
import re
from typing import Dict, Any, Optional

# LangChain imports with fallback handling
try:
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
    from langchain.schema import HumanMessage, SystemMessage, AIMessage  # type: ignore
    from langchain.chains import ConversationalRetrievalChain  # type: ignore
    from langchain.memory import ConversationBufferMemory  # type: ignore
    from langchain.prompts import PromptTemplate  # type: ignore
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain packages not available. LangChain integration will be disabled.")

from ..config import config
from ..utils.langchain_knowledge_manager import langchain_knowledge_manager
from ..utils.langgraph_conversation_manager import langgraph_conversation_manager
from ..utils.linkedin_integrator import linkedin_integrator

logger = logging.getLogger(__name__)

class LangChainGeminiClient:
    """Enhanced Gemini client using LangChain for advanced capabilities"""
    
    def __init__(self):
        self.llm = None
        self.conversation_chain = None
        self.memory = None
        self.is_initialized = False
        
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, client will be disabled")
            return
            
        if config.GEMINI_API_KEY:
            self._initialize_langchain_gemini()
        else:
            logger.warning("Gemini API key missing")
    
    def _initialize_langchain_gemini(self):
        """Initialize LangChain Gemini integration"""
        try:
            # Initialize the LLM
            self.llm = ChatGoogleGenerativeAI(
                model=config.MODEL_NAME,
                google_api_key=config.GEMINI_API_KEY,
                temperature=config.LANGCHAIN_TEMPERATURE,
                max_output_tokens=config.LANGCHAIN_MAX_TOKENS,
                convert_system_message_to_human=True
            )
            
            # Initialize conversation memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            # Ensure knowledge manager is initialized first
            if not hasattr(langchain_knowledge_manager, 'vector_store') or langchain_knowledge_manager.vector_store is None:
                logger.info("Initializing knowledge manager...")
                langchain_knowledge_manager.load_and_chunk_knowledge()
            
            # Create conversation chain only if vector store is available
            if langchain_knowledge_manager.vector_store:
                self.conversation_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=langchain_knowledge_manager.vector_store.as_retriever(
                        search_kwargs={"k": config.VECTOR_SEARCH_TOP_K}
                    ),
                    memory=self.memory,
                    return_source_documents=True,
                    verbose=False
                )
                logger.info("Conversational retrieval chain created successfully")
            else:
                self.conversation_chain = None
                logger.warning("Vector store not available, conversation chain disabled")
            
            self.is_initialized = True
            logger.info("LangChain Gemini integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain Gemini: {str(e)}")
            self.is_initialized = False
    
    def generate_response(self, query: str, session_id: Optional[str] = None) -> str:
        """Generate response using LangChain enhanced Gemini"""
        if not self.is_initialized:
            return "I'm not properly initialized. Please check the configuration."
        
        try:
            # Get conversation context if session_id provided
            conversation_context = ""
            conversation = None
            if session_id:
                conversation = langgraph_conversation_manager.get_conversation(session_id)
                if conversation:
                    conversation_context = conversation.get_recent_context()
                    # Update conversation with current query
                    conversation.add_message("user", query)
                    conversation.last_query = query
                else:
                    # Start new conversation if none exists
                    conversation = langgraph_conversation_manager.start_conversation("unknown", session_id)
                    conversation.add_message("user", query)
            
            # Check if this is a casual conversation (greetings, etc.) or a knowledge query
            is_casual_conversation = self._is_casual_conversation(query)
            
            if is_casual_conversation:
                # For casual conversation, use direct LLM with conversation context
                try:
                    if not self.llm:
                        return "AI service not available. Please try again later."
                    
                    messages = [
                        SystemMessage(content=self._get_system_prompt()),
                        HumanMessage(content=self._build_casual_prompt(query, conversation_context))
                    ]
                    
                    result = self.llm.invoke(messages)
                    response = result.content if hasattr(result, 'content') else str(result)
                    
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower() or "rate" in str(e).lower():
                        # Rate limited - use fallback response
                        response = self._get_rate_limited_response(query, conversation_context)
                    else:
                        raise e
                
            else:
                # For knowledge queries, use enhanced knowledge retrieval with conversation context
                knowledge_context = langchain_knowledge_manager.get_context_for_query(query)
                
                # Enhanced knowledge retrieval - try multiple approaches
                if not knowledge_context or len(knowledge_context.strip()) < 50:
                    # Try broader search if initial search is too narrow
                    logger.debug(f"Initial search returned limited results, trying broader search for: {query}")
                    broader_query = self._expand_search_query(query)
                    knowledge_context = langchain_knowledge_manager.get_context_for_query(broader_query)
                
                # If still no results, provide comprehensive company knowledge
                if not knowledge_context or len(knowledge_context.strip()) < 50:
                    logger.debug(f"Using comprehensive company knowledge for: {query}")
                    knowledge_context = self._get_comprehensive_company_knowledge()
                
                # Always ensure we have some knowledge context
                if not knowledge_context or len(knowledge_context.strip()) < 50:
                    logger.warning(f"Failed to retrieve knowledge for query: {query}, using fallback")
                    knowledge_context = self._get_fallback_knowledge(query)
                
                # Build enhanced prompt with conversation context and knowledge
                enhanced_prompt = self._build_enhanced_prompt(
                    query, 
                    knowledge_context, 
                    conversation_context
                )
                
                # Use direct LLM call for better control over response style
                try:
                    if not self.llm:
                        return "AI service not available. Please try again later."
                    
                    messages = [
                        SystemMessage(content=self._get_system_prompt()),
                        HumanMessage(content=enhanced_prompt)
                    ]
                    
                    result = self.llm.invoke(messages)
                    response = result.content if hasattr(result, 'content') else str(result)
                    
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower() or "rate" in str(e).lower():
                        # Rate limited - use fallback response with knowledge context
                        response = self._get_rate_limited_response_with_knowledge(query, knowledge_context, conversation_context)
                    else:
                        raise e
                
                # Log if we found relevant knowledge
                if knowledge_context:
                    logger.debug(f"Found knowledge context for query: {query[:50]}...")
                else:
                    logger.debug(f"No knowledge context found for query: {query}")
            
            # Clean and format response
            response = self._clean_response(response)
            
            # Add AI response to conversation history if conversation exists
            if conversation:
                conversation.add_message("assistant", response)
                # Update conversation state based on response
                # Note: current_state assignment removed as it's not a valid attribute
            
            logger.info(f"Generated response using LangChain Gemini")
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return f"I'm experiencing some technical difficulties. Please try again. Error: {str(e)}"
    
    def _is_casual_conversation(self, query: str) -> bool:
        """Check if the query is casual conversation (greetings, etc.)"""
        casual_patterns = [
            r'\b(hi|hello|hey|howdy|yo)\b',
            r'\b(how are you|how\'s it going|what\'s up)\b',
            r'\b(good morning|good afternoon|good evening)\b',
            r'\b(thanks|thank you|thx)\b',
            r'\b(bye|goodbye|see you|talk to you later)\b',
            r'\b(ok|okay|sure|yeah|yes|no)\b',
            r'\b(that\'s nice|that is nice|cool|awesome|great|good|bad)\b',
            r'\b(i am|i\'m|you are|you\'re)\b',
            r'\b(nice|interesting|wow|oh|ah)\b'
        ]
        
        query_lower = query.lower().strip()
        for pattern in casual_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _build_casual_prompt(self, query: str, conversation_context: str) -> str:
        """Build prompt for casual conversation"""
        prompt_parts = []
        
        if conversation_context:
            prompt_parts.append(f"CONVERSATION CONTEXT:\n{conversation_context}")
            prompt_parts.append("IMPORTANT: Use this context to continue the conversation naturally. Don't start over - build on what was just said. Reference previous topics when relevant.")
        
        prompt_parts.append(f"USER'S LATEST MESSAGE: {query}")
        prompt_parts.append("RESPOND: Chat naturally and continue the conversation flow. Be friendly, casual, and conversational - like you're talking to a friend. If there's relevant context from the conversation, use it to make your response more personal and contextual.")
        
        return "\n\n".join(prompt_parts)
    
    def _build_enhanced_prompt(self, query: str, knowledge_context: str, conversation_context: str) -> str:
        """Build enhanced prompt with context"""
        prompt_parts = []
        
        prompt_parts.append("""You are NovaTech AI, a friendly and helpful assistant. When answering questions, be natural and conversational, not formal or robotic.

IMPORTANT: Use the knowledge provided to answer questions in a friendly, natural way. Don't say "Based on the provided text" or "The provided text gives information about" - just answer naturally like a helpful friend would.

COMMUNICATION STYLE:
• Be friendly and conversational
• Use contractions (I'm, you're, he's, etc.)
• Keep responses natural and helpful
• Don't sound like a database or formal report
• Build on the conversation naturally
• Be warm and approachable
• Reference previous conversation topics when relevant
• Show you remember what was discussed earlier""")
        
        if conversation_context:
            prompt_parts.append(f"CONVERSATION CONTEXT:\n{conversation_context}")
            prompt_parts.append("IMPORTANT: Use this context to continue the conversation naturally and build on previous discussions. Reference specific topics, questions, or preferences mentioned earlier to show continuity and understanding.")
        
        if knowledge_context:
            prompt_parts.append(f"RELEVANT KNOWLEDGE:\n{knowledge_context}")
            prompt_parts.append("IMPORTANT: Use this knowledge to provide helpful answers, but keep the tone friendly and natural. Integrate this information seamlessly into your response.")
        
        prompt_parts.append(f"USER QUERY: {query}")
        prompt_parts.append("RESPOND: Answer the question naturally using the knowledge provided, maintaining a friendly and conversational tone. If there's relevant conversation context, use it to make your response more personalized and contextual.")
        
        return "\n\n".join(prompt_parts)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the AI"""
        return """You are NovaTech AI, a friendly and helpful assistant. You're having a casual chat with someone right now - be natural and conversational!

IMPORTANT: Sound like a real person having a casual conversation, not like a formal business presentation.

COMMUNICATION STYLE:
• Talk like you're chatting with a friend
• Keep responses short, friendly, and natural
• Use contractions (I'm, you're, he's, etc.)
• Be warm and helpful
• Don't sound robotic or formal
• Respond to what they just said, not like you're giving a sales pitch

ABOUT NOVATECH:
NovaTech is a SaaS company in Bengaluru that makes software for CRM, HR, Helpdesk, and Analytics. They help businesses work better with smart software.

HOW TO RESPOND:
• For greetings like "hi" or "hello": Respond warmly and ask how you can help
• For "how are you": Say you're doing great and ask about them
• For NovaTech questions: Give simple, natural answers
• For contact info: Share it naturally when asked
• If you don't know something: Say so casually and naturally
• Always be helpful and friendly
• Build on the conversation naturally

Remember: Just be yourself and chat naturally like a helpful friend would! Keep the conversation flowing naturally."""
    
    def _clean_response(self, response: str) -> str:
        """Clean and format the AI response"""
        if not response:
            return "I couldn't generate a response. Please try again."
        
        # Remove any system-like formatting
        response = response.strip()
        
        # Remove quotes if the entire response is quoted
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        
        # Remove any markdown formatting
        response = response.replace('**', '').replace('*', '')
        
        return response
    
    def chat_with_memory(self, query: str, session_id: str) -> str:
        """Chat with conversation memory"""
        if not self.is_initialized:
            return "I'm not properly initialized. Please check the configuration."
        
        try:
            # Get or create conversation context
            conversation = langgraph_conversation_manager.get_conversation(session_id)
            if not conversation:
                conversation = langgraph_conversation_manager.start_conversation("unknown", session_id)
            
            # Add user message to conversation history
            conversation.add_message("user", query)
            conversation.last_query = query
            
            # Add user message to LangChain memory as well
            if self.memory:
                self.memory.chat_memory.add_user_message(query)
            
            # Generate response with conversation context
            response = self.generate_response(query, session_id)
            
            # Add AI response to LangChain memory
            if self.memory:
                self.memory.chat_memory.add_ai_message(response)
            
            # Update conversation state based on the interaction
            intent = self._determine_intent(query)
            conversation.user_intent = intent
            
            return response
            
        except Exception as e:
            logger.error(f"Chat with memory failed: {str(e)}")
            return f"I'm experiencing some technical difficulties. Please try again."
    
    def _determine_intent(self, message: str) -> str:
        """Determine user intent from message"""
        message_lower = message.lower()
        
        # Product-related intent
        if any(word in message_lower for word in ["product", "crm", "hrm", "helpdesk", "bi", "software", "pricing"]):
            return "product_inquiry"
        
        # Leadership-related intent
        if any(word in message_lower for word in ["ceo", "leader", "management", "team", "founder"]):
            return "leadership_info"
        
        # Company-related intent
        if any(word in message_lower for word in ["company", "about", "mission", "values", "contact", "location"]):
            return "company_info"
        
        # Greeting intent
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return "greeting"
        
        # Closing intent
        if any(word in message_lower for word in ["bye", "goodbye", "thanks", "thank you", "exit"]):
            return "closing"
        
        # Default to question answering
        return "question_answering"
    
    def get_conversation_summary(self, session_id: str) -> str:
        """Get a summary of the conversation"""
        try:
            conversation = langgraph_conversation_manager.get_conversation(session_id)
            if not conversation:
                return "No conversation found for this session."
            
            # Get recent messages
            recent_context = conversation.get_recent_context(max_messages=10)
            
            # Generate summary using LLM
            if not self.llm:
                return "AI service not available for summary generation."
            
            summary_prompt = f"""Please provide a brief summary of this conversation:

{recent_context}

Summary:"""
            
            messages = [
                SystemMessage(content="You are a helpful assistant that summarizes conversations concisely."),
                HumanMessage(content=summary_prompt)
            ]
            
            result = self.llm.invoke(messages)
            summary = result.content if hasattr(result, 'content') else str(result)
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate conversation summary: {str(e)}")
            return "Unable to generate conversation summary."
    
    def clear_memory(self) -> None:
        """Clear conversation memory"""
        if self.memory:
            self.memory.clear()
            logger.info("Conversation memory cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        langchain_stats = {
            "is_initialized": self.is_initialized,
            "model": config.MODEL_NAME,
            "temperature": config.LANGCHAIN_TEMPERATURE,
            "max_tokens": config.LANGCHAIN_MAX_TOKENS,
            "memory_size": len(self.memory.chat_memory.messages) if self.memory else 0
        }
        
        # Get knowledge manager stats
        knowledge_stats = langchain_knowledge_manager.get_stats()
        
        # Get conversation manager stats
        conversation_stats = langgraph_conversation_manager.get_all_conversations_stats()
        
        return {
            "langchain_gemini": langchain_stats,
            "knowledge_manager": knowledge_stats,
            "conversation_manager": conversation_stats
        }
    
    def reset_stats(self) -> None:
        """Reset all statistics and clear memory"""
        self.clear_memory()
        langchain_knowledge_manager.clear_cache()
        langgraph_conversation_manager.clear_all_conversations()
        logger.info("All statistics and memory reset")

    def _expand_search_query(self, query: str) -> str:
        """Expand search query to find more relevant information"""
        query_lower = query.lower()
        
        # Common query expansions
        expansions = {
            'founder': ['founder', 'ceo', 'cto', 'leadership', 'management', 'executive'],
            'company': ['company', 'business', 'organization', 'enterprise', 'corporation'],
            'product': ['product', 'software', 'solution', 'platform', 'tool', 'service'],
            'pricing': ['pricing', 'cost', 'price', 'subscription', 'plan', 'billing'],
            'contact': ['contact', 'email', 'phone', 'address', 'location', 'office'],
            'integration': ['integration', 'api', 'connect', 'sync', 'compatibility'],
            'feature': ['feature', 'functionality', 'capability', 'benefit', 'advantage']
        }
        
        # Find matching expansion
        for _, terms in expansions.items():
            if any(term in query_lower for term in terms):
                return ' '.join(terms)
        
        # Default to broader search
        return f"{query} company business software"
    
    def _get_comprehensive_company_knowledge(self) -> str:
        """Provide comprehensive company knowledge when specific search fails"""
        # Fetch LinkedIn data
        linkedin_data = linkedin_integrator.get_company_updates()
        
        # Combine existing knowledge with LinkedIn data
        existing_knowledge = """COMPREHENSIVE NOVATECH KNOWLEDGE:

COMPANY OVERVIEW:
NovaTech Solutions Pvt. Ltd. is a leading SaaS company headquartered in Bengaluru, India, founded in April 2018. We're known for innovation, customer success, and helping businesses work smarter through intelligent software.

CORE PRODUCTS:
1. NovaCRM (₹2,499/month) - Cloud CRM for sales teams with lead management, pipeline tracking, email campaigns
2. NovaHR (₹4,199/month) - HR & payroll automation with leave tracking, performance management
3. NovaDesk (₹3,299/month) - AI-powered helpdesk with knowledge base and automated responses
4. NovaAnalytics (₹4,999/month) - BI dashboards with ML-powered insights and smart alerts

LEADERSHIP:
- Priya Menon: CEO & Co-founder (28% ownership) - Former VP at TechCorp, 15+ years SaaS leadership
- Rajesh Gupta: CTO & Co-founder (20% ownership) - Ex-Google engineer, PhD Computer Science
- Kavita Sharma: COO (8% ownership) - Former COO at StartupXYZ, MBA from IIM

BUSINESS METRICS:
- Revenue FY2024: ₹105.3 Cr (~$13M)
- Gross Margin: 75%
- Net Profit: ₹18.6 Cr (~$2.3M)
- Customer Count: 1,200+
- Employees: 210 across 5 departments
- Valuation: ₹500 Cr ($60M)

TECHNOLOGY:
- Backend: Python (Django/FastAPI), PostgreSQL, Redis, Kafka
- Frontend: React.js, Material-UI
- AI/ML: TensorFlow, proprietary recommendation engine
- Deployment: AWS Mumbai region with DR in Singapore

MARKET POSITION:
- Industry: SaaS/Enterprise Software
- Target: SMBs and mid-market enterprises (50-500 users)
- Competitive Advantage: Unified platform, AI-powered features, Indian market expertise
- Growth: 25% annual growth rate

CONTACT INFORMATION:
- Email: info@novatech.com
- Phone: +91 80 1234 5678
- Address: Tech Park, Whitefield, Bengaluru, Karnataka 560066, India
- Website: www.novatech.com

This comprehensive knowledge ensures you can answer any question about NovaTech with authority and detail."""
        
        if linkedin_data:
            # Add LinkedIn-specific updates and insights
            recent_updates = linkedin_data.get('recent_updates', [])
            employee_highlights = linkedin_data.get('employee_highlights', [])
            industry_insights = linkedin_data.get('industry_insights', [])
            
            linkedin_section = "\n\nLATEST COMPANY UPDATES (LinkedIn):"
            
            if recent_updates:
                linkedin_section += "\n• " + "\n• ".join([f"{update['content']} ({update['date']})" for update in recent_updates[:3]])
            
            if employee_highlights:
                linkedin_section += "\n\nKEY EMPLOYEE ACTIVITIES:"
                for employee in employee_highlights:
                    linkedin_section += f"\n• {employee['name']} ({employee['title']}): {employee['recent_activity']}"
            
            if industry_insights:
                linkedin_section += "\n\nINDUSTRY INSIGHTS:"
                for insight in industry_insights:
                    linkedin_section += f"\n• {insight['topic']}: {insight['insight']}"
            
            existing_knowledge += linkedin_section
        
        return existing_knowledge

    def _get_fallback_knowledge(self, query: str) -> str:
        """Provide fallback knowledge when all other methods fail"""
        query_lower = query.lower()
        
        # Basic company information that should always be available
        fallback_knowledge = """NOVATECH SOLUTIONS - BASIC COMPANY INFORMATION:

COMPANY OVERVIEW:
NovaTech Solutions Pvt. Ltd. is a leading SaaS company headquartered in Bengaluru, India, founded in April 2018. We specialize in business software solutions.

CORE PRODUCTS:
• NovaCRM - Customer Relationship Management software
• NovaHR - Human Resources and payroll automation
• NovaDesk - AI-powered helpdesk solution
• NovaAnalytics - Business intelligence and analytics platform

LOCATION:
Bengaluru, Karnataka, India

CONTACT:
• Email: info@novatech.com
• Website: www.novatech.com

MISSION:
To empower businesses with intelligent software solutions that drive growth and efficiency."""
        
        # Add specific context based on query keywords
        if any(word in query_lower for word in ["ceo", "founder", "leader", "management"]):
            fallback_knowledge += """

LEADERSHIP:
• Priya Menon: CEO & Co-founder
• Rajesh Gupta: CTO & Co-founder
• Kavita Sharma: COO"""
        
        elif any(word in query_lower for word in ["product", "software", "crm", "hr", "helpdesk"]):
            fallback_knowledge += """

PRODUCT DETAILS:
• All products are cloud-based SaaS solutions
• Designed for small to medium businesses
• Include AI-powered features
• Subscription-based pricing model"""
        
        elif any(word in query_lower for word in ["company", "business", "about"]):
            fallback_knowledge += """

BUSINESS DETAILS:
• Founded: April 2018
• Industry: SaaS/Enterprise Software
• Target Market: SMBs and mid-market enterprises
• Growth: Expanding rapidly in the Indian market"""
        
        return fallback_knowledge

    def _get_rate_limited_response(self, query: str, conversation_context: str) -> str:
        """Provide a fallback response when the API is rate limited."""
        logger.warning(f"API rate limited for query: {query}. Providing fallback response.")
        
        # Provide a helpful response even when rate limited
        if conversation_context:
            return f"""🤖 **AI Service Temporarily Unavailable**

I'm currently experiencing a temporary technical issue with my AI processing capabilities. However, I can see from our conversation that we were discussing: 

**Recent Context:** {conversation_context[:100]}...

**Status:** ⚠️ Rate limit reached (50 requests/day free tier)
**Expected Resolution:** Daily reset at midnight Pacific Time
**Alternative:** Upgrade to paid plan for unlimited requests

Please try again in a few minutes when the system is available, or contact support if you need immediate assistance."""
        else:
            return """🤖 **AI Service Temporarily Unavailable**

I'm currently experiencing a temporary technical issue with my AI processing capabilities.

**Status:** ⚠️ Rate limit reached (50 requests/day free tier)
**Expected Resolution:** Daily reset at midnight Pacific Time
**Alternative:** Upgrade to paid plan for unlimited requests

Please try again in a few minutes when the system is available, or contact support if you need immediate assistance."""

    def _get_rate_limited_response_with_knowledge(self, query: str, knowledge_context: str, conversation_context: str) -> str:
        """Provide a fallback response when the API is rate limited, but knowledge context is available."""
        logger.warning(f"API rate limited for query: {query}. Providing fallback response with knowledge context.")
        
        response_parts = []
        response_parts.append("""🤖 **AI Service Temporarily Unavailable**

I'm currently experiencing a temporary technical issue with my AI processing capabilities, but I can provide some information based on what I know:""")
        
        if knowledge_context:
            response_parts.append(f"\n\n📚 **KNOWLEDGE BASE INFORMATION:**\n{knowledge_context}")
        
        if conversation_context:
            response_parts.append(f"\n\n💬 **CONVERSATION CONTEXT:**\n{conversation_context[:200]}...")
        
        response_parts.append("""\n\n⚠️ **CURRENT STATUS:**
• **Issue:** Rate limit reached (50 requests/day free tier)
• **Expected Resolution:** Daily reset at midnight Pacific Time
• **Alternative:** Upgrade to paid plan for unlimited requests

Please try again in a few minutes when the AI system is available, or contact support if you need immediate assistance.""")
        
        return "".join(response_parts)

    def _determine_conversation_state(self, query: str, response: str) -> str:
        """Determine the appropriate conversation state based on query and response"""
        query_lower = query.lower()
        
        # Product-related state
        if any(word in query_lower for word in ["product", "crm", "hrm", "helpdesk", "bi", "software", "pricing"]):
            return "product_inquiry"
        
        # Leadership-related state
        if any(word in query_lower for word in ["ceo", "leader", "management", "team", "founder"]):
            return "leadership_info"
        
        # Company-related state
        if any(word in query_lower for word in ["company", "about", "mission", "values", "contact", "location"]):
            return "company_info"
        
        # Greeting state
        if any(word in query_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return "greeting"
        
        # Closing state
        if any(word in query_lower for word in ["bye", "goodbye", "thanks", "thank you", "exit"]):
            return "closing"
        
        # Default to question answering
        return "question_answering"

# Global instance
langchain_gemini_client = LangChainGeminiClient() 