import axios from 'axios';

export const api = axios.create({
  baseURL: '/', 
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true', 
  },
});

// Автоматическая подстановка токена перед каждым запросом
api.interceptors.request.use((config) => {
  const token = 'СЮДА JWT ТОКЕН ВЪЕБИ'; 
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});