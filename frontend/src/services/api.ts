import { createApiInstance } from "./api/config";
import { AuthService } from "./api/auth";
import { UsersService } from "./api/users";
import { FournisseursService } from "./api/fournisseurs";
import { ArticlesService } from "./api/articles";
import { CommandesService } from "./api/commandes";
import { StockService } from "./api/stock";
import { AlertesService } from "./api/alertes";
import { ReportsService } from "./api/reports";
import { DashboardService } from "./api/dashboard";
import { KPIsService } from "./api/kpis";
import { VariationsService } from "./api/variations";
import { ExportService } from "./api/export";

class ApiService {
  private api = createApiInstance();

  // Services
  public auth = new AuthService(this.api);
  public users = new UsersService(this.api);
  public fournisseurs = new FournisseursService(this.api);
  public articles = new ArticlesService(this.api);
  public commandes = new CommandesService(this.api);
  public stock = new StockService(this.api);
  public alertes = new AlertesService(this.api);
  public reports = new ReportsService(this.api);
  public dashboard = new DashboardService(this.api);
  public kpis = new KPIsService(this.api);
  public variations = new VariationsService(this.api);
  public export = new ExportService(this.api);

  // Méthodes de compatibilité pour maintenir l'API existante
  async login(email: string, password: string) {
    return this.auth.login(email, password);
  }

  async register(userData: any) {
    return this.auth.register(userData);
  }

  async getCurrentUser() {
    return this.auth.getCurrentUser();
  }

  async getUsers(params?: any) {
    return this.users.getUsers(params);
  }

  async getUser(id: string) {
    return this.users.getUser(id);
  }

  async createUser(data: any) {
    return this.users.createUser(data);
  }

  async updateUser(id: string, data: any) {
    return this.users.updateUser(id, data);
  }

  async deleteUser(id: string) {
    return this.users.deleteUser(id);
  }

  async resetUserPassword(id: string, newPassword: string) {
    return this.users.resetUserPassword(id, newPassword);
  }

  async getFournisseurs(params?: any) {
    return this.fournisseurs.getFournisseurs(params);
  }

  async getFournisseur(id: string) {
    return this.fournisseurs.getFournisseur(id);
  }

  async createFournisseur(data: any) {
    return this.fournisseurs.createFournisseur(data);
  }

  async updateFournisseur(id: string, data: any) {
    return this.fournisseurs.updateFournisseur(id, data);
  }

  async getArticles(params?: any) {
    return this.articles.getArticles(params);
  }

  async getArticle(id: string) {
    return this.articles.getArticle(id);
  }

  async createArticle(data: any) {
    return this.articles.createArticle(data);
  }

  async updateArticle(id: string, data: any) {
    return this.articles.updateArticle(id, data);
  }

  async getArticlesStockBas() {
    return this.articles.getArticlesStockBas();
  }

  async getCommandes(params?: any) {
    return this.commandes.getCommandes(params);
  }

  async getCommande(id: string) {
    return this.commandes.getCommande(id);
  }

  async createCommande(data: any) {
    return this.commandes.createCommande(data);
  }

  async updateCommande(id: string, data: any) {
    return this.commandes.updateCommande(id, data);
  }
  async getAlertes(lue?: boolean) {
    return this.alertes.getAlertes(lue);
  }

  async marquerAlerteLue(id: string) {
    return this.alertes.marquerAlerteLue(id);
  }

  async getDashboardStats() {
    return this.dashboard.getDashboardStats();
  }

  async getFournisseursReport(params?: any) {
    return this.reports.getFournisseursReport(params);
  }

  async getArticlesReport(params?: any) {
    return this.reports.getArticlesReport(params);
  }

  async getCommandesReport(params?: any) {
    return this.reports.getCommandesReport(params);
  }

  async getSyntheseReport(params?: any) {
    return this.reports.getSyntheseReport(params);
  }

  async createMouvementStock(data: any) {
    return this.stock.createMouvementStock(data);
  }

  async getMouvementsStock(articleId: string, limit: number = 100) {
    return this.stock.getMouvementsStock(articleId, limit);
  }

  async getCalculCouverture(articleId: string) {
    return this.stock.getCalculCouverture(articleId);
  }

  async getEvolutionStock(articleId: string, semaines: number = 26) {
    return this.stock.getEvolutionStock(articleId, semaines);
  }

  async getAlertesAvancees() {
    return this.stock.getAlertesAvancees();
  }

  async genererAlertesAvancees() {
    return this.stock.genererAlertesAvancees();
  }

  async createPrevisionConsommation(data: any) {
    return this.stock.createPrevisionConsommation(data);
  }

  async getPrevisionsConsommation(articleId: string, semaines: number = 26) {
    return this.stock.getPrevisionsConsommation(articleId, semaines);
  }

  async calculerCompositionTC(articlesIds: string[]) {
    return this.stock.calculerCompositionTC(articlesIds);
  }

  async getStockCoverageData(articleId: string, semaines: number = 26) {
    return this.stock.getStockCoverageData(articleId, semaines);
  }

  async validateCommandeAvancee(data: any) {
    return this.commandes.validateCommandeAvancee(data);
  }

  async getKPIsTauxServiceClient() {
    return this.kpis.getKPIsTauxServiceClient();
  }

  async getKPIsDelaiMoyenLivraison() {
    return this.kpis.getKPIsDelaiMoyenLivraison();
  }

  async getKPIsNombreCommandes() {
    return this.kpis.getKPIsNombreCommandes();
  }

  async getKPIsCommandesAeriennes() {
    return this.kpis.getKPIsCommandesAeriennes();
  }

  async getKPIsSynthese() {
    return this.kpis.getKPIsSynthese();
  }

  async getEcartsAnalyse(params?: any) {
    return this.variations.getEcartsAnalyse(params);
  }

  async getPrevisionsVsRealisations(articleId: string) {
    return this.variations.getPrevisionsVsRealisations(articleId);
  }

  async createDashboardPersonnalise(data: any) {
    return this.dashboard.createDashboardPersonnalise(data);
  }

  async getDashboardsPersonnalises() {
    return this.dashboard.getDashboardsPersonnalises();
  }

  async updateDashboardPersonnalise(id: string, data: any) {
    return this.dashboard.updateDashboardPersonnalise(id, data);
  }

  async deleteDashboardPersonnalise(id: string) {
    return this.dashboard.deleteDashboardPersonnalise(id);
  }

  async getWidgetsDisponibles() {
    return this.dashboard.getWidgetsDisponibles();
  }

  async exportData(type: string, format: string, params?: any) {
    return this.export.exportData(type, format, params);
  }

  async getPowerBIDatasets() {
    return this.export.getPowerBIDatasets();
  }

  async getPowerBIData(dataType: string) {
    return this.export.getPowerBIData(dataType);
  }
}

export default new ApiService();
