import axios from 'axios';
import type {
  User,
  UserLogin,
  UserCreate,
  Token,
  Fournisseur,
  FournisseurCreate,
  Article,
  ArticleCreate,
  Commande,
  CommandeCreate,
  Alerte,
  DashboardStats
} from '../common/types';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: UserLogin): Promise<Token> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: UserCreate): Promise<User> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Fournisseurs API
export const fournisseursAPI = {
  getAll: async (params?: {
    search?: string;
    sort_by?: string;
    sort_order?: string;
    ville?: string;
    pays?: string;
    active?: boolean;
    limit?: number;
    skip?: number;
  }): Promise<Fournisseur[]> => {
    const response = await api.get('/fournisseurs', { params });
    return response.data;
  },

  getById: async (id: string): Promise<Fournisseur> => {
    const response = await api.get(`/fournisseurs/${id}`);
    return response.data;
  },

  create: async (data: FournisseurCreate): Promise<Fournisseur> => {
    const response = await api.post('/fournisseurs', data);
    return response.data;
  },

  update: async (id: string, data: FournisseurCreate): Promise<Fournisseur> => {
    const response = await api.put(`/fournisseurs/${id}`, data);
    return response.data;
  },
};

// Articles API
export const articlesAPI = {
  getAll: async (params?: {
    search?: string;
    sort_by?: string;
    sort_order?: string;
    famille?: string;
    fournisseur_id?: string;
    stock_bas?: boolean;
    active?: boolean;
    limit?: number;
    skip?: number;
  }): Promise<Article[]> => {
    const response = await api.get('/articles', { params });
    return response.data;
  },

  getById: async (id: string): Promise<Article> => {
    const response = await api.get(`/articles/${id}`);
    return response.data;
  },

  create: async (data: ArticleCreate): Promise<Article> => {
    const response = await api.post('/articles', data);
    return response.data;
  },

  update: async (id: string, data: ArticleCreate): Promise<Article> => {
    const response = await api.put(`/articles/${id}`, data);
    return response.data;
  },

  getStockBas: async (): Promise<Article[]> => {
    const response = await api.get('/articles/stock-bas');
    return response.data;
  },
};

// Commandes API
export const commandesAPI = {
  getAll: async (params?: {
    search?: string;
    sort_by?: string;
    sort_order?: string;
    status?: string;
    fournisseur_id?: string;
    date_from?: string;
    date_to?: string;
    limit?: number;
    skip?: number;
  }): Promise<Commande[]> => {
    const response = await api.get('/commandes', { params });
    return response.data;
  },

  getById: async (id: string): Promise<Commande> => {
    const response = await api.get(`/commandes/${id}`);
    return response.data;
  },

  create: async (data: CommandeCreate): Promise<Commande> => {
    const response = await api.post('/commandes', data);
    return response.data;
  },

  update: async (id: string, data: Partial<Commande>): Promise<Commande> => {
    const response = await api.put(`/commandes/${id}`, data);
    return response.data;
  },
};

// Alertes API
export const alertesAPI = {
  getAll: async (params?: { lue?: boolean }): Promise<Alerte[]> => {
    const response = await api.get('/alertes', { params });
    return response.data;
  },

  marquerLue: async (id: string): Promise<{ message: string }> => {
    const response = await api.put(`/alertes/${id}/marquer-lue`);
    return response.data;
  },

  createTest: async (data: any): Promise<Alerte> => {
    const response = await api.post('/alertes/test-create', data);
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
};

// Reports API
export const reportsAPI = {
  getFournisseurs: async (params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<any[]> => {
    const response = await api.get('/reports/fournisseurs', { params });
    return response.data;
  },

  getArticles: async (params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<any[]> => {
    const response = await api.get('/reports/articles', { params });
    return response.data;
  },

  getCommandes: async (params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<any[]> => {
    const response = await api.get('/reports/commandes', { params });
    return response.data;
  },

  getSynthese: async (params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<any> => {
    const response = await api.get('/reports/synthese', { params });
    return response.data;
  },
};

export default api;