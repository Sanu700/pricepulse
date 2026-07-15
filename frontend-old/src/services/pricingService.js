import api from "../api/axios";

export const getPrices = async () => {
  const response = await api.get("/prices/");
  return response.data;
};