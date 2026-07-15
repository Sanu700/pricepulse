import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Package, Trophy, CheckCircle2, XCircle, Sparkles, ArrowRight } from "lucide-react";
import { useProduct } from "../../hooks/useProducts";
import { useProductPrices } from "../../hooks/useProductPrices";
import { useProductHistory } from "../../hooks/useProductHistory";
import PriceHistoryChart from "../../components/products/PriceHistoryChart";
import Skeleton from "../../components/common/Skeleton";
import ErrorState from "../../components/common/ErrorState";
import ComingSoon from "../../components/common/ComingSoon";

function ProductDetails() {
  const { id } = useParams();

  const { data, isLoading, error } = useProduct(id);
  const { data: prices, isLoading: pricesLoading } = useProductPrices(id);
  const { data: history, isLoading: historyLoading } = useProductHistory(id);

  if (isLoading) {
    return (
      <div className="grid gap-10 lg:grid-cols-2">
        <Skeleton className="h-96" />
        <div className="space-y-4">
          <Skeleton className="h-10 w-2/3" />
          <Skeleton className="h-24" />
          <Skeleton className="h-48" />
        </div>
      </div>
    );
  }

  if (error) {
    return <ErrorState description="We couldn't load this product. It may have been removed." />;
  }

  const product = data ?? {};
  const currentPrices = prices ?? [];
  const priceHistory = history ?? [];
  const lowest = currentPrices[0];

  return (
    <div className="space-y-10">
      {historyLoading ? (
        <Skeleton className="h-80 w-full" />
      ) : (
        priceHistory.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
            <PriceHistoryChart data={priceHistory} />
          </motion.div>
        )
      )}

      <div className="grid gap-10 lg:grid-cols-2">
        {/* Image */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card flex h-80 items-center justify-center lg:h-full"
        >
          <Package size={96} className="text-brand-300 dark:text-brand-700" />
        </motion.div>

        {/* Details */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
              {product.name}
            </h1>
            <div className="mt-3 flex flex-wrap gap-2 text-sm text-zinc-500 dark:text-zinc-400">
              <span className="rounded-full bg-zinc-100 px-3 py-1 dark:bg-zinc-800">{product.brand}</span>
              <span className="rounded-full bg-zinc-100 px-3 py-1 dark:bg-zinc-800">{product.category}</span>
              {product.barcode && (
                <span className="rounded-full bg-zinc-100 px-3 py-1 dark:bg-zinc-800">#{product.barcode}</span>
              )}
            </div>
          </div>

          {lowest && (
            <div className="flex items-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-900/50 dark:bg-emerald-950/30">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600 dark:bg-emerald-900/50 dark:text-emerald-400">
                <Trophy size={18} />
              </span>
              <div>
                <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">Lowest price</p>
                <p className="text-zinc-700 dark:text-zinc-300">
                  {lowest.store} • <span className="tabular font-bold">₹{lowest.price}</span>
                </p>
              </div>
            </div>
          )}

          {product.description && (
            <div className="card p-5">
              <h2 className="mb-2 text-lg font-semibold">Description</h2>
              <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">{product.description}</p>
            </div>
          )}

          {/* AI prediction — no backend support exists yet */}
          <div className="card relative overflow-hidden bg-gradient-to-br from-brand-600 to-brand-800 p-5 text-white">
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center gap-1.5 text-sm font-semibold">
                <Sparkles size={14} /> AI price prediction
              </span>
              <ComingSoon />
            </div>
            <p className="mt-2 text-sm text-white/80">
              We'll forecast whether this product's price is likely to rise or fall soon.
            </p>
          </div>
        </div>
      </div>

      {/* Current prices */}
      <div className="card p-6">
        <h2 className="mb-6 text-xl font-semibold">Current prices</h2>

        {pricesLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
          </div>
        ) : currentPrices.length === 0 ? (
          <p className="text-sm text-zinc-500 dark:text-zinc-400">No prices available for this product yet.</p>
        ) : (
          <div className="space-y-3">
            {currentPrices.map((price, index) => (
              <div
                key={price.store}
                className={`flex items-center justify-between rounded-xl border p-4 transition hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-800/50 ${
                  index === 0
                    ? "border-emerald-200 bg-emerald-50/50 dark:border-emerald-900/50 dark:bg-emerald-950/20"
                    : "border-zinc-100"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-full font-bold ${
                      index === 0
                        ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-400"
                        : "bg-brand-100 text-brand-600 dark:bg-brand-500/10 dark:text-brand-400"
                    }`}
                  >
                    {index + 1}
                  </div>
                  <div>
                    <h3 className="font-semibold text-zinc-900 dark:text-zinc-100">{price.store}</h3>
                    <p
                      className={`flex items-center gap-1 text-sm ${
                        price.in_stock ? "text-emerald-600 dark:text-emerald-400" : "text-rose-500"
                      }`}
                    >
                      {price.in_stock ? <CheckCircle2 size={13} /> : <XCircle size={13} />}
                      {price.in_stock ? "In stock" : "Out of stock"}
                    </p>
                  </div>
                </div>
                <div className="tabular text-2xl font-bold text-zinc-900 dark:text-zinc-50">₹{price.price}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Related products — mock, no backend endpoint for recommendations */}
      <div className="card p-6">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Related products</h2>
          <ComingSoon />
        </div>
        <div className="scrollbar-thin flex gap-4 overflow-x-auto pb-2">
          {["Similar Atta", "Similar Oil", "Similar Salt", "Similar Snack"].map((name) => (
            <div
              key={name}
              className="flex w-44 shrink-0 flex-col items-center gap-3 rounded-xl border border-zinc-100 p-4 dark:border-zinc-800"
            >
              <div className="flex h-20 w-20 items-center justify-center rounded-lg bg-zinc-100 dark:bg-zinc-800">
                <Package size={28} className="text-zinc-400" />
              </div>
              <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">{name}</p>
            </div>
          ))}
        </div>
      </div>

      <Link
        to="/products"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
      >
        <ArrowRight size={14} className="rotate-180" /> Back to products
      </Link>
    </div>
  );
}

export default ProductDetails;
