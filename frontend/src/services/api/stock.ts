import { AxiosInstance } from "axios";

export class StockService {
  constructor(private api: AxiosInstance) {}

  async createMouvementStock(data: any) {
    const response = await this.api.post("/stock/mouvements", data);
    return response.data;
  }

  async getMouvementsStock(articleId: string, limit: number = 100) {
    const response = await this.api.get(
      `/stock/mouvements/${articleId}?limit=${limit}`
    );
    return response.data;
  }

  async getCalculCouverture(articleId: string) {
    const response = await this.api.get(`/stock/couverture/${articleId}`);
    return response.data;
  }

  async getEvolutionStock(articleId: string, semaines: number = 26) {
    const response = await this.api.get(
      `/stock/evolution/${articleId}?semaines=${semaines}`
    );
    return response.data;
  }

  async getAlertesAvancees() {
    const response = await this.api.get("/stock/alertes-avancees");
    return response.data;
  }

  async genererAlertesAvancees() {
    const response = await this.api.post("/stock/generer-alertes");
    return response.data;
  }

  async createPrevisionConsommation(data: any) {
    const response = await this.api.post("/stock/previsions", data);
    return response.data;
  }

  async getPrevisionsConsommation(articleId: string, semaines: number = 26) {
    const response = await this.api.get(
      `/stock/previsions/${articleId}?semaines=${semaines}`
    );
    return response.data;
  }

  async calculerCompositionTC(articlesIds: string[]) {
    const response = await this.api.post("/stock/composition-tc", {
      articles_ids: articlesIds,
    });
    return response.data;
  }

  async getStockCoverageData(articleId: string, semaines: number = 26) {
    const [evolution, couverture, previsions] = await Promise.all([
      this.getEvolutionStock(articleId, semaines),
      this.getCalculCouverture(articleId),
      this.getPrevisionsConsommation(articleId, semaines),
    ]);

    return {
      evolution,
      couverture,
      previsions,
    };
  }
}
