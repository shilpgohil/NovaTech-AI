// Backend configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const WS_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8000').replace('http://', 'ws://') + '/ws';

// Environment-specific configuration
export const config = {
  apiBaseUrl: API_BASE_URL,
  wsUrl: WS_URL,
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production'
}; 