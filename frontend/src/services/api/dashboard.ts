import { AxiosInstance } from "axios";

export class DashboardService {
  constructor(private api: AxiosInstance) {}

  async getDashboardStats() {
    const response = await this.api.get("/dashboard/stats");
    return response.data;
  }

  async createDashboardPersonnalise(data: any) {
    const response = await this.api.post("/dashboards/personnalises", data);
    return response.data;
  }

  async getDashboardsPersonnalises() {
    const response = await this.api.get("/dashboards/personnalises");
    return response.data;
  }

  async updateDashboardPersonnalise(id: string, data: any) {
    const response = await this.api.put(
      `/dashboards/personnalises/${id}`,
      data
    );
    return response.data;
  }

  async deleteDashboardPersonnalise(id: string) {
    const response = await this.api.delete(`/dashboards/personnalises/${id}`);
    return response.data;
  }

  async getWidgetsDisponibles() {
    const response = await this.api.get("/dashboards/widgets-disponibles");
    return response.data.widgets || [];
  }
}
