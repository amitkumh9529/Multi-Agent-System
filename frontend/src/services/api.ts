import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor per gestire errori globalmente
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Errore con risposta dal server
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Richiesta fatta ma nessuna risposta
      console.error('Network Error:', error.request);
    } else {
      // Errore nella configurazione della richiesta
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

