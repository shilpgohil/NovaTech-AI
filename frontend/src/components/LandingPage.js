import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Brain, Zap, ArrowRight } from 'lucide-react';
import TransitionManager from './TransitionManager';

const LandingPage = ({ onStartChat, isVisible = true }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [stars, setStars] = useState([]);
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    // Create realistic space starfield with different star layers for parallax effect
    const starLayers = [
      { count: 120, size: 1, speed: 0.5, opacity: 0.8, color: 'white' },      // Distant stars (slow, small)
      { count: 80, size: 1.5, speed: 1, opacity: 0.9, color: 'yellow' },      // Medium stars (medium speed)
      { count: 40, size: 2, speed: 1.5, opacity: 1, color: 'yellow' },        // Closer stars (faster)
      { count: 20, size: 2.5, speed: 2, opacity: 1, color: 'orange' },        // Near stars (fastest)
    ];

    const allStars = [];
    starLayers.forEach((layer, layerIndex) => {
      for (let i = 0; i < layer.count; i++) {
        allStars.push({
          id: `${layerIndex}-${i}`,
          x: Math.random() * 120 - 10, // Start slightly off-screen for smooth entry
          y: Math.random() * 120 - 10,
          size: layer.size,
          speed: layer.speed,
          opacity: layer.opacity,
          color: layer.color,
          layer: layerIndex,
          // Random starting positions for continuous flow
          startX: Math.random() * 120 - 10,
          startY: Math.random() * 120 - 10,
        });
      }
    });
    
    setStars(allStars);
  }, []);

  const handleBallClick = () => {
    setIsTransitioning(true);
    
    // Enhanced click animation before transition
    const ball = document.querySelector('.main-ball');
    if (ball) {
      ball.style.transform = 'scale(0.8) rotate(180deg)';
      ball.style.transition = 'all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
    }
    
    // Add a glow effect
    const glow = document.querySelector('.ball-glow');
    if (glow) {
      glow.style.transform = 'scale(2)';
      glow.style.opacity = '0.8';
      glow.style.transition = 'all 0.4s ease-out';
    }
    
    // Delay the transition to show the click animation
    setTimeout(() => {
      onStartChat();
    }, 800); // Increased delay for smooth transition
  };

  const handleTransitionComplete = () => {
    setIsTransitioning(false);
  };

  return (
    <TransitionManager 
      isVisible={isVisible} 
      onTransitionComplete={handleTransitionComplete}
      transitionType="dissolve"
    >
      <motion.div 
        className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 relative overflow-hidden"
        exit={{ 
          opacity: 0, 
          scale: 0.95,
          transition: { duration: 0.8, ease: "easeInOut" }
        }}
      >
      {/* Realistic Space Starfield with Parallax Effect */}
      {stars.map((star) => (
        <motion.div
          key={star.id}
          className="absolute rounded-full"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            width: `${star.size}px`,
            height: `${star.size}px`,
            background: star.color === 'white' 
              ? `radial-gradient(circle, rgba(255, 255, 255, ${star.opacity}) 0%, rgba(255, 255, 255, ${star.opacity * 0.7}) 70%, transparent 100%)`
              : star.color === 'yellow'
              ? `radial-gradient(circle, rgba(255, 255, 0, ${star.opacity}) 0%, rgba(255, 215, 0, ${star.opacity * 0.7}) 70%, transparent 100%)`
              : `radial-gradient(circle, rgba(255, 165, 0, ${star.opacity}) 0%, rgba(255, 140, 0, ${star.opacity * 0.7}) 70%, transparent 100%)`,
            boxShadow: star.color === 'white'
              ? `0 0 ${star.size * 2}px rgba(255, 255, 255, ${star.opacity * 0.8})`
              : star.color === 'yellow'
              ? `0 0 ${star.size * 2}px rgba(255, 255, 0, ${star.opacity * 0.8})`
              : `0 0 ${star.size * 2}px rgba(255, 165, 0, ${star.opacity * 0.8})`,
            zIndex: star.layer,
          }}
          animate={{
            // Parallax movement - different layers move at different speeds
            y: [star.startY, star.startY - (200 * star.speed)],
            x: [star.startX, star.startX + (Math.random() * 40 - 20) * star.speed],
            opacity: [star.opacity, star.opacity * 0.3, 0],
            scale: [1, 1.2, 0.8],
          }}
          transition={{
            duration: 20 / star.speed, // Faster stars complete cycle sooner
            repeat: Infinity,
            ease: "linear",
            delay: Math.random() * 5,
          }}
          onAnimationComplete={() => {
            // Reset star position for continuous flow
            star.startY = Math.random() * 120 - 10;
            star.startX = Math.random() * 120 - 10;
          }}
        />
      ))}

      {/* Background Grid */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0)`,
          backgroundSize: '50px 50px'
        }} />
      </div>
      
      {/* Space Starfield Background Complete */}

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4">
        {/* NovaTech AI Branding */}
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="text-center mb-16"
        >
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-accent-400 to-accent-600 rounded-full mb-6 shadow-2xl"
          >
            <Brain className="w-10 h-10 text-white" />
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="text-6xl md:text-8xl font-display font-bold text-white mb-4"
          >
            NovaTech
            <span className="block text-4xl md:text-6xl text-accent-400 mt-2">AI</span>
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
            className="text-xl md:text-2xl text-primary-200 max-w-2xl mx-auto leading-relaxed"
          >
            Experience the future of AI-powered business solutions
          </motion.p>
        </motion.div>

        {/* Dynamic Blooming Ball */}
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 1, ease: "easeOut" }}
          className="relative mb-16"
        >
          {/* Enhanced Glow Effect - More Vibrant */}
          <motion.div
            className="ball-glow absolute inset-0 bg-gradient-to-r from-yellow-400 via-orange-400 to-yellow-500 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.3, 1.6, 1.3, 1],
              opacity: [0.4, 0.7, 0.9, 0.7, 0.4],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
          
          {/* Additional Outer Glow */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-yellow-300 via-orange-300 to-yellow-400 rounded-full blur-2xl"
            animate={{
              scale: [1, 1.4, 1.8, 1.4, 1],
              opacity: [0.2, 0.5, 0.8, 0.5, 0.2],
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 1,
            }}
          />
          
          {/* Enhanced Main Ball - More Vibrant Yellow */}
          <motion.button
            className="main-ball relative w-32 h-32 bg-gradient-to-br from-yellow-400 via-orange-400 to-yellow-500 rounded-full shadow-2xl cursor-pointer group transition-all duration-300"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onHoverStart={() => setIsHovered(true)}
            onHoverEnd={() => setIsHovered(false)}
            onClick={handleBallClick}
            style={{
              boxShadow: '0 0 40px rgba(245, 158, 11, 0.6), 0 0 80px rgba(245, 158, 11, 0.4), 0 0 120px rgba(245, 158, 11, 0.2)'
            }}
          >
            {/* Enhanced Inner Glow - More Vibrant */}
            <motion.div
              animate={{
                scale: isHovered ? 1.2 : 1,
                rotate: isHovered ? 360 : 0,
                opacity: isHovered ? 0.8 : 0.6,
              }}
              transition={{ duration: 0.5 }}
              className="absolute inset-4 bg-gradient-to-br from-yellow-200/40 via-orange-200/30 to-yellow-300/20 rounded-full"
              style={{
                boxShadow: 'inset 0 0 20px rgba(245, 158, 11, 0.3)'
              }}
            />
            
            {/* Enhanced Icon - Glowing Effect */}
            <motion.div
              animate={{
                scale: isHovered ? 1.3 : 1,
                y: isHovered ? -5 : 0,
                filter: isHovered ? "brightness(1.5) drop-shadow(0 0 10px rgba(255, 255, 255, 0.8))" : "brightness(1)",
              }}
              transition={{ duration: 0.3 }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <Zap className="w-16 h-16 text-white drop-shadow-lg" />
            </motion.div>
            
            {/* Enhanced Pulse Rings - More Vibrant Yellow */}
            <motion.div
              animate={{
                scale: [1, 1.6, 2.2],
                opacity: [0.9, 0.5, 0],
              }}
              transition={{
                duration: 2.5,
                repeat: Infinity,
                ease: "easeOut",
              }}
              className="absolute inset-0 border-3 border-yellow-300 rounded-full"
              style={{
                boxShadow: '0 0 20px rgba(245, 158, 11, 0.4)'
              }}
            />
            
            <motion.div
              animate={{
                scale: [1, 1.4, 1.8],
                opacity: [0.7, 0.3, 0],
              }}
              transition={{
                duration: 2.5,
                repeat: Infinity,
                ease: "easeOut",
                delay: 0.8,
              }}
              className="absolute inset-0 border-3 border-yellow-200 rounded-full"
              style={{
                boxShadow: '0 0 15px rgba(245, 158, 11, 0.3)'
              }}
            />
            
            {/* Third Pulse Ring for More Dynamic Effect */}
            <motion.div
              animate={{
                scale: [1, 1.2, 1.5],
                opacity: [0.5, 0.2, 0],
              }}
              transition={{
                duration: 2.5,
                repeat: Infinity,
                ease: "easeOut",
                delay: 1.2,
              }}
              className="absolute inset-0 border-2 border-yellow-100 rounded-full"
              style={{
                boxShadow: '0 0 10px rgba(245, 158, 11, 0.2)'
              }}
            />
            
            {/* Additional Floating Glow Elements Around Ball */}
            <motion.div
              animate={{
                scale: [1, 1.1, 1],
                opacity: [0.3, 0.6, 0.3],
                rotate: [0, 180, 360],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="absolute -top-8 -left-8 w-6 h-6 bg-yellow-300 rounded-full blur-sm"
              style={{
                boxShadow: '0 0 20px rgba(245, 158, 11, 0.6)'
              }}
            />
            
            <motion.div
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.4, 0.7, 0.4],
                rotate: [360, 180, 0],
              }}
              transition={{
                duration: 3.5,
                repeat: Infinity,
                ease: "easeInOut",
                delay: 1,
              }}
              className="absolute -top-6 -right-6 w-4 h-4 bg-orange-300 rounded-full blur-sm"
              style={{
                boxShadow: '0 0 15px rgba(245, 158, 11, 0.5)'
              }}
            />
            
            <motion.div
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.2, 0.5, 0.2],
                y: [0, -10, 0],
              }}
              transition={{
                duration: 5,
                repeat: Infinity,
                ease: "easeInOut",
                delay: 2,
              }}
              className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-yellow-200 rounded-full blur-sm"
              style={{
                boxShadow: '0 0 10px rgba(245, 158, 11, 0.4)'
              }}
            />
          </motion.button>
          
          {/* Enhanced Hover Text - More Vibrant */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: isHovered ? 1 : 0, y: isHovered ? 0 : 20 }}
            transition={{ duration: 0.3 }}
            className="absolute -bottom-20 left-1/2 transform -translate-x-1/2 text-center"
          >
            <motion.p 
              className="text-yellow-300 text-xl font-bold mb-3 drop-shadow-lg"
              animate={{
                textShadow: isHovered ? "0 0 10px rgba(245, 158, 11, 0.8)" : "0 0 5px rgba(245, 158, 11, 0.4)"
              }}
              transition={{ duration: 0.3 }}
            >
              Click to Start Chat
            </motion.p>
            <motion.div
              animate={{ 
                x: [0, 5, 0],
                scale: isHovered ? 1.05 : 1
              }}
              transition={{ duration: 1, repeat: Infinity }}
              className="inline-flex items-center text-yellow-400 font-medium"
            >
              <ArrowRight className="w-6 h-6 mr-2 drop-shadow-lg" />
              Begin AI Experience
            </motion.div>
            
            {/* Additional Glow Effect Under Text */}
            <motion.div
              animate={{
                opacity: isHovered ? 0.6 : 0,
                scale: isHovered ? 1 : 0.8,
              }}
              transition={{ duration: 0.4 }}
              className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-32 h-1 bg-gradient-to-r from-transparent via-yellow-400 to-transparent rounded-full blur-sm"
            />
          </motion.div>
        </motion.div>

        {/* Feature Highlights */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.5 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
        >
          {[
            {
              icon: <Brain className="w-8 h-8" />,
              title: "AI-Powered",
              description: "Advanced machine learning for intelligent responses"
            },
            {
              icon: <Sparkles className="w-8 h-8" />,
              title: "Real-Time",
              description: "Live data integration and instant updates"
            },
            {
              icon: <Zap className="w-8 h-8" />,
              title: "Lightning Fast",
              description: "Optimized for speed and performance"
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.7 + index * 0.1 }}
              className="text-center p-6 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-all duration-300"
            >
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full mb-4">
                <div className="text-white">
                  {feature.icon}
                </div>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-primary-200">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.div>
    </TransitionManager>
  );
};

export default LandingPage; 