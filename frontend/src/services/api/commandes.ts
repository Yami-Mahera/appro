import { AxiosInstance } from "axios";

export class CommandesService {
  constructor(private api: AxiosInstance) {}

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
    if (params?.search) queryParams.append("search", params.search);
    if (params?.sort_by) queryParams.append("sort_by", params.sort_by);
    if (params?.sort_order) queryParams.append("sort_order", params.sort_order);
    if (params?.status) queryParams.append("status", params.status);
    if (params?.fournisseur_id)
      queryParams.append("fournisseur_id", params.fournisseur_id);
    if (params?.date_from) queryParams.append("date_from", params.date_from);
    if (params?.date_to) queryParams.append("date_to", params.date_to);
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.skip) queryParams.append("skip", params.skip.toString());

    const url = queryParams.toString()
      ? `/commandes?${queryParams.toString()}`
      : "/commandes";
    const response = await this.api.get(url);
    return response.data;
  }

  async getCommande(id: string) {
    const response = await this.api.get(`/commandes/${id}`);
    return response.data;
  }

  async createCommande(data: any) {
    const response = await this.api.post("/commandes", data);
    return response.data;
  }

  async updateCommande(id: string, data: any) {
    const response = await this.api.put(`/commandes/${id}`, data);
    return response.data;
  }

  async validateCommandeAvancee(data: any) {
    const response = await this.api.post("/commandes/validation-avancee", data);
    return response.data;
  }
}
