import { AxiosInstance } from "axios";

export class FournisseursService {
  constructor(private api: AxiosInstance) {}

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
    if (params?.search) queryParams.append("search", params.search);
    if (params?.sort_by) queryParams.append("sort_by", params.sort_by);
    if (params?.sort_order) queryParams.append("sort_order", params.sort_order);
    if (params?.ville) queryParams.append("ville", params.ville);
    if (params?.pays) queryParams.append("pays", params.pays);
    if (params?.active !== undefined)
      queryParams.append("active", params.active.toString());
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.skip) queryParams.append("skip", params.skip.toString());

    const url = queryParams.toString()
      ? `/fournisseurs?${queryParams.toString()}`
      : "/fournisseurs";
    const response = await this.api.get(url);
    return response.data;
  }

  async getFournisseur(id: string) {
    const response = await this.api.get(`/fournisseurs/${id}`);
    return response.data;
  }

  async createFournisseur(data: any) {
    const response = await this.api.post("/fournisseurs", data);
    return response.data;
  }

  async updateFournisseur(id: string, data: any) {
    const response = await this.api.put(`/fournisseurs/${id}`, data);
    return response.data;
  }
}
