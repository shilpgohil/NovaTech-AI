import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './PageTransition.css';

const PageTransition = ({ children, isVisible, onTransitionComplete }) => {
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    if (isVisible) {
      setIsTransitioning(true);
    }
  }, [isVisible]);

  const handleTransitionComplete = () => {
    if (onTransitionComplete) {
      onTransitionComplete();
    }
  };

  return (
    <AnimatePresence mode="wait" onExitComplete={handleTransitionComplete}>
      {isVisible && (
        <motion.div
          key="page-transition"
          initial={{ 
            opacity: 0,
            scale: 0.95,
            filter: "blur(10px)",
            transform: "translateY(20px)"
          }}
          animate={{ 
            opacity: 1,
            scale: 1,
            filter: "blur(0px)",
            transform: "translateY(0px)"
          }}
          exit={{ 
            opacity: 0,
            scale: 1.05,
            filter: "blur(15px)",
            transform: "translateY(-20px)"
          }}
          transition={{
            duration: 0.8,
            ease: [0.25, 0.46, 0.45, 0.94], // Custom easing for smooth feel
            staggerChildren: 0.1
          }}
          className="page-transition-container"
        >
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="page-content"
          >
            {children}
          </motion.div>
          
          {/* Background dissolve effect */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.2 }}
            className="background-dissolve"
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default PageTransition; 