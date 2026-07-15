import api from "../api/axios";

export async function login(credentials) {
  const response = await api.post("/accounts/login/", credentials);
  return response.data;
}

export async function register(payload) {
  const response = await api.post("/accounts/register/", payload);
  return response.data;
}

export async function getProfile() {
  const response = await api.get("/accounts/profile/");
  return response.data;
}

export async function createPriceAlert(payload) {
  const response = await api.post("/alerts/", payload);
  return response.data;
}

export async function getNotifications() {
  const response = await api.get("/notifications/");
  return response.data;
}

export async function getNotificationStatus() {
  const response = await api.get("/notifications/status/");
  return response.data;
}
