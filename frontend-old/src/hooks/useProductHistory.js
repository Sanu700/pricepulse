import { useQuery } from "@tanstack/react-query";
import { getProductHistory } from "../services/productService";

export function useProductHistory(id) {
    return useQuery({
        queryKey: ["history", id],
        queryFn: () => getProductHistory(id),
        enabled: !!id,
    });
}