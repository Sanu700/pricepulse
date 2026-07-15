import { useQuery } from "@tanstack/react-query";
import { getAnalyticsSummary, getStores } from "../services/pricingService";
import { getProduct, getProducts } from "../services/productService";

export function useProducts(params = {}, options = {}) {
  return useQuery({
    queryKey: ["products", params],
    queryFn: () => getProducts(params),
    ...options,
  });
}

export function useProduct(id) {
  return useQuery({
    queryKey: ["product", id],
    queryFn: () => getProduct(id),
    enabled: !!id,
  });
}

export function useAnalytics() {
  return useQuery({
    queryKey: ["analytics-summary"],
    queryFn: getAnalyticsSummary,
    staleTime: 60_000,
  });
}

export function useStores() {
  return useQuery({
    queryKey: ["stores"],
    queryFn: getStores,
    staleTime: 5 * 60_000,
  });
}
