import axios, { AxiosInstance } from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE_URL = `${BACKEND_URL}/api`;

export const createApiInstance = (): AxiosInstance => {
  const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Add auth interceptor
  api.interceptors.request.use((config) => {
    const token = localStorage.getItem("auth_token");
    console.log("🔑 Token from localStorage:", token ? "EXISTS" : "NOT FOUND");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log("🔑 Authorization header set");
    } else {
      console.warn("⚠️ No token found in localStorage");
    }
    return config;
  });

  // Add response interceptor for error handling
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("user_data");
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }
  );

  return api;
};
