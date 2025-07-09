import { AxiosInstance } from "axios";

export class KPIsService {
  constructor(private api: AxiosInstance) {}

  async getKPIsTauxServiceClient() {
    const response = await this.api.get("/kpis/taux-service-client");
    return response.data;
  }

  async getKPIsDelaiMoyenLivraison() {
    const response = await this.api.get("/kpis/delai-moyen-livraison");
    return response.data;
  }

  async getKPIsNombreCommandes() {
    const response = await this.api.get("/kpis/nombre-commandes");
    return response.data;
  }

  async getKPIsCommandesAeriennes() {
    const response = await this.api.get("/kpis/commandes-aeriennes");
    return response.data;
  }

  async getKPIsSynthese() {
    const response = await this.api.get("/kpis/synthese");
    return response.data;
  }
}
