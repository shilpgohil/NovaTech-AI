"""
LangGraph Conversation Manager
Stateful conversation management using LangGraph for NovaTech chatbot
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Annotated
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from ..config import config
from .langchain_knowledge_manager import langchain_knowledge_manager

logger = logging.getLogger(__name__)

class ConversationState(str, Enum):
    """Possible conversation states"""
    GREETING = "greeting"
    QUESTION_ANSWERING = "question_answering"
    PRODUCT_INQUIRY = "product_inquiry"
    LEADERSHIP_INFO = "leadership_info"
    COMPANY_INFO = "company_info"
    FOLLOW_UP = "follow_up"
    CLOSING = "closing"

@dataclass
class ConversationContext:
    """Conversation context and state"""
    user_id: str
    session_id: str
    current_state: ConversationState = ConversationState.GREETING
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    user_intent: Optional[str] = None
    last_query: Optional[str] = None
    knowledge_context: Optional[str] = None
    response_count: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "state": self.current_state.value if hasattr(self.current_state, 'value') else str(self.current_state),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.last_activity = datetime.now()
        self.response_count += 1
    
    def get_recent_context(self, max_messages: int = 5) -> str:
        """Get recent conversation context"""
        if not self.conversation_history:
            return ""
            
        recent_messages = self.conversation_history[-max_messages:]
        context_parts = []
        
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        if context_parts:
            return "Recent conversation:\n" + "\n".join(context_parts)
        return ""
    
    def is_timed_out(self) -> bool:
        """Check if conversation has timed out"""
        timeout_seconds = config.LANGGRAPH_CONVERSATION_TIMEOUT
        return (datetime.now() - self.last_activity).total_seconds() > timeout_seconds

class LangGraphConversationManager:
    """Stateful conversation management using LangGraph"""
    
    def __init__(self):
        self.conversations: Dict[str, ConversationContext] = {}
        self.memory_saver = MemorySaver()
        self.conversation_graph = self._build_conversation_graph()
        
    def _build_conversation_graph(self) -> StateGraph:
        """Build the conversation workflow graph"""
        
        # Define the state graph
        workflow = StateGraph(ConversationContext)
        
        # Add nodes for different conversation states
        workflow.add_node("greeting", self._handle_greeting)
        workflow.add_node("question_answering", self._handle_question_answering)
        workflow.add_node("product_inquiry", self._handle_product_inquiry)
        workflow.add_node("leadership_info", self._handle_leadership_info)
        workflow.add_node("company_info", self._handle_company_info)
        workflow.add_node("follow_up", self._handle_follow_up)
        workflow.add_node("closing", self._handle_closing)
        
        # Define the workflow edges
        workflow.set_entry_point("greeting")
        
        # Greeting can lead to question answering or closing
        workflow.add_edge("greeting", "question_answering")
        workflow.add_edge("greeting", "closing")
        
        # Question answering can lead to specific info nodes or follow-up
        workflow.add_edge("question_answering", "product_inquiry")
        workflow.add_edge("question_answering", "leadership_info")
        workflow.add_edge("question_answering", "company_info")
        workflow.add_edge("question_answering", "follow_up")
        workflow.add_edge("question_answering", "closing")
        
        # Specific info nodes can lead to follow-up or closing
        workflow.add_edge("product_inquiry", "follow_up")
        workflow.add_edge("product_inquiry", "closing")
        workflow.add_edge("leadership_info", "follow_up")
        workflow.add_edge("leadership_info", "closing")
        workflow.add_edge("company_info", "follow_up")
        workflow.add_edge("company_info", "closing")
        
        # Follow-up can lead back to question answering or closing
        workflow.add_edge("follow_up", "question_answering")
        workflow.add_edge("follow_up", "closing")
        
        # All paths can end
        workflow.add_edge("closing", END)
        
        return workflow.compile(checkpointer=self.memory_saver)
    
    def start_conversation(self, user_id: str, session_id: str) -> ConversationContext:
        """Start a new conversation"""
        conversation = ConversationContext(
            user_id=user_id,
            session_id=session_id
        )
        
        self.conversations[session_id] = conversation
        logger.info(f"Started new conversation for user {user_id}, session {session_id}")
        
        return conversation
    
    def get_conversation(self, session_id: str) -> Optional[ConversationContext]:
        """Get existing conversation by session ID"""
        conversation = self.conversations.get(session_id)
        
        if conversation and conversation.is_timed_out():
            # Clean up timed out conversation
            del self.conversations[session_id]
            return None
        
        return conversation
    
    def process_message(self, session_id: str, user_message: str) -> Tuple[str, ConversationState]:
        """Process a user message and return response with new state"""
        conversation = self.get_conversation(session_id)
        
        if not conversation:
            # Start new conversation if none exists
            conversation = self.start_conversation("unknown", session_id)
        
        # Add user message to history
        conversation.add_message("user", user_message)
        conversation.last_query = user_message
        
        # Determine intent and update state
        intent = self._determine_intent(user_message)
        conversation.user_intent = intent
        
        # Get relevant knowledge context
        conversation.knowledge_context = langchain_knowledge_manager.get_context_for_query(user_message)
        
        # Run conversation through the graph
        try:
            result = self.conversation_graph.invoke(conversation)
            
            # Extract response and new state
            if isinstance(result, list) and len(result) > 0:
                response = result[-1].get("response", "I'm not sure how to respond to that.")
                new_state = result[-1].get("state", ConversationState.QUESTION_ANSWERING)
            else:
                response = "I'm having trouble processing your request. Please try again."
                new_state = ConversationState.QUESTION_ANSWERING
            
            # Update conversation state
            conversation.current_state = new_state
            
            # Add assistant response to history
            conversation.add_message("assistant", response)
            
            return response, new_state
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            fallback_response = "I'm experiencing some technical difficulties. Please try again."
            conversation.add_message("assistant", fallback_response)
            return fallback_response, ConversationState.QUESTION_ANSWERING
    
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
    
    # Node handlers for the conversation graph
    def _handle_greeting(self, state: ConversationContext) -> Dict[str, Any]:
        """Handle greeting state"""
        greetings = [
            "Hello! Welcome to NovaTech Solutions. How can I help you today?",
            "Hi there! I'm your NovaTech assistant. What would you like to know?",
            "Good day! I'm here to help with any questions about NovaTech. What's on your mind?"
        ]
        
        import random
        response = random.choice(greetings)
        
        return {
            "response": response,
            "state": ConversationState.QUESTION_ANSWERING
        }
    
    def _handle_question_answering(self, state: ConversationContext) -> Dict[str, Any]:
        """Handle general question answering"""
        if state.knowledge_context:
            # Use the knowledge context to provide a more informed response
            response = f"I'd be happy to help you with that! {state.knowledge_context}"
        else:
            # Provide a helpful response even without specific knowledge
            response = "I'd be happy to help you with information about NovaTech Solutions. What specific question do you have? I can tell you about our products, leadership team, company information, or help you with any other inquiries."
        
        return {
            "response": response,
            "state": ConversationState.QUESTION_ANSWERING
        }
    
    def _handle_product_inquiry(self, state: ConversationContext) -> Dict[str, Any]:
        """Handle product-related inquiries"""
        if state.knowledge_context:
            response = f"Great question about our products! {state.knowledge_context}"
        else:
            response = "I'd be happy to tell you about our products! We offer a unified software suite including CRM, HRM, Helpdesk, and BI solutions. What specific product would you like to know more about?"
        
        return {
            "response": response,
            "state": ConversationState.FOLLOW_UP
        }
    
    def _handle_leadership_info(self, state: ConversationContext) -> Dict[str, Any]:
        """Handle leadership-related inquiries"""
        if state.knowledge_context:
            response = f"Great question about our leadership! {state.knowledge_context}"
        else:
            response = "I can tell you about our leadership team! We have experienced leaders across various departments. Who specifically would you like to know about?"
        
        return {
            "response": response,
            "state": ConversationState.FOLLOW_UP
        }
    
    def _handle_company_info(self, state: ConversationContext) -> Dict[str, Any]:
        """Handle company information inquiries"""
        if state.knowledge_context:
            response = f"Great question about NovaTech! {state.knowledge_context}"
        else:
            response = "NovaTech Solutions is a Bengaluru-based SaaS company empowering businesses through intelligent software. What aspect of the company would you like to learn more about?"
        
        return {
            "response": response,
            "state": ConversationState.FOLLOW_UP
        }
    
    def _handle_follow_up(self, state: ConversationContext) -> Dict[str, Any]:
        """Handle follow-up questions"""
        # Use conversation context to provide more personalized follow-up
        if state.conversation_history and len(state.conversation_history) > 2:
            recent_topics = self._extract_recent_topics(state.conversation_history[-3:])
            if recent_topics:
                response = f"Is there anything else you'd like to know about {recent_topics[0]} or any other aspect of NovaTech?"
            else:
                response = "Is there anything else you'd like to know about NovaTech?"
        else:
            response = "Is there anything else you'd like to know about NovaTech?"
        
        return {
            "response": response,
            "state": ConversationState.QUESTION_ANSWERING
        }
    
    def _extract_recent_topics(self, recent_messages: List[Dict[str, Any]]) -> List[str]:
        """Extract recent conversation topics for better follow-up"""
        topics = []
        for msg in recent_messages:
            content = msg.get('content', '').lower()
            
            # Extract product mentions
            if any(word in content for word in ['crm', 'hr', 'helpdesk', 'analytics', 'bi']):
                topics.append('our products')
            
            # Extract leadership mentions
            if any(word in content for word in ['ceo', 'cto', 'founder', 'leader']):
                topics.append('our leadership team')
            
            # Extract company mentions
            if any(word in content for word in ['company', 'business', 'novatech']):
                topics.append('NovaTech')
        
        return list(set(topics))  # Remove duplicates
    
    def _handle_closing(self, state: ConversationContext) -> Dict[str, Any]:
        """Handle conversation closing"""
        closings = [
            "Thank you for chatting with me! Feel free to reach out if you have more questions about NovaTech.",
            "It's been great helping you! Don't hesitate to ask if you need more information later.",
            "Thanks for your time! I'm here whenever you need to know more about NovaTech Solutions."
        ]
        
        import random
        response = random.choice(closings)
        
        return {
            "response": response,
            "state": ConversationState.CLOSING
        }
    
    def get_conversation_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific conversation"""
        conversation = self.get_conversation(session_id)
        
        if not conversation:
            return None
        
        return {
            "session_id": session_id,
            "user_id": conversation.user_id,
            "current_state": conversation.current_state.value if hasattr(conversation.current_state, 'value') else str(conversation.current_state),
            "message_count": len(conversation.conversation_history),
            "response_count": conversation.response_count,
            "start_time": conversation.start_time.isoformat(),
            "last_activity": conversation.last_activity.isoformat(),
            "duration_minutes": (conversation.last_activity - conversation.start_time).total_seconds() / 60
        }
    
    def get_all_conversations_stats(self) -> Dict[str, Any]:
        """Get statistics for all active conversations"""
        active_conversations = [
            conv for conv in self.conversations.values() 
            if not conv.is_timed_out()
        ]
        
        return {
            "total_active_conversations": len(active_conversations),
            "total_sessions": len(self.conversations),
            "conversations": [
                self.get_conversation_stats(conv.session_id) 
                for conv in active_conversations
            ]
        }
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear a specific conversation"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared conversation: {session_id}")
            return True
        return False
    
    def clear_all_conversations(self) -> int:
        """Clear all conversations and return count"""
        count = len(self.conversations)
        self.conversations.clear()
        logger.info(f"Cleared {count} conversations")
        return count

# Global instance
langgraph_conversation_manager = LangGraphConversationManager() 