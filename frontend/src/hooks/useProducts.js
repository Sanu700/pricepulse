import { useQuery } from "@tanstack/react-query";
import { getProduct, getProducts } from "../services/productService";

export function useProducts() {
    return useQuery({
        queryKey: ["products"],
        queryFn: getProducts,
    });
}

export function useProduct(id) {
    return useQuery({
        queryKey: ["product", id],
        queryFn: () => getProduct(id),
        enabled: !!id,
    });
}