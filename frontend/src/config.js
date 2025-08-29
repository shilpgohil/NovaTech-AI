// Backend configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://novatech-ai-p1ar.onrender.com';
export const WS_URL = (process.env.REACT_APP_API_URL || 'https://novatech-ai-p1ar.onrender.com').replace('https://', 'wss://') + '/ws';

// Environment-specific configuration
export const config = {
  apiBaseUrl: API_BASE_URL,
  wsUrl: WS_URL,
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production'
}; 