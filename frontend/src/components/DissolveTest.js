import React from 'react';
import PureDissolveTransition from './PureDissolveTransition';

const DissolveTest = ({ isVisible, onComplete }) => {
  return (
    <PureDissolveTransition 
      isVisible={isVisible} 
      onTransitionComplete={onComplete}
    >
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
        <div className="text-center text-white">
          <h1 className="text-6xl font-bold mb-4">Pure Dissolve Test</h1>
          <p className="text-xl">This tests ONLY dissolving transitions - NO sliding!</p>
          <div className="mt-8 p-6 bg-white/10 rounded-lg backdrop-blur-sm border border-white/20">
            <p className="text-lg mb-2">Transition Type: Pure Dissolve</p>
            <p className="text-lg mb-2">Status: {isVisible ? 'Visible' : 'Hidden'}</p>
            <p className="text-sm text-purple-200">No horizontal movement - only opacity, scale, and blur</p>
          </div>
        </div>
      </div>
    </PureDissolveTransition>
  );
};

export default DissolveTest; 