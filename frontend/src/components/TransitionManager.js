import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './PageTransition.css';

const TransitionManager = ({ children, isVisible, transitionType = 'dissolve' }) => {



  // Different transition variants for different effects
  const transitionVariants = {
    dissolve: {
      initial: {
        opacity: 0,
        scale: 0.95,
        filter: "blur(15px)",
        transform: "translateY(20px)"
      },
      animate: {
        opacity: 1,
        scale: 1,
        filter: "blur(0px)",
        transform: "translateY(0px)"
      },
      exit: {
        opacity: 0,
        scale: 1.05,
        filter: "blur(20px)",
        transform: "translateY(-20px)"
      }
    },
    slide: {
      initial: {
        opacity: 0,
        scale: 0.95,
        filter: "blur(10px)"
      },
      animate: {
        opacity: 1,
        scale: 1,
        filter: "blur(0px)"
      },
      exit: {
        opacity: 0,
        scale: 1.05,
        filter: "blur(10px)"
      }
    },
    fade: {
      initial: {
        opacity: 0,
        y: 20
      },
      animate: {
        opacity: 1,
        y: 0
      },
      exit: {
        opacity: 0,
        y: -20
      }
    }
  };

  const currentVariants = transitionVariants[transitionType];

  return (
    <div className="transition-manager">
      <AnimatePresence 
        mode="wait" 
        initial={false}
      >
        {isVisible && (
          <motion.div
            key="page-content"
            variants={currentVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{
              duration: 1.2,
              ease: [0.25, 0.46, 0.45, 0.94],
              staggerChildren: 0.15,
              delayChildren: 0.1
            }}
            className="page-transition-container"
          >
            {/* Background dissolve effect */}
            <motion.div
              initial={{ opacity: 0, scale: 1.2 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 1.5, ease: "easeInOut" }}
              className="background-dissolve"
            />
            
            {/* Main content with staggered children */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="page-content"
            >
              {React.Children.map(children, (child, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{
                    duration: 0.6,
                    delay: 0.4 + (index * 0.1),
                    ease: [0.25, 0.46, 0.45, 0.94]
                  }}
                  className="content-reveal"
                >
                  {child}
                </motion.div>
              ))}
            </motion.div>

            {/* Transition overlay for smooth dissolve */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0 }}
              exit={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              className="page-overlay"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TransitionManager; 