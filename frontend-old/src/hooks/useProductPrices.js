import { useQuery } from "@tanstack/react-query";
import { getProductPrices } from "../services/productService";

export function useProductPrices(id) {
    return useQuery({
        queryKey: ["product-prices", id],
        queryFn: () => getProductPrices(id),
        enabled: !!id,
    });
}