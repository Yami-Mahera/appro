import { AxiosInstance } from "axios";

export class VariationsService {
  constructor(private api: AxiosInstance) {}

  async getEcartsAnalyse(params?: { type_ecart?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.type_ecart) queryParams.append("type_ecart", params.type_ecart);

    const url = queryParams.toString()
      ? `/variations/ecarts?${queryParams.toString()}`
      : "/variations/ecarts";
    const response = await this.api.get(url);
    return response.data;
  }

  async getPrevisionsVsRealisations(articleId: string) {
    const response = await this.api.get(
      `/variations/previsions-vs-realisations/${articleId}`
    );
    return response.data;
  }
}
