/**
 * Serviço de autenticação e chamadas HTTP do IntegraOCI standalone.
 *
 * Replica as funcionalidades essenciais do authService do Portal-SCCS:
 * - Instância axios com CSRF e JWT automáticos
 * - Exportação de `api` (instância) e `fetchCSRFToken`
 */

import axios from 'axios';

const API_BASE = process.env.VUE_APP_API_URL || 'http://localhost:8000';

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : null;
}

const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
});

// Injeta CSRF token e JWT em todas as requisições
api.interceptors.request.use((config) => {
  const csrfToken = getCookie('csrftoken');
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  const jwtToken = getCookie('access_token');
  if (jwtToken) {
    config.headers['Authorization'] = `Bearer ${jwtToken}`;
  }
  return config;
});

// Tenta renovar o token automaticamente em caso de 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        await axios.post(`${API_BASE}/api/v1/auth/refresh/`, {}, { withCredentials: true });
        return api(originalRequest);
      } catch (_) {
        // Token inválido — redireciona para login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

/**
 * Garante que o cookie CSRF esteja disponível antes de requisições POST.
 * No IntegraOCI standalone o cookie é emitido automaticamente pelo Django
 * no primeiro request GET; esta função faz um ping para garantir isso.
 */
export async function fetchCSRFToken() {
  try {
    await api.get('/api/v1/auth/user/');
  } catch (_) {
    // ignora — o objetivo é apenas obter o cookie
  }
}

export default api;
