import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
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
  const initial = searchParams.get("q") ?? "";
  const [search, setSearch] = useState(initial);
  const { data, isLoading, error } = useProducts(
    search.trim() ? { search: search.trim() } : {}
  );

  useEffect(() => {
    setSearch(searchParams.get("q") ?? "");
  }, [searchParams]);

  const products = data ?? [];

  function commitSearch(q) {
    const trimmed = (q ?? search).trim();
    setSearch(trimmed);
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
          value={search}
          onChange={setSearch}
          onSubmit={commitSearch}
          size="sm"
          placeholder="Filter by name, brand, category…"
        />
      </div>

      {isLoading && (
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

      {!isLoading && !error && products.length > 0 && (
        <motion.div
          className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3"
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
