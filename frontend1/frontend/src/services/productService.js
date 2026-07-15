import api from "../api/axios";

function unwrapList(data) {
  if (Array.isArray(data)) return data;
  if (data?.results && Array.isArray(data.results)) return data.results;
  if (data?.prices && Array.isArray(data.prices)) return data.prices;
  return [];
}

export async function getProducts(params = {}) {
  const response = await api.get("/products/", {
    params: { page_size: 48, ...params },
  });
  return unwrapList(response.data);
}

export async function getProduct(id) {
  const response = await api.get(`/products/${id}/`);
  return response.data;
}

export async function getProductPrices(id) {
  try {
    const response = await api.get(`/products/${id}/prices/`);
    const data = response.data;
    if (Array.isArray(data?.prices)) return data.prices;
    return unwrapList(data);
  } catch {
    const response = await api.get(`/prices/product/${id}/`);
    return unwrapList(response.data);
  }
}

export async function getProductHistory(id, params = {}) {
  const response = await api.get(`/products/${id}/history/`, { params });
  return unwrapList(response.data);
}

export async function getProductStats(id) {
  const response = await api.get(`/products/${id}/stats/`);
  return response.data;
}

export async function searchSuggestions(query) {
  if (!query?.trim()) return [];
  const response = await api.get("/products/", {
    params: { search: query, page_size: 6 },
  });
  return unwrapList(response.data).slice(0, 6);
}
