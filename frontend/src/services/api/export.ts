import { AxiosInstance } from "axios";

export class ExportService {
  constructor(private api: AxiosInstance) {}

  async exportData(type: string, format: string, params?: any) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.keys(params).forEach((key) => {
        if (params[key] !== undefined && params[key] !== null) {
          queryParams.append(key, params[key].toString());
        }
      });
    }

    const url = queryParams.toString()
      ? `/export/${type}/${format}?${queryParams.toString()}`
      : `/export/${type}/${format}`;
    const response = await this.api.get(url, { responseType: "blob" });
    return response.data;
  }

  async getPowerBIDatasets() {
    const response = await this.api.get("/powerbi/datasets");
    return response.data;
  }

  async getPowerBIData(dataType: string) {
    const response = await this.api.get(`/powerbi/data/${dataType}`);
    return response.data;
  }
}
