import React from 'react';
import TransitionManager from './TransitionManager';

const TransitionTest = ({ isVisible, onComplete }) => {
  return (
    <TransitionManager 
      isVisible={isVisible} 
      onTransitionComplete={onComplete}
      transitionType="dissolve"
    >
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900 flex items-center justify-center">
        <div className="text-center text-white">
          <h1 className="text-6xl font-bold mb-4">Transition Test</h1>
          <p className="text-xl">This page tests the dissolving transition effect</p>
          <div className="mt-8 p-4 bg-white/10 rounded-lg backdrop-blur-sm">
            <p>Transition Type: Dissolve</p>
            <p>Status: {isVisible ? 'Visible' : 'Hidden'}</p>
          </div>
        </div>
      </div>
    </TransitionManager>
  );
};

export default TransitionTest; 