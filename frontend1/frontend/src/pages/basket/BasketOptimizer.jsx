import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ShoppingBasket, Check, Trophy } from "lucide-react";
import { useProducts } from "../../hooks/useProducts";
import Skeleton from "../../components/common/Skeleton";
import EmptyState from "../../components/common/EmptyState";
import ErrorState from "../../components/common/ErrorState";

const STORES = ["Blinkit", "Zepto", "Instamart", "BigBasket"];

function estimatePrice(product, store) {
  // Prefer real lowest/highest when available; otherwise deterministic estimate
  const low = product.lowest_price != null ? Number(product.lowest_price) : null;
  const high = product.highest_price != null ? Number(product.highest_price) : null;
  if (low != null && high != null && high > low) {
    const idx = STORES.indexOf(store);
    const t = idx / Math.max(STORES.length - 1, 1);
    return Math.round(low + (high - low) * t);
  }
  const seed = (product.id ?? 1) * 17 + store.length * 13;
  return 40 + (seed % 160);
}

function BasketOptimizer() {
  const { data, isLoading, error } = useProducts();
  const products = useMemo(() => data ?? [], [data]);
  const [selected, setSelected] = useState([]);

  const toggle = (id) =>
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));

  const basket = useMemo(() => {
    if (selected.length === 0) return null;
    const picked = products.filter((p) => selected.includes(p.id));
    const totals = STORES.map((store) => ({
      store,
      total: picked.reduce((sum, p) => sum + estimatePrice(p, store), 0),
    }));
    const best = totals.reduce((a, b) => (b.total < a.total ? b : a));
    return { totals, best };
  }, [selected, products]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-ink">Basket optimizer</h1>
        <p className="mt-1 text-muted">
          Pick products and see which store wins on estimated total.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card p-5 lg:col-span-2 sm:p-6">
          <h2 className="mb-4 text-lg font-semibold text-ink">Select products</h2>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-14" />
              ))}
            </div>
          ) : error ? (
            <ErrorState
              title="Basket data unavailable"
              description="We couldn't load products to estimate basket totals."
            />
          ) : products.length === 0 ? (
            <EmptyState
              icon={ShoppingBasket}
              title="No products to add"
              description="Track some products first."
            />
          ) : (
            <div className="max-h-96 space-y-2 overflow-y-auto scrollbar-thin pr-1">
              {products.map((p) => {
                const isSelected = selected.includes(p.id);
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => toggle(p.id)}
                    className={`flex w-full items-center justify-between rounded-xl border p-3 text-left transition ${
                      isSelected
                        ? "border-primary/40 bg-primary-soft"
                        : "border-line hover:bg-canvas"
                    }`}
                  >
                    <div>
                      <p className="font-medium text-ink">{p.name}</p>
                      <p className="text-xs text-muted">{p.brand}</p>
                    </div>
                    {isSelected && (
                      <span className="flex h-7 w-7 items-center justify-center rounded-full bg-primary text-white">
                        <Check size={14} />
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        <div className="card p-5 sm:p-6">
          <h2 className="mb-1 text-lg font-semibold text-ink">Store totals</h2>
          <p className="mb-4 text-xs text-muted">
            Estimates from current price ranges — not live checkout carts.
          </p>
          {!basket ? (
            <p className="text-sm text-muted">Select at least one product.</p>
          ) : (
            <div className="space-y-3">
              {basket.totals
                .slice()
                .sort((a, b) => a.total - b.total)
                .map((row) => (
                  <motion.div
                    key={row.store}
                    layout
                    className={`flex items-center justify-between rounded-xl border px-4 py-3 ${
                      row.store === basket.best.store
                        ? "border-primary/40 bg-primary-soft"
                        : "border-line"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {row.store === basket.best.store && (
                        <Trophy size={14} className="text-primary" />
                      )}
                      <span className="font-medium text-ink">{row.store}</span>
                    </div>
                    <span className="tabular font-bold text-ink">₹{row.total}</span>
                  </motion.div>
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default BasketOptimizer;
