import { useQuery } from "@tanstack/react-query";
import { getProductHistory } from "../services/productService";

export function useProductHistory(id, params = {}) {
  return useQuery({
    queryKey: ["history", id, params],
    queryFn: () => getProductHistory(id, params),
    enabled: !!id,
  });
}
