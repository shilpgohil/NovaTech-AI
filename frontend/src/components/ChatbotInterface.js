import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence, useAnimation } from 'framer-motion';
import { Send, ArrowLeft, Bot, Settings, Volume2, VolumeX } from 'lucide-react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const ChatbotInterface = ({ onBackToLanding }) => {
  // Version check to force refresh if needed
  console.log('[DEBUG] ChatbotInterface component version: 2.0 - Connection fixes applied');
  
  const controls = useAnimation();
  const inputControls = useAnimation();
  const messageControls = useAnimation();
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hello! I'm NovaTech AI, your intelligent business assistant. I can help you with company information, market data, industry trends, and much more. What would you like to know?",
      timestamp: new Date(),
      animation: 'welcome'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [wsConnection, setWsConnection] = useState(null); // eslint-disable-line no-unused-vars
  const messagesEndRef = useRef(null);
  const [adminMode, setAdminMode] = useState(false);
  const [adminKey, setAdminKey] = useState('');
  const [systemStatus, setSystemStatus] = useState({});
  const [typingDots, setTypingDots] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showWelcomeAnimation, setShowWelcomeAnimation] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [soundEffects, setSoundEffects] = useState({});
  const [conversationContext, setConversationContext] = useState('');
  const [showContextIndicator, setShowContextIndicator] = useState(false);
  const inputRef = useRef(null);
  const hasShownInitialToast = useRef(false);
  const connectionCheckTimeoutRef = useRef(null);
  const connectionAttempted = useRef(false);
  
  // Add session ID for conversation continuity
  const [sessionId] = useState(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  // Constants
  const API_BASE_URL = 'https://novatech-ai-3qii.onrender.com'; // Force correct backend URL
  const WS_URL = 'https://novatech-ai-3qii.onrender.com'.replace('https://', 'wss://') + '/ws';

  // Fetch conversation context
  const fetchConversationContext = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/langchain/conversation/${sessionId}/context`);
      if (response.data && response.data.status === 'success') {
        const context = response.data.conversation_context;
        if (context && context.trim()) {
          setConversationContext(context);
          setShowContextIndicator(true);
          // Hide context indicator after 5 seconds
          setTimeout(() => setShowContextIndicator(false), 5000);
        }
      }
    } catch (error) {
      // Context fetch failed, which is fine for new conversations
      console.debug('No existing conversation context found');
    }
  };

  // Clear conversation context
  const clearConversationContext = async () => {
    try {
      await axios.delete(`${API_BASE_URL}/api/langchain/conversation/${sessionId}`);
      setConversationContext('');
      setShowContextIndicator(false);
      setMessages([messages[0]]); // Keep only the welcome message
      toast.success('Conversation cleared');
    } catch (error) {
      console.error('Error clearing conversation:', error);
      toast.error('Failed to clear conversation');
    }
  };

  // Sound Effects System
  const initializeSoundEffects = useCallback(() => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      
      const createTone = (frequency, duration, type = 'sine', volume = 0.3) => {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
        oscillator.type = type;
        
        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(volume * 0.7, audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + duration);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + duration);
      };

      const createChord = (frequencies, duration) => {
        frequencies.forEach(freq => createTone(freq, duration, 'sine', 0.2));
      };

      const createLogoSwish = (context) => {
        // Create a dynamic swish effect with multiple oscillators
        const startTime = context.currentTime;
        const duration = 0.8;
        
        // Main swish oscillator (descending frequency)
        const swishOsc = context.createOscillator();
        const swishGain = context.createGain();
        swishOsc.connect(swishGain);
        swishGain.connect(context.destination);
        
        // Swish frequency sweep: high to low
        swishOsc.frequency.setValueAtTime(1200, startTime);
        swishOsc.frequency.exponentialRampToValueAtTime(200, startTime + duration);
        swishOsc.type = 'sawtooth';
        
        // Swish envelope with quick attack and long release
        swishGain.gain.setValueAtTime(0, startTime);
        swishGain.gain.linearRampToValueAtTime(0.4 * 0.7, startTime + 0.05);
        swishGain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        // High-frequency shimmer effect
        const shimmerOsc = context.createOscillator();
        const shimmerGain = context.createGain();
        shimmerOsc.connect(shimmerGain);
        shimmerGain.connect(context.destination);
        
        shimmerOsc.frequency.setValueAtTime(2000, startTime);
        shimmerOsc.frequency.exponentialRampToValueAtTime(400, startTime + duration);
        shimmerOsc.type = 'sine';
        
        shimmerGain.gain.setValueAtTime(0, startTime);
        shimmerGain.gain.linearRampToValueAtTime(0.2 * 0.7, startTime + 0.1);
        shimmerGain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        // Low-end whoosh
        const whooshOsc = context.createOscillator();
        const whooshGain = context.createGain();
        whooshOsc.connect(whooshGain);
        whooshGain.connect(context.destination);
        
        whooshOsc.frequency.setValueAtTime(300, startTime);
        whooshOsc.frequency.exponentialRampToValueAtTime(80, startTime + duration);
        whooshOsc.type = 'triangle';
        
        whooshGain.gain.setValueAtTime(0, startTime);
        whooshGain.gain.linearRampToValueAtTime(0.3 * 0.7, startTime + 0.02);
        whooshGain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
        
        // Start all oscillators
        swishOsc.start(startTime);
        shimmerOsc.start(startTime);
        whooshOsc.start(startTime);
        
        // Stop all oscillators
        swishOsc.stop(startTime + duration);
        shimmerOsc.stop(startTime + duration);
        whooshOsc.stop(startTime + duration);
      };

      setSoundEffects({
        messageSend: () => createChord([440, 554, 659], 0.2), // A major chord
        messageReceive: () => createChord([523, 659, 784], 0.3), // C major chord
        notification: () => createTone(800, 0.1, 'square', 0.4),
        error: () => createChord([220, 196, 174], 0.4), // Low dissonant chord
        success: () => createChord([523, 659, 784, 1047], 0.3), // C major 7th
        typing: () => createTone(600, 0.1, 'sine', 0.2),
        welcome: () => createChord([523, 659, 784, 1047, 1319], 0.5), // C major scale
        connection: () => createChord([440, 554, 659, 880], 0.4), // A major with octave
        disconnect: () => createChord([220, 196, 174, 146], 0.3), // Low descending
        logoSwish: () => createLogoSwish(audioContext) // Special logo transition sound
      });
    } catch (error) {
      console.warn('Web Audio API not supported:', error);
    }
  }, []);

  const playSound = useCallback((soundType) => {
    if (!soundEnabled || !soundEffects[soundType]) return;
    try {
      soundEffects[soundType]();
    } catch (error) {
      console.warn('Error playing sound:', error);
    }
  }, [soundEnabled, soundEffects]);

  const checkBackendConnection = useCallback(async (showToast = false) => {
    // Don't check if already connected and not showing toast
    if (isConnected && !showToast) return;
    
    // Prevent multiple simultaneous connection checks
    if (isProcessing) return;
    
    // Additional guard: prevent connection checks if we've already shown the toast
    if (hasShownInitialToast.current && !showToast) return;
    
    // Prevent multiple initial connection attempts
    if (connectionAttempted.current && !showToast) return;
    
    // TEMPORARY DEBUG: Log connection attempts
    console.log(`[DEBUG] Connection check called - showToast: ${showToast}, isConnected: ${isConnected}, hasShownToast: ${hasShownInitialToast.current}, connectionAttempted: ${connectionAttempted.current}`);
    
    // Clear any pending connection check
    if (connectionCheckTimeoutRef.current) {
      clearTimeout(connectionCheckTimeoutRef.current);
    }
    
    // Debounce connection checks to prevent rapid successive calls
    connectionCheckTimeoutRef.current = setTimeout(async () => {
      try {
        setIsProcessing(true);
        connectionAttempted.current = true;
        console.log(`[DEBUG] Making actual connection request`);
        const response = await axios.get(`${API_BASE_URL}/health`);
        if (response.status === 200) {
          const wasConnected = isConnected;
          setIsConnected(true);
          console.log(`[DEBUG] Connection successful - wasConnected: ${wasConnected}, will show toast: ${!wasConnected && !hasShownInitialToast.current}`);
          
          // Only show success toast and play sound on first connection
          if (!wasConnected && !hasShownInitialToast.current) {
            toast.success('Connected to NovaTech AI Backend');
            playSound('connection'); // Connection success sound
            hasShownInitialToast.current = true;
            console.log(`[DEBUG] Toast shown and sound played`);
          }
        }
      } catch (error) {
        console.error('Backend connection failed:', error);
        const wasConnected = isConnected;
        setIsConnected(false);
        
        // Only show error toast and play sound on first failure
        if (wasConnected) {
          toast.error('Backend connection failed. Please ensure the server is running.');
          playSound('disconnect'); // Connection failed sound
        }
      } finally {
        setIsProcessing(false);
      }
    }, 100); // 100ms debounce
  }, [playSound, isConnected, isProcessing]);

  const initializeWebSocket = useCallback(() => {
    // Don't create new WebSocket if one already exists
    if (wsConnection) return;
    
    try {
      const ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setWsConnection(ws);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
          // REMOVED: This was causing duplicate responses
          // WebSocket is now only for connection status, not message handling
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnection(null);
      };
    } catch (error) {
      console.error('WebSocket initialization failed:', error);
    }
  }, [wsConnection]);

  const scrollToBottom = useCallback(() => {
    // Method 1: Scroll to the messages end ref
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'end',
        inline: 'nearest'
      });
    }
    
    // Method 2: Also scroll the messages container directly
    const messagesContainer = document.querySelector('.messages-container');
    if (messagesContainer) {
      messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'smooth'
      });
    }
    
    // Method 3: Scroll the main chat container
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
      messagesContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, []);

  const focusInput = useCallback(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    console.log('[DEBUG] Main useEffect triggered - Component mounted/updated');
    scrollToBottom();
    checkBackendConnection(true); // Initial connection check with toast
    initializeWebSocket();
    initializeSoundEffects(); // Initialize sound effects
    
    // Set up periodic connection check (every 60 seconds, only if not connected)
    const connectionInterval = setInterval(() => {
      console.log('[DEBUG] Periodic check triggered - isConnected:', isConnected);
      if (!isConnected) {
        checkBackendConnection(false); // Silent connection check only if disconnected
      }
    }, 60000);
    
    if (showWelcomeAnimation) {
      setTimeout(() => {
        controls.start({
          scale: [0.8, 1.1, 1],
          opacity: [0, 1, 1],
          transition: { duration: 1.5, ease: "easeOut" }
        });
        setShowWelcomeAnimation(false);
        
        // Play sounds with proper timing
        setTimeout(() => {
          playSound('welcome'); // Welcome sound
        }, 200);
        
        setTimeout(() => {
          playSound('logoSwish'); // Logo swish sound effect
        }, 800);
        
        // Focus input after welcome animation
        setTimeout(() => {
          focusInput();
        }, 200);
      }, 500);
    }
    
    // Cleanup interval and WebSocket on unmount
    return () => {
      console.log('[DEBUG] Cleanup function called');
      clearInterval(connectionInterval);
      if (connectionCheckTimeoutRef.current) {
        clearTimeout(connectionCheckTimeoutRef.current);
      }
      if (wsConnection) {
        wsConnection.close();
        setWsConnection(null);
      }
    };
  }, [showWelcomeAnimation, controls, checkBackendConnection, playSound, initializeWebSocket, initializeSoundEffects, scrollToBottom, focusInput, wsConnection, connectionCheckTimeoutRef, connectionAttempted]);

  useEffect(() => {
    if (isTyping) {
      playSound('typing'); // Play typing sound when starting to type
      const interval = setInterval(() => {
        setTypingDots(prev => (prev + 1) % 4);
      }, 300);
      return () => clearInterval(interval);
    }
  }, [isTyping, playSound]);

  // Fetch conversation context on mount
  useEffect(() => {
    fetchConversationContext();
  }, []);

  // Fetch conversation context after each message
  useEffect(() => {
    if (messages.length > 1) {
      const timer = setTimeout(() => {
        fetchConversationContext();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [messages.length]);


  // Auto-scroll whenever messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Auto-scroll when typing indicator appears/disappears
  useEffect(() => {
    scrollToBottom();
  }, [isTyping, scrollToBottom]);





  const sendMessageToBackend = async (message) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/langchain/chat`, {
        message: message,
        session_id: sessionId
      });
      
      if (response.data && response.data.status === 'success') {
        return response.data.response;
      } else {
        throw new Error('Invalid response from backend');
      }
    } catch (error) {
      console.error('Error sending message to backend:', error);
      throw error;
    }
  };

  const addBotMessage = (content, animationType = 'default') => {
    const botMessage = {
      id: Date.now(),
      type: 'bot',
      content: content,
      timestamp: new Date(),
      animation: animationType
    };
    setMessages(prev => [...prev, botMessage]);
    messageControls.start({
      y: [20, 0],
      opacity: [0, 1],
      scale: [0.95, 1],
      transition: { duration: 0.6, ease: "easeOut" }
    });
    
    // Auto-scroll to bottom and focus input after bot message
    setTimeout(() => {
      scrollToBottom();
      focusInput();
    }, 300); // Increased delay to ensure message is fully rendered
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping || isProcessing) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);
    setIsProcessing(true);
    playSound('messageSend'); // Play message send sound
    
    // Auto-scroll after user message
    setTimeout(() => {
      scrollToBottom();
    }, 100);
    
    inputControls.start({
      scale: [1, 0.95, 1],
      transition: { duration: 0.3 }
    });
    
    try {
      const response = await sendMessageToBackend(inputValue.trim());
      addBotMessage(response, 'response');
      playSound('messageReceive'); // Play message receive sound
      controls.start({
        scale: [1, 1.05, 1],
        transition: { duration: 0.4 }
      });
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message. Please try again.');
      addBotMessage("I'm sorry, but I'm having trouble connecting to my knowledge base right now. Please try again in a moment.", 'error');
      playSound('error'); // Play error sound
      controls.start({
        x: [-5, 5, -5, 5, 0],
        transition: { duration: 0.5 }
      });
    } finally {
      setIsTyping(false);
      setIsProcessing(false);
    }
  };

  const renderTypingIndicator = () => {
    if (!isTyping) return null;
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="typing-indicator"
      >
        <div className="flex items-center space-x-2">
          <Bot className="w-5 h-5 text-blue-400 animate-pulse" />
          <span className="text-sm text-gray-400">NovaTech AI is thinking</span>
          <div className="flex space-x-1">
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                animate={{
                  scale: typingDots >= i ? 1.2 : 0.8,
                  opacity: typingDots >= i ? 1 : 0.5
                }}
                transition={{ duration: 0.2 }}
                className="w-2 h-2 bg-blue-400 rounded-full"
              />
            ))}
          </div>
        </div>
      </motion.div>
    );
  };

  const renderMessage = (message, index) => {
    const isLastMessage = index === messages.length - 1;
    const animationVariants = {
      welcome: { initial: { opacity: 0, y: 20, scale: 0.8 }, animate: { opacity: 1, y: 0, scale: 1 }, transition: { duration: 0.8, ease: "easeOut" } },
      default: { initial: { opacity: 0, x: message.type === 'user' ? 20 : -20 }, animate: { opacity: 1, x: 0 }, transition: { duration: 0.5, ease: "easeOut" } },
      response: { initial: { opacity: 0, y: 15, scale: 0.95 }, animate: { opacity: 1, y: 0, scale: 1 }, transition: { duration: 0.6, ease: "easeOut" } },
      error: { initial: { opacity: 0, x: [-10, 10, -10, 10, 0] }, animate: { opacity: 1, x: 0 }, transition: { duration: 0.8, ease: "easeOut" } }
    };
    const variants = animationVariants[message.animation] || animationVariants.default;
    
    return (
      <motion.div
        key={message.id}
        initial={variants.initial}
        animate={variants.animate}
        transition={variants.transition}
        className={`message ${message.type} ${isLastMessage ? 'last-message' : ''}`}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <div className="message-content">
          {message.type === 'bot' && (
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              transition={{ delay: 0.2 }} 
              className="message-icon"
            >
              <Bot className="w-4 h-4 text-blue-400 mr-2" />
            </motion.div>
          )}
          <div className="message-text">{message.content}</div>
          {message.type === 'bot' && conversationContext && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.8 }} 
              animate={{ opacity: 1, scale: 1 }} 
              transition={{ delay: 0.4 }} 
              className="flex items-center space-x-1 mt-2"
            >
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-blue-400">Using conversation context</span>
            </motion.div>
          )}
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            transition={{ delay: 0.3 }} 
            className="message-timestamp"
          >
            {message.timestamp.toLocaleTimeString()}
          </motion.div>
        </div>
      </motion.div>
    );
  };

  const renderEnhancedInput = () => (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      transition={{ duration: 0.6, delay: 0.3 }} 
      className="enhanced-input-container"
    >
      <div className="input-wrapper">
        <motion.input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Ask NovaTech AI anything..."
          className="enhanced-input"
          disabled={isProcessing}
          whileFocus={{ scale: 1.02 }}
          animate={{ 
            borderColor: inputValue ? '#3b82f6' : 'rgba(255, 255, 255, 0.2)', 
            boxShadow: inputValue ? '0 0 0 3px rgba(59, 130, 246, 0.1)' : 'none' 
          }}
        />
        <motion.button
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isProcessing}
          className="enhanced-send-btn"
          whileHover={{ scale: 1.1, rotate: 5 }}
          whileTap={{ scale: 0.9 }}
          animate={{ 
            opacity: inputValue.trim() ? 1 : 0.6, 
            scale: inputValue.trim() ? 1 : 0.95 
          }}
        >
          <Send className="w-5 h-5" />
        </motion.button>
      </div>
      {inputValue && (
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          className="char-counter"
        >
          {inputValue.length}/500
        </motion.div>
      )}
    </motion.div>
  );

  return (
    <div className="min-h-screen relative overflow-hidden text-white">
      {/* Dynamic Background with Glass Morphism */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        {/* Animated floating orbs */}
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-32 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-32 left-1/3 w-80 h-80 bg-indigo-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}}></div>
        
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 opacity-30">
          <div className="w-full h-full" style={{
            backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.02) 1px, transparent 0)',
            backgroundSize: '60px 60px'
          }}></div>
        </div>
      </div>
      
      {/* Content Layer */}
      <div className="relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/10 backdrop-blur-md border-b border-white/20 p-4 shadow-lg"
        >
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <motion.button
            onClick={onBackToLanding}
            className="flex items-center space-x-2 text-blue-400 hover:text-blue-300 transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Landing</span>
          </motion.button>
          
          <motion.div 
            ref={controls}
            className="flex items-center space-x-4"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            onAnimationStart={() => {
              // Delay the logo swish sound for better effect
              setTimeout(() => {
                playSound('logoSwish');
              }, 300);
            }}
          >
            <div className="flex items-center space-x-2">
              <Bot className="w-6 h-6 text-blue-400" />
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                NovaTech AI
              </h1>
            </div>
            
            {/* Sound Toggle Button */}
            <motion.button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className={`p-2 rounded-full transition-all duration-300 ${
                soundEnabled 
                  ? 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30' 
                  : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
              }`}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title={soundEnabled ? 'Disable Sound' : 'Enable Sound'}
            >
              {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            </motion.button>
            
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-sm text-gray-300">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
              <motion.button
                onClick={() => {
                  // Only allow manual connection test if not currently connected
                  if (!isConnected) {
                    hasShownInitialToast.current = false;
                    connectionAttempted.current = false;
                    checkBackendConnection(true);
                  }
                }}
                className={`p-1 rounded text-xs transition-all ${
                  isConnected 
                    ? 'text-green-400 hover:text-green-300 hover:bg-green-500/20' 
                    : 'text-blue-400 hover:text-blue-300 hover:bg-blue-500/20'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                title={isConnected ? "Already Connected" : "Test Connection"}
                disabled={isConnected}
              >
                ↻
              </motion.button>
            </div>
          </motion.div>
            
            <motion.button
              onClick={() => setAdminMode(!adminMode)}
            className="text-gray-400 hover:text-white transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            >
              <Settings className="w-5 h-5" />
            </motion.button>
        </div>
      </motion.div>

      {/* Admin Panel */}
        {adminMode && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          className="bg-white/5 backdrop-blur-sm border-b border-white/20 p-4"
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
              <button
                onClick={async () => {
                  try {
                    await axios.post(`${API_BASE_URL}/api/admin/update`, {}, {
                      headers: { 'X-Admin-Key': adminKey }
                    });
                    toast.success('System updated');
                  } catch (error) {
                    toast.error('Failed to update system');
                  }
                }}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-white transition-colors"
              >
                  Update System
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
      <div className="max-w-4xl mx-auto h-[calc(100vh-180px)] flex flex-col chat-container">
        {/* Chat Header with Memory Indicator */}
        <div className="flex items-center justify-between p-4 border-b border-white/20 bg-white/5 backdrop-blur-sm">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">NovaTech AI</h2>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-300">
                  {isConnected ? 'Connected' : 'Connecting...'}
                </span>
                {conversationContext && (
                  <div className="flex items-center space-x-1">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></div>
                    <span className="text-xs text-blue-400">Memory Active</span>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {conversationContext && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="px-3 py-1 bg-blue-500/20 border border-blue-400/30 rounded-full"
              >
                <span className="text-xs text-blue-400 font-medium">Context: {messages.length} messages</span>
              </motion.div>
            )}
            <motion.button
              onClick={clearConversationContext}
              className="p-2 rounded-full text-gray-400 hover:text-white transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Clear Conversation Context"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </motion.button>
          </div>
        </div>

        {/* Messages - Flex to bottom */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 messages-container">
          <AnimatePresence>
            {messages.map((message, index) => renderMessage(message, index))}
          </AnimatePresence>

          {/* Enhanced Typing Indicator */}
          {renderTypingIndicator()}
        </div>

        {/* Input Area - Fixed at bottom */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 border-t border-white/20 bg-gradient-to-t from-black/40 via-white/5 to-transparent backdrop-blur-xl sticky bottom-0"
        >
          {renderEnhancedInput()}
        </motion.div>
      </div>

      {/* Context Indicator */}
      {showContextIndicator && conversationContext && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-blue-100 border border-blue-300 text-blue-800 px-4 py-2 rounded-lg shadow-lg z-50 max-w-md"
        >
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">I remember our conversation!</span>
          </div>
          <div className="text-xs text-blue-600 mt-1">
            {conversationContext.split('\n').slice(0, 2).join(' ')}...
          </div>
        </motion.div>
      )}

      {/* Welcome Animation */}
      <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatbotInterface; 