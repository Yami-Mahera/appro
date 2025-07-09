import { AxiosInstance } from "axios";

export class ArticlesService {
  constructor(private api: AxiosInstance) {}

  async getArticles(params?: {
    search?: string;
    sort_by?: string;
    sort_order?: string;
    famille?: string;
    fournisseur_id?: string;
    stock_bas?: boolean;
    active?: boolean;
    limit?: number;
    skip?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append("search", params.search);
    if (params?.sort_by) queryParams.append("sort_by", params.sort_by);
    if (params?.sort_order) queryParams.append("sort_order", params.sort_order);
    if (params?.famille) queryParams.append("famille", params.famille);
    if (params?.fournisseur_id)
      queryParams.append("fournisseur_id", params.fournisseur_id);
    if (params?.stock_bas !== undefined)
      queryParams.append("stock_bas", params.stock_bas.toString());
    if (params?.active !== undefined)
      queryParams.append("active", params.active.toString());
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.skip) queryParams.append("skip", params.skip.toString());

    const url = queryParams.toString()
      ? `/articles?${queryParams.toString()}`
      : "/articles";
    const response = await this.api.get(url);
    return response.data;
  }

  async getArticle(id: string) {
    const response = await this.api.get(`/articles/${id}`);
    return response.data;
  }

  async createArticle(data: any) {
    const response = await this.api.post("/articles", data);
    return response.data;
  }

  async updateArticle(id: string, data: any) {
    const response = await this.api.put(`/articles/${id}`, data);
    return response.data;
  }

  async getArticlesStockBas() {
    const response = await this.api.get("/articles/stock-bas");
    return response.data;
  }
}
