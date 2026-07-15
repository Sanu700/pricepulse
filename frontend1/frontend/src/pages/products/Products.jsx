import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { PackageSearch } from "lucide-react";
import ProductCard from "../../components/products/ProductCard";
import { useProducts } from "../../hooks/useProducts";
import SearchBar from "../../components/common/SearchBar";
import Skeleton from "../../components/common/Skeleton";
import ErrorState from "../../components/common/ErrorState";
import EmptyState from "../../components/common/EmptyState";

function Products() {
  const { data, isLoading, error } = useProducts();
  const [searchParams] = useSearchParams();
  // Honors ?q= set by the navbar / dashboard quick search, same filtering
  // logic that already existed here — just seeded from the URL too.
  const [search, setSearch] = useState(searchParams.get("q") ?? "");

  const products = data ?? [];
  const filteredProducts = products.filter((product) =>
    product.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
          Products
        </h1>
        <p className="mt-2 text-zinc-500 dark:text-zinc-400">Compare prices across stores.</p>
      </div>

      <div className="mb-8 max-w-lg">
        <SearchBar value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {isLoading && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-72" />
          ))}
        </div>
      )}

      {error && (
        <ErrorState description="We couldn't load products right now. Try refreshing the page." />
      )}

      {!isLoading && !error && filteredProducts.length === 0 && (
        <EmptyState
          icon={PackageSearch}
          title="No products match your search"
          description="Try a different name, brand, or category."
        />
      )}

      {!isLoading && !error && filteredProducts.length > 0 && (
        <motion.div
          className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
          initial="hidden"
          animate="visible"
          variants={{ visible: { transition: { staggerChildren: 0.04 } } }}
        >
          {filteredProducts.map((product) => (
            <motion.div
              key={product.id}
              variants={{
                hidden: { opacity: 0, y: 12 },
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
