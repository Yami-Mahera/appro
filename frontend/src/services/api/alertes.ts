import { AxiosInstance } from "axios";

export class AlertesService {
  constructor(private api: AxiosInstance) {}

  async getAlertes(lue?: boolean) {
    const params = lue !== undefined ? `?lue=${lue}` : "";
    const response = await this.api.get(`/alertes${params}`);
    return response.data;
  }

  async marquerAlerteLue(id: string) {
    const response = await this.api.put(`/alertes/${id}/marquer-lue`);
    return response.data;
  }
}
