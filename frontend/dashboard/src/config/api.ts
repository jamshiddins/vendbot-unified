import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v2`,
  headers: {
    'Content-Type': 'application/json',
    'channel': 'web'
  }
});

// Interceptor для обработки ошибок
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Перенаправляем на логин
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);