import React from 'react';
import ReactDOM from 'react-dom/client';
import { Toaster } from 'react-hot-toast';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <>
    <App />
    <Toaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: '#1e293b',
          color: '#fff',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
        success: {
          style: {
            background: '#059669',
            border: '1px solid #10b981',
          },
        },
        error: {
          style: {
            background: '#dc2626',
            border: '1px solid #ef4444',
          },
        },
      }}
    />
  </>
); 