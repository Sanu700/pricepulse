import api from "../api/axios";

export async function login(credentials) {
  const response = await api.post("/accounts/login/", credentials);
  return response.data;
}