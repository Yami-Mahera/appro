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
      console.log('🔑 Token from localStorage:', token ? 'EXISTS' : 'NOT FOUND');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('🔑 Authorization header set');
      } else {
        console.warn('⚠️ No token found in localStorage');
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

  // Users management methods
  async getUsers(params?: {
    search?: string;
    sort_by?: string;
    sort_order?: string;
    role?: string;
    active?: boolean;
    limit?: number;
    skip?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append('search', params.search);
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order);
    if (params?.role) queryParams.append('role', params.role);
    if (params?.active !== undefined) queryParams.append('active', params.active.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    
    const url = queryParams.toString() ? `/users?${queryParams.toString()}` : '/users';
    const response = await this.api.get(url);
    return response.data;
  }

  async getUser(id: string) {
    const response = await this.api.get(`/users/${id}`);
    return response.data;
  }

  async createUser(data: any) {
    const response = await this.api.post('/users', data);
    return response.data;
  }

  async updateUser(id: string, data: any) {
    const response = await this.api.put(`/users/${id}`, data);
    return response.data;
  }

  async deleteUser(id: string) {
    const response = await this.api.delete(`/users/${id}`);
    return response.data;
  }

  async resetUserPassword(id: string, newPassword: string) {
    const response = await this.api.put(`/users/${id}/reset-password`, { new_password: newPassword });
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
  async getCommandes(params?: {
    search?: string;
    sort_by?: string;
    sort_order?: string;
    status?: string;
    fournisseur_id?: string;
    date_from?: string;
    date_to?: string;
    limit?: number;
    skip?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append('search', params.search);
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params?.sort_order) queryParams.append('sort_order', params.sort_order);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.fournisseur_id) queryParams.append('fournisseur_id', params.fournisseur_id);
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    
    const url = queryParams.toString() ? `/commandes?${queryParams.toString()}` : '/commandes';
    const response = await this.api.get(url);
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

  // Reports methods
  async getFournisseursReport(params?: { date_from?: string; date_to?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);
    
    const url = queryParams.toString() ? `/api/reports/fournisseurs?${queryParams.toString()}` : '/api/reports/fournisseurs';
    const response = await this.api.get(url);
    return response.data;
  }

  async getArticlesReport(params?: { date_from?: string; date_to?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);
    
    const url = queryParams.toString() ? `/api/reports/articles?${queryParams.toString()}` : '/api/reports/articles';
    const response = await this.api.get(url);
    return response.data;
  }

  async getCommandesReport(params?: { date_from?: string; date_to?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);
    
    const url = queryParams.toString() ? `/api/reports/commandes?${queryParams.toString()}` : '/api/reports/commandes';
    const response = await this.api.get(url);
    return response.data;
  }

  async getSyntheseReport(params?: { date_from?: string; date_to?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);
    
    const url = queryParams.toString() ? `/api/reports/synthese?${queryParams.toString()}` : '/api/reports/synthese';
    const response = await this.api.get(url);
    return response.data;
  }

  // Méthodes pour la gestion avancée des stocks

  async createMouvementStock(data: any) {
    const response = await this.api.post('/stock/mouvements', data);
    return response.data;
  }

  async getMouvementsStock(articleId: string, limit: number = 100) {
    const response = await this.api.get(`/stock/mouvements/${articleId}?limit=${limit}`);
    return response.data;
  }

  async getCalculCouverture(articleId: string) {
    const response = await this.api.get(`/stock/couverture/${articleId}`);
    return response.data;
  }

  async getEvolutionStock(articleId: string, semaines: number = 26) {
    const response = await this.api.get(`/stock/evolution/${articleId}?semaines=${semaines}`);
    return response.data;
  }

  async getAlertesAvancees() {
    const response = await this.api.get('/stock/alertes-avancees');
    return response.data;
  }

  async genererAlertesAvancees() {
    const response = await this.api.post('/stock/generer-alertes');
    return response.data;
  }

  async createPrevisionConsommation(data: any) {
    const response = await this.api.post('/stock/previsions', data);
    return response.data;
  }

  async getPrevisionsConsommation(articleId: string, semaines: number = 26) {
    const response = await this.api.get(`/stock/previsions/${articleId}?semaines=${semaines}`);
    return response.data;
  }

  async calculerCompositionTC(articlesIds: string[]) {
    const response = await this.api.post('/stock/composition-tc', { articles_ids: articlesIds });
    return response.data;
  }

  async getStockCoverageData(articleId: string, semaines: number = 26) {
    // Cette méthode combine plusieurs appels pour récupérer toutes les données nécessaires au graphique
    const [evolution, couverture, previsions] = await Promise.all([
      this.getEvolutionStock(articleId, semaines),
      this.getCalculCouverture(articleId),
      this.getPrevisionsConsommation(articleId, semaines)
    ]);

    return {
      evolution,
      couverture,
      previsions
    };
  }

  // Nouvelles méthodes pour les tableaux de gestion des stocks

  async validateCommandeAvancee(data: any) {
    const response = await this.api.post('/commandes/validation-avancee', data);
    return response.data;
  }

  async getKPIsTauxServiceClient() {
    const response = await this.api.get('/kpis/taux-service-client');
    return response.data;
  }

  async getKPIsDelaiMoyenLivraison() {
    const response = await this.api.get('/kpis/delai-moyen-livraison');
    return response.data;
  }

  async getKPIsNombreCommandes() {
    const response = await this.api.get('/kpis/nombre-commandes');
    return response.data;
  }

  async getKPIsCommandesAeriennes() {
    const response = await this.api.get('/kpis/commandes-aeriennes');
    return response.data;
  }

  async getKPIsSynthese() {
    const response = await this.api.get('/kpis/synthese');
    return response.data;
  }

  async getEcartsAnalyse(params?: { type_ecart?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.type_ecart) queryParams.append('type_ecart', params.type_ecart);
    
    const url = queryParams.toString() ? `/variations/ecarts?${queryParams.toString()}` : '/variations/ecarts';
    const response = await this.api.get(url);
    return response.data;
  }

  async getPrevisionsVsRealisations(articleId: string) {
    const response = await this.api.get(`/variations/previsions-vs-realisations/${articleId}`);
    return response.data;
  }

  async createDashboardPersonnalise(data: any) {
    const response = await this.api.post('/dashboards/personnalises', data);
    return response.data;
  }

  async getDashboardsPersonnalises() {
    const response = await this.api.get('/dashboards/personnalises');
    return response.data;
  }

  async updateDashboardPersonnalise(id: string, data: any) {
    const response = await this.api.put(`/dashboards/personnalises/${id}`, data);
    return response.data;
  }

  async deleteDashboardPersonnalise(id: string) {
    const response = await this.api.delete(`/dashboards/personnalises/${id}`);
    return response.data;
  }

  async getWidgetsDisponibles() {
    const response = await this.api.get('/dashboards/widgets-disponibles');
    return response.data.widgets || [];
  }

  async exportData(type: string, format: string, params?: any) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
          queryParams.append(key, params[key].toString());
        }
      });
    }
    
    const url = queryParams.toString() ? `/export/${type}/${format}?${queryParams.toString()}` : `/export/${type}/${format}`;
    const response = await this.api.get(url, { responseType: 'blob' });
    return response.data;
  }

  async getPowerBIDatasets() {
    const response = await this.api.get('/powerbi/datasets');
    return response.data;
  }

  async getPowerBIData(dataType: string) {
    const response = await this.api.get(`/powerbi/data/${dataType}`);
    return response.data;
  }
}

export default new ApiService();