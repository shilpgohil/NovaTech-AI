import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './PageTransition.css';

const PureDissolveTransition = ({ children, isVisible, onTransitionComplete }) => {
  const handleTransitionComplete = () => {
    if (onTransitionComplete) {
      onTransitionComplete();
    }
  };

  return (
    <div className="pure-dissolve-transition">
      <AnimatePresence 
        mode="wait" 
        onExitComplete={handleTransitionComplete}
        initial={false}
      >
        {isVisible && (
          <motion.div
            key="pure-dissolve-content"
            initial={{
              opacity: 0,
              scale: 0.95,
              filter: "blur(15px)"
            }}
            animate={{
              opacity: 1,
              scale: 1,
              filter: "blur(0px)"
            }}
            exit={{
              opacity: 0,
              scale: 1.05,
              filter: "blur(20px)"
            }}
            transition={{
              duration: 1.2,
              ease: [0.25, 0.46, 0.45, 0.94],
              staggerChildren: 0.1,
              delayChildren: 0.1
            }}
            className="pure-dissolve-container"
          >
            {/* Enhanced background dissolve effect */}
            <motion.div
              initial={{ opacity: 0, scale: 1.1 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 1.5, ease: "easeInOut" }}
              className="enhanced-background-dissolve"
            />
            
            {/* Main content with pure dissolve */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="pure-dissolve-content"
            >
              {React.Children.map(children, (child, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{
                    duration: 0.6,
                    delay: 0.4 + (index * 0.1),
                    ease: [0.25, 0.46, 0.45, 0.94]
                  }}
                  className="pure-content-reveal"
                >
                  {child}
                </motion.div>
              ))}
            </motion.div>

            {/* Smooth dissolve overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0 }}
              exit={{ opacity: 1 }}
              transition={{ duration: 1.0 }}
              className="pure-dissolve-overlay"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PureDissolveTransition; 