import api from "../api/axios";

export async function getProducts() {
    const response = await api.get("/products/");
    return response.data.results;
}

export async function getProduct(id) {
    const response = await api.get(`/products/${id}/`);
    return response.data;
}

export async function getProductPrices(id) {
    const response = await api.get(`/products/${id}/prices/`);
    return response.data;
}