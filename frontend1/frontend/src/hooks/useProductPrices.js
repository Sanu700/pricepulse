import { useQuery } from "@tanstack/react-query";
import { getProductPrices, getProductStats } from "../services/productService";

export function useProductPrices(id) {
  return useQuery({
    queryKey: ["product-prices", id],
    queryFn: () => getProductPrices(id),
    enabled: !!id,
  });
}

export function useProductStats(id) {
  return useQuery({
    queryKey: ["product-stats", id],
    queryFn: () => getProductStats(id),
    enabled: !!id,
  });
}
