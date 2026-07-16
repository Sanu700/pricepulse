import api from "../api/axios";

export async function getStores() {
  const response = await api.get("/stores/");
  return Array.isArray(response.data) ? response.data : response.data?.results ?? [];
}

export async function getAnalyticsSummary() {
  const response = await api.get("/analytics/summary/");
  return response.data;
}
