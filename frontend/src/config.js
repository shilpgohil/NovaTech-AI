// Backend configuration
export const API_BASE_URL = 'https://novaai-x0rx.onrender.com';
export const WS_URL = 'wss://novaai-x0rx.onrender.com/ws';

// Environment-specific configuration
export const config = {
  apiBaseUrl: API_BASE_URL,
  wsUrl: WS_URL,
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production'
}; 