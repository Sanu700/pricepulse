import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { keepPreviousData } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { PackageSearch } from "lucide-react";
import ProductCard from "../../components/products/ProductCard";
import { useProducts } from "../../hooks/useProducts";
import HeroSearch from "../../components/common/HeroSearch";
import Skeleton from "../../components/common/Skeleton";
import ErrorState from "../../components/common/ErrorState";
import EmptyState from "../../components/common/EmptyState";

function Products() {
  const [searchParams, setSearchParams] = useSearchParams();
  const committed = (searchParams.get("q") ?? "").trim();
  const [draft, setDraft] = useState(committed);

  // Only the URL-committed query hits the API (submit / Enter / suggestion pick).
  const { data, isLoading, isFetching, error } = useProducts(
    committed ? { search: committed } : {},
    { placeholderData: keepPreviousData }
  );

  useEffect(() => {
    setDraft(searchParams.get("q") ?? "");
  }, [searchParams]);

  const products = data ?? [];

  function commitSearch(q) {
    const trimmed = (q ?? draft).trim();
    setDraft(trimmed);
    if (trimmed) setSearchParams({ q: trimmed });
    else setSearchParams({});
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-ink">Products</h1>
        <p className="mt-1 text-muted">Compare prices across Blinkit, Zepto & Instamart.</p>
      </div>

      <div className="mb-8 max-w-xl">
        <HeroSearch
          value={draft}
          onChange={setDraft}
          onSubmit={commitSearch}
          size="sm"
          placeholder="Filter by name, brand, category…"
        />
      </div>

      {isLoading && !data && (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-80" />
          ))}
        </div>
      )}

      {error && (
        <ErrorState description="We couldn't load products. Is the API running on :8000?" />
      )}

      {!isLoading && !error && products.length === 0 && (
        <EmptyState
          icon={PackageSearch}
          title="No products match your search"
          description="Try a different name, brand, or category."
        />
      )}

      {!error && products.length > 0 && (
        <motion.div
          className={`grid gap-5 sm:grid-cols-2 lg:grid-cols-3 ${isFetching ? "opacity-70" : ""}`}
          initial="hidden"
          animate="visible"
          variants={{ visible: { transition: { staggerChildren: 0.04 } } }}
        >
          {products.map((product) => (
            <motion.div
              key={product.id}
              variants={{
                hidden: { opacity: 0, y: 10 },
                visible: { opacity: 1, y: 0 },
              }}
            >
              <ProductCard product={product} />
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}

export default Products;
