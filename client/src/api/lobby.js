import api from './index';

export const lobbyApi = {
  create: (name, quizId) => api.post('/lobby/create', { name, quiz_id: quizId }),
  join: (token) => api.post(`/lobby/join/${token}`),
  exit: () => api.post('/lobby/exit'),
  run: () => api.post('/lobby/run'),
  getInfo: () => api.get('/lobby/get-info'),
  pollRunning: (token) => api.get(`/lobby/poll-running/${token}`),
  search: (query = '') => api.get('/lobby/search', { params: { query } }),
  compare: (answers) => api.put('/lobby/compare', { answers }),
};

export const quizApi = {
  search: (query = '') => api.get('/quiz/search', { params: { query } }),
};
