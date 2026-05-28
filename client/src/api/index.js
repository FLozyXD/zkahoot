import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// перед каждым запросом проверяем токен в localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Unauthorized => Забываем про токен, логин и айди
api.interceptors.response.use(
  response => { return response; },
  error => {
    if (error.response.status !== 401)
      return error;
    localStorage.clear();
  },
);

export default api;
