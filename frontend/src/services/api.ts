import axios, { AxiosInstance, AxiosResponse } from 'axios';
import createAuthRefreshInterceptor from 'axios-auth-refresh';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE_URL = `${BACKEND_URL}/api`;

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth interceptor
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_data');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async login(email: string, password: string) {
    const response = await this.api.post('/auth/login', { email, password });
    return response.data;
  }

  async register(userData: any) {
    const response = await this.api.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.api.get('/auth/me');
    return response.data;
  }

  // Fournisseurs methods
  async getFournisseurs(params?: {
    search?: string;
    sort_by?: string;
    sort_order?: string;
    ville?: string;
    pays?: string;
    active?: boolean;
    limit?: number;
    skip?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append('search', params.search);
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order);
    if (params?.ville) queryParams.append('ville', params.ville);
    if (params?.pays) queryParams.append('pays', params.pays);
    if (params?.active !== undefined) queryParams.append('active', params.active.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    
    const url = queryParams.toString() ? `/fournisseurs?${queryParams.toString()}` : '/fournisseurs';
    const response = await this.api.get(url);
    return response.data;
  }

  async getFournisseur(id: string) {
    const response = await this.api.get(`/fournisseurs/${id}`);
    return response.data;
  }

  async createFournisseur(data: any) {
    const response = await this.api.post('/fournisseurs', data);
    return response.data;
  }

  async updateFournisseur(id: string, data: any) {
    const response = await this.api.put(`/fournisseurs/${id}`, data);
    return response.data;
  }

  // Articles methods
  async getArticles(params?: {
    search?: string;
    sort_by?: string;
    sort_order?: string;
    famille?: string;
    fournisseur_id?: string;
    stock_bas?: boolean;
    active?: boolean;
    limit?: number;
    skip?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append('search', params.search);
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order);
    if (params?.famille) queryParams.append('famille', params.famille);
    if (params?.fournisseur_id) queryParams.append('fournisseur_id', params.fournisseur_id);
    if (params?.stock_bas !== undefined) queryParams.append('stock_bas', params.stock_bas.toString());
    if (params?.active !== undefined) queryParams.append('active', params.active.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    
    const url = queryParams.toString() ? `/articles?${queryParams.toString()}` : '/articles';
    const response = await this.api.get(url);
    return response.data;
  }

  async getArticle(id: string) {
    const response = await this.api.get(`/articles/${id}`);
    return response.data;
  }

  async createArticle(data: any) {
    const response = await this.api.post('/articles', data);
    return response.data;
  }

  async updateArticle(id: string, data: any) {
    const response = await this.api.put(`/articles/${id}`, data);
    return response.data;
  }

  async getArticlesStockBas() {
    const response = await this.api.get('/articles/stock-bas');
    return response.data;
  }

  // Commandes methods
  async getCommandes(status?: string) {
    const params = status ? `?status=${status}` : '';
    const response = await this.api.get(`/commandes${params}`);
    return response.data;
  }

  async getCommande(id: string) {
    const response = await this.api.get(`/commandes/${id}`);
    return response.data;
  }

  async createCommande(data: any) {
    const response = await this.api.post('/commandes', data);
    return response.data;
  }

  async updateCommande(id: string, data: any) {
    const response = await this.api.put(`/commandes/${id}`, data);
    return response.data;
  }

  // Alertes methods
  async getAlertes(lue?: boolean) {
    const params = lue !== undefined ? `?lue=${lue}` : '';
    const response = await this.api.get(`/alertes${params}`);
    return response.data;
  }

  async marquerAlerteLue(id: string) {
    const response = await this.api.put(`/alertes/${id}/marquer-lue`);
    return response.data;
  }

  // Dashboard methods
  async getDashboardStats() {
    const response = await this.api.get('/dashboard/stats');
    return response.data;
  }
}

export default new ApiService();