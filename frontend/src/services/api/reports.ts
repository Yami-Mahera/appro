import { AxiosInstance } from "axios";

export class ReportsService {
  constructor(private api: AxiosInstance) {}

  async getFournisseursReport(params?: {
    date_from?: string;
    date_to?: string;
  }) {
    const queryParams = new URLSearchParams();

    if (params?.date_from) queryParams.append("date_from", params.date_from);
    if (params?.date_to) queryParams.append("date_to", params.date_to);

    const url = queryParams.toString()
      ? `/reports/fournisseurs?${queryParams.toString()}`
      : "/reports/fournisseurs";
    const response = await this.api.get(url);
    return response.data;
  }

  async getArticlesReport(params?: { date_from?: string; date_to?: string }) {
    const queryParams = new URLSearchParams();

    if (params?.date_from) queryParams.append("date_from", params.date_from);
    if (params?.date_to) queryParams.append("date_to", params.date_to);

    const url = queryParams.toString()
      ? `/reports/articles?${queryParams.toString()}`
      : "/reports/articles";
    const response = await this.api.get(url);
    return response.data;
  }

  async getCommandesReport(params?: { date_from?: string; date_to?: string }) {
    const queryParams = new URLSearchParams();

    if (params?.date_from) queryParams.append("date_from", params.date_from);
    if (params?.date_to) queryParams.append("date_to", params.date_to);

    const url = queryParams.toString()
      ? `/reports/commandes?${queryParams.toString()}`
      : "/reports/commandes";
    const response = await this.api.get(url);
    return response.data;
  }

  async getSyntheseReport(params?: { date_from?: string; date_to?: string }) {
    console.log(
      "🔍 ReportsService.getSyntheseReport called with params:",
      params
    );
    const queryParams = new URLSearchParams();

    if (params?.date_from) queryParams.append("date_from", params.date_from);
    if (params?.date_to) queryParams.append("date_to", params.date_to);

    const url = queryParams.toString()
      ? `/reports/synthese?${queryParams.toString()}`
      : "/reports/synthese";
    console.log("🌐 Making request to:", url);

    try {
      const response = await this.api.get(url);
      console.log("✅ Synthese API response:", response.data);
      return response.data;
    } catch (error) {
      console.error("❌ Synthese API error:", error);
      throw error;
    }
  }
}
