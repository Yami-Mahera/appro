import { AxiosInstance } from "axios";

export class UsersService {
  constructor(private api: AxiosInstance) {}

  async getUsers(params?: {
    search?: string;
    sort_by?: string;
    sort_order?: string;
    role?: string;
    active?: boolean;
    limit?: number;
    skip?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append("search", params.search);
    if (params?.sort_by) queryParams.append("sort_by", params.sort_by);
    if (params?.sort_order) queryParams.append("sort_order", params.sort_order);
    if (params?.role) queryParams.append("role", params.role);
    if (params?.active !== undefined)
      queryParams.append("active", params.active.toString());
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.skip) queryParams.append("skip", params.skip.toString());

    const url = queryParams.toString()
      ? `/users?${queryParams.toString()}`
      : "/users";
    const response = await this.api.get(url);
    return response.data;
  }

  async getUser(id: string) {
    const response = await this.api.get(`/users/${id}`);
    return response.data;
  }

  async createUser(data: any) {
    const response = await this.api.post("/users", data);
    return response.data;
  }

  async updateUser(id: string, data: any) {
    const response = await this.api.put(`/users/${id}`, data);
    return response.data;
  }

  async deleteUser(id: string) {
    const response = await this.api.delete(`/users/${id}`);
    return response.data;
  }

  async resetUserPassword(id: string, newPassword: string) {
    const response = await this.api.put(`/users/${id}/reset-password`, {
      new_password: newPassword,
    });
    return response.data;
  }
}
