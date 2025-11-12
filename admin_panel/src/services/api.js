import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

let authToken = null;

api.setToken = (token) => {
  authToken = token;
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// Load token from localStorage on initialization
const savedToken = localStorage.getItem('token');
if (savedToken) {
  api.setToken(savedToken);
}

export default api;

