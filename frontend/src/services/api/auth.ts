import { AxiosInstance } from "axios";

export class AuthService {
  constructor(private api: AxiosInstance) {}

  async login(email: string, password: string) {
    const response = await this.api.post("/auth/login", { email, password });
    return response.data;
  }

  async register(userData: any) {
    const response = await this.api.post("/auth/register", userData);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.api.get("/auth/me");
    return response.data;
  }
}
