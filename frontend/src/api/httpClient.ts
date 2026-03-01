import axios from 'axios';

// Get token from cookie manually since it is not HttpOnly
function getCookie(name: string) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift();
}

export const authClient = axios.create({
  baseURL: import.meta.env.VITE_AUTH_URL || 'http://localhost:3000',
  withCredentials: true,
});

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
});

apiClient.interceptors.request.use((config) => {
  const token = getCookie('medgraph_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
