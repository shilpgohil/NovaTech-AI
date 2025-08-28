import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const ParticleTest = () => {
  const [stars, setStars] = useState([]);

  useEffect(() => {
    // Create realistic space starfield with different star layers for parallax effect
    const starLayers = [
      { count: 150, size: 1, speed: 0.5, opacity: 0.8, color: 'white' },      // Distant stars (slow, small)
      { count: 100, size: 1.5, speed: 1, opacity: 0.9, color: 'yellow' },     // Medium stars (medium speed)
      { count: 60, size: 2, speed: 1.5, opacity: 1, color: 'yellow' },         // Closer stars (faster)
      { count: 30, size: 2.5, speed: 2, opacity: 1, color: 'orange' },         // Near stars (fastest)
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 relative overflow-hidden">
      <div className="absolute inset-0 flex items-center justify-center text-white text-4xl font-bold z-20">
        Particle Test - Space Starfield Effect
      </div>
      
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
    </div>
  );
};

export default ParticleTest; 