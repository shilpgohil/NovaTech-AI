import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import LandingPage from './components/LandingPage';
import ChatbotInterfaceNew from './components/ChatbotInterfaceNew';
import PureDissolveTransition from './components/PureDissolveTransition';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('landing');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const handleStartChat = () => {
    // Enhanced transition with dissolving effect
    setTimeout(() => {
      setCurrentView('chatbot');
    }, 800); // Increased delay for smooth dissolving transition
  };

  const handleBackToLanding = () => {
    setCurrentView('landing');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 border-4 border-accent-400 border-t-transparent rounded-full mx-auto mb-4"
          />
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="text-3xl font-display font-bold text-white mb-2"
          >
            NovaTech AI
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.8 }}
            className="text-primary-200 text-lg"
          >
            Initializing...
          </motion.p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="App">
      <AnimatePresence mode="wait" initial={false} onExitComplete={() => {}}>
        {currentView === 'landing' ? (
          <PureDissolveTransition
            key="landing"
            isVisible={currentView === 'landing'}
            onTransitionComplete={() => {}}
          >
            <LandingPage onStartChat={handleStartChat} isVisible={currentView === 'landing'} />
          </PureDissolveTransition>
        ) : (
          <PureDissolveTransition
            key="chatbot"
            isVisible={currentView === 'chatbot'}
            onTransitionComplete={() => {}}
          >
            <ChatbotInterfaceNew onBackToLanding={handleBackToLanding} isVisible={currentView === 'chatbot'} />
          </PureDissolveTransition>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App; 