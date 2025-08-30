import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, ArrowLeft, Settings } from 'lucide-react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const ChatbotInterfaceNew = ({ onBackToLanding, isVisible = true }) => {
  // Core state
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hello! I'm NovaTech AI, your intelligent business assistant. I can help you with company information, market data, industry trends, and much more. What would you like to know?",
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [adminMode, setAdminMode] = useState(false);
  const [adminKey, setAdminKey] = useState('');
  const [systemStatus, setSystemStatus] = useState({});
  const [soundEnabled, setSoundEnabled] = useState(true);
  
  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const connectionAttempted = useRef(false);
  
  // Add session ID for conversation continuity
  const [sessionId] = useState(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  
  // Constants
  const API_BASE_URL = 'https://novatech-ai-3qii.onrender.com'; // Force correct backend URL
  
  // Simple sound effects
  const playSound = useCallback((type) => {
    if (!soundEnabled) return; // Don't play if disabled
    
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      
      if (type === 'send') {
        // High-pitched send sound
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.2);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
      } else if (type === 'receive') {
        // Low-pitched receive sound
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
      }
    } catch (error) {
      // Silently fail if audio is not supported
      console.warn('Audio not supported:', error);
    }
  }, [soundEnabled]);
  
  // Scroll to bottom utility
  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'end' 
      });
    }
  }, []);
  
  // Focus input utility
  const focusInput = useCallback(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);
  
  // Connection check - SIMPLIFIED and ROBUST
  const checkBackendConnection = useCallback(async () => {
    // Only check once per session
    if (connectionAttempted.current) return;
    
    try {
      connectionAttempted.current = true;
      const response = await axios.get(`${API_BASE_URL}/health`);
      
      if (response.status === 200) {
        setIsConnected(true);
        toast.success('Connected to NovaTech AI Backend');
      }
    } catch (error) {
      console.error('Backend connection failed:', error);
      setIsConnected(false);
      toast.error('Backend connection failed. Please ensure the server is running.');
    }
  }, [API_BASE_URL]);
  
  // Send message to backend
  const sendMessageToBackend = async (message) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message: message,
        session_id: sessionId
      });
      
      if (response.data && response.data.response) {
        return response.data.response;
      } else {
        throw new Error('Invalid response from backend');
      }
    } catch (error) {
      console.error('Error sending message to backend:', error);
      throw error;
    }
  };
  
  // Add bot message
  const addBotMessage = (content) => {
    const botMessage = {
      id: Date.now(),
      type: 'bot',
      content: content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, botMessage]);
  };
  
  // Handle send message
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);
    
    // Play send sound
    playSound('send');
    
    try {
      const response = await sendMessageToBackend(inputValue.trim());
      addBotMessage(response);
      // Play receive sound
      playSound('receive');
    } catch (error) {
      addBotMessage("Sorry, I encountered an error processing your message. Please try again.");
    } finally {
      setIsTyping(false);
    }
  };
  
  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  // Initialize connection on mount
  useEffect(() => {
    checkBackendConnection();
    focusInput();
  }, [checkBackendConnection, focusInput]);
  
  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);
  
  // Auto-scroll when typing indicator appears/disappears
  useEffect(() => {
    scrollToBottom();
  }, [isTyping, scrollToBottom]);
  
  // Render message
  const renderMessage = (message, index) => (
    <motion.div
      key={message.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg backdrop-blur-xl shadow-lg border ${
        message.type === 'user' 
          ? 'bg-gradient-to-r from-blue-600/80 to-purple-600/80 text-white border-blue-400/30' 
          : 'bg-white/10 text-gray-100 border-white/20'
      }`}>
        <p className="text-sm">{message.content}</p>
        <p className="text-xs opacity-70 mt-1">
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </motion.div>
  );
  
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        {/* Floating orbs with bloom effects */}
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-32 left-1/3 w-80 h-80 bg-pink-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}}></div>
        <div className="absolute top-1/2 right-20 w-64 h-64 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
        
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
      </div>
      
      {/* Content with glassy effects */}
      <div className="relative z-10">
        {/* Header */}
        <div className="bg-white/5 backdrop-blur-xl border-b border-white/10 shadow-2xl">
          <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
            <motion.button
              onClick={onBackToLanding}
              className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Landing</span>
            </motion.button>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                <span className="text-sm text-gray-300">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              <motion.button
                onClick={() => setSoundEnabled(!soundEnabled)}
                className={`transition-colors ${soundEnabled ? 'text-green-400' : 'text-gray-400'}`}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title={soundEnabled ? 'Disable Sound' : 'Enable Sound'}
              >
                🔊
              </motion.button>
              
              <motion.button
                onClick={() => setAdminMode(!adminMode)}
                className="text-gray-400 hover:text-white transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Settings className="w-5 h-5" />
              </motion.button>
            </div>
          </div>
        </div>
        
        {/* Admin Panel */}
        {adminMode && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-white/5 backdrop-blur-xl border-b border-white/10 p-4 shadow-lg"
          >
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center space-x-4">
                <input
                  type="password"
                  placeholder="Admin Key"
                  value={adminKey}
                  onChange={(e) => setAdminKey(e.target.value)}
                  className="px-3 py-2 bg-white/10 border border-white/20 rounded text-white placeholder-gray-400"
                />
                <button
                  onClick={async () => {
                    try {
                      const response = await axios.post(`${API_BASE_URL}/api/admin/status`, {}, {
                        headers: { 'X-Admin-Key': adminKey }
                      });
                      setSystemStatus(response.data);
                      toast.success('System status retrieved');
                    } catch (error) {
                      toast.error('Failed to get system status');
                    }
                  }}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors"
                >
                  Get Status
                </button>
              </div>
              {Object.keys(systemStatus).length > 0 && (
                <div className="mt-4 p-4 bg-white/10 rounded">
                  <h3 className="text-lg font-semibold mb-2">System Status:</h3>
                  <pre className="text-sm text-gray-300 overflow-auto">
                    {JSON.stringify(systemStatus, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </motion.div>
        )}
        
        {/* Chat Container */}
        <div className="max-w-4xl mx-auto h-[calc(100vh-200px)] flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <AnimatePresence>
              {messages.map((message, index) => renderMessage(message, index))}
            </AnimatePresence>
            
            {/* Typing Indicator */}
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start mb-4"
              >
                <div className="bg-white/10 backdrop-blur-xl border border-white/20 text-gray-100 px-4 py-2 rounded-lg shadow-lg">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Input Area */}
          <div className="border-t border-white/10 p-4 bg-white/5 backdrop-blur-xl">
            <div className="flex space-x-4">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask NovaTech AI anything..."
                className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 transition-all duration-300 backdrop-blur-xl"
              />
              <motion.button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isTyping}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed rounded-lg text-white transition-all duration-300 shadow-lg backdrop-blur-xl"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Send className="w-5 h-5" />
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotInterfaceNew; 