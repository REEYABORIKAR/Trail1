import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('doctalk_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('doctalk_token');
      localStorage.removeItem('doctalk_user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;

// ─── Auth ────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login/json', data),
  me: () => api.get('/auth/me'),
};

// ─── RAG ─────────────────────────────────────────────────────────────────────
export const ragAPI = {
  query: (question) => api.post('/rag/query', { question }),
  ingest: (file) => {
    const form = new FormData();
    form.append('file', file);
    return api.post('/rag/ingest', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  documents: () => api.get('/rag/documents'),
};