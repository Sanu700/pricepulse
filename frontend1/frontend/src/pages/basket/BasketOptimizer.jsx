import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ShoppingBasket, Check, Trophy } from "lucide-react";
import { useProducts } from "../../hooks/useProducts";
import Skeleton from "../../components/common/Skeleton";
import EmptyState from "../../components/common/EmptyState";
import ComingSoon from "../../components/common/ComingSoon";

const MOCK_STORES = ["BigBasket", "Blinkit", "Zepto"];

// Deterministic mock price per product+store so the demo is stable across
// renders, without inventing a fake API call. Real optimization would need
// a backend endpoint that doesn't exist yet.
function mockPrice(productId, store) {
  const seed = String(productId).length + store.length + MOCK_STORES.indexOf(store);
  return 40 + ((productId?.toString().charCodeAt(0) ?? 50) * 7 + seed * 13) % 160;
}

function BasketOptimizer() {
  const { data, isLoading } = useProducts();
  const products = data ?? [];
  const [selected, setSelected] = useState([]);

  const toggle = (id) =>
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));

  const basket = useMemo(() => {
    if (selected.length === 0) return null;
    const totals = MOCK_STORES.map((store) => ({
      store,
      total: selected.reduce((sum, id) => sum + mockPrice(id, store), 0),
    }));
    const best = totals.reduce((a, b) => (b.total < a.total ? b : a));
    return { totals, best };
  }, [selected]);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
            Basket optimizer
          </h1>
          <p className="mt-2 text-zinc-500 dark:text-zinc-400">
            Pick products and see which store wins on total price.
          </p>
        </div>
        <ComingSoon label="Mock data" />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card p-6 lg:col-span-2">
          <h2 className="mb-4 text-lg font-semibold">Select products</h2>

          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-14" />
              ))}
            </div>
          ) : products.length === 0 ? (
            <EmptyState icon={ShoppingBasket} title="No products to add" description="Track some products first." />
          ) : (
            <div className="max-h-96 space-y-2 overflow-y-auto scrollbar-thin pr-1">
              {products.map((p) => {
                const isSelected = selected.includes(p.id);
                return (
                  <button
                    key={p.id}
                    onClick={() => toggle(p.id)}
                    className={`flex w-full items-center justify-between rounded-xl border p-3 text-left transition ${
                      isSelected
                        ? "border-brand-300 bg-brand-50 dark:border-brand-500/40 dark:bg-brand-500/10"
                        : "border-zinc-100 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-800/50"
                    }`}
                  >
                    <div>
                      <p className="font-medium text-zinc-900 dark:text-zinc-100">{p.name}</p>
                      <p className="text-xs text-zinc-500 dark:text-zinc-400">{p.brand}</p>
                    </div>
                    <span
                      className={`flex h-6 w-6 items-center justify-center rounded-full border ${
                        isSelected
                          ? "border-brand-600 bg-brand-600 text-white"
                          : "border-zinc-300 dark:border-zinc-600"
                      }`}
                    >
                      {isSelected && <Check size={14} />}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        <div className="card p-6">
          <h2 className="mb-4 text-lg font-semibold">Store comparison</h2>

          {!basket ? (
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              Select at least one product to compare totals.
            </p>
          ) : (
            <div className="space-y-3">
              {basket.totals
                .sort((a, b) => a.total - b.total)
                .map((t) => (
                  <motion.div
                    layout
                    key={t.store}
                    className={`flex items-center justify-between rounded-xl border p-3 ${
                      t.store === basket.best.store
                        ? "border-emerald-200 bg-emerald-50 dark:border-emerald-900/50 dark:bg-emerald-950/30"
                        : "border-zinc-100 dark:border-zinc-800"
                    }`}
                  >
                    <span className="flex items-center gap-2 font-medium text-zinc-800 dark:text-zinc-200">
                      {t.store === basket.best.store && <Trophy size={14} className="text-emerald-600" />}
                      {t.store}
                    </span>
                    <span className="tabular font-bold">₹{t.total}</span>
                  </motion.div>
                ))}
              <p className="pt-2 text-xs text-zinc-400">
                Totals are illustrative — computed client-side, not from live store prices.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default BasketOptimizer;
