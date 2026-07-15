import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Package,
  Trophy,
  CheckCircle2,
  XCircle,
  Heart,
  ArrowLeft,
  ExternalLink,
  TrendingDown,
} from "lucide-react";
import { toast } from "sonner";
import { useProduct } from "../../hooks/useProducts";
import { useProductHistory } from "../../hooks/useProductHistory";
import { useProductPrices, useProductStats } from "../../hooks/useProductPrices";
import { useWishlist } from "../../hooks/useWishlist";
import { createPriceAlert } from "../../services/authService";
import PriceHistoryChart from "../../components/products/PriceHistoryChart";
import Skeleton from "../../components/common/Skeleton";
import ErrorState from "../../components/common/ErrorState";

function formatINR(v) {
  if (v == null || v === "") return "—";
  return `₹${Number(v).toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
}

function ProductDetails() {
  const { id } = useParams();
  const { data, isLoading, error } = useProduct(id);
  const { data: prices, isLoading: pricesLoading } = useProductPrices(id);
  const { data: history, isLoading: historyLoading } = useProductHistory(id);
  const { data: stats } = useProductStats(id);
  const { isWishlisted, toggleWishlist } = useWishlist();
  const [alertPrice, setAlertPrice] = useState("");
  const [alertEmail, setAlertEmail] = useState("");
  const [savingAlert, setSavingAlert] = useState(false);

  const product = data ?? {};
  const currentPrices = useMemo(() => {
    const rows = Array.isArray(prices) ? [...prices] : [];
    return rows.sort((a, b) => Number(a.price) - Number(b.price));
  }, [prices]);
  const lowest = currentPrices[0];
  const wishlisted = isWishlisted(Number(id));

  async function handleAlert(e) {
    e.preventDefault();
    if (!alertPrice) {
      toast.error("Enter a target price");
      return;
    }
    setSavingAlert(true);
    try {
      await createPriceAlert({
        product: Number(id),
        target_price: alertPrice,
        email: alertEmail,
      });
      toast.success("Price alert saved");
      setAlertPrice("");
    } catch (err) {
      toast.error("Could not save alert");
      console.error(err);
    } finally {
      setSavingAlert(false);
    }
  }

  if (isLoading) {
    return (
      <div className="grid gap-8 lg:grid-cols-2">
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
    return <ErrorState description="We couldn't load this product." />;
  }

  return (
    <div className="space-y-8">
      <Link to="/products" className="btn-ghost -ml-2 w-fit text-muted">
        <ArrowLeft size={16} /> Back to products
      </Link>

      <div className="grid gap-8 lg:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="card flex h-72 items-center justify-center overflow-hidden sm:h-96"
        >
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="h-full w-full object-contain p-8"
            />
          ) : (
            <Package size={96} className="text-slate-300" />
          )}
        </motion.div>

        <div className="space-y-5">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-ink sm:text-3xl">
                {product.name}
              </h1>
              <div className="mt-3 flex flex-wrap gap-2 text-sm">
                <span className="rounded-full bg-canvas px-3 py-1 text-muted">{product.brand}</span>
                <span className="rounded-full bg-canvas px-3 py-1 text-muted">{product.category}</span>
              </div>
            </div>
            <button
              type="button"
              onClick={() => {
                toggleWishlist(product);
                toast.success(wishlisted ? "Removed from wishlist" : "Saved to wishlist");
              }}
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-line bg-surface transition hover:bg-canvas"
              aria-label="Toggle wishlist"
            >
              <Heart size={18} className={wishlisted ? "fill-danger text-danger" : "text-muted"} />
            </button>
          </div>

          {lowest && (
            <div className="flex items-center gap-3 rounded-2xl border border-primary/20 bg-primary-soft/60 p-4">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-white">
                <Trophy size={18} />
              </span>
              <div>
                <p className="text-sm font-semibold text-primary-dark">Cheapest right now</p>
                <p className="text-ink">
                  {lowest.store} · <span className="tabular font-bold">{formatINR(lowest.price)}</span>
                </p>
              </div>
            </div>
          )}

          {stats && (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                { label: "Lowest", value: formatINR(stats.lowest_price) },
                { label: "Highest", value: formatINR(stats.highest_price) },
                { label: "Average", value: formatINR(stats.average_price) },
                { label: "Save up to", value: formatINR(stats.savings) },
              ].map((s) => (
                <div key={s.label} className="rounded-xl border border-line bg-canvas px-3 py-3">
                  <p className="text-[11px] font-medium uppercase tracking-wide text-muted">{s.label}</p>
                  <p className="tabular mt-1 text-base font-bold text-ink">{s.value}</p>
                </div>
              ))}
            </div>
          )}

          {product.description && (
            <p className="text-sm leading-relaxed text-muted">{product.description}</p>
          )}

          <form onSubmit={handleAlert} className="card space-y-3 p-4">
            <p className="text-sm font-semibold text-ink">Set a price alert</p>
            <div className="grid gap-2 sm:grid-cols-2">
              <input
                type="number"
                step="0.01"
                min="1"
                placeholder="Notify below ₹"
                value={alertPrice}
                onChange={(e) => setAlertPrice(e.target.value)}
                className="input-field"
              />
              <input
                type="email"
                placeholder="Email (optional)"
                value={alertEmail}
                onChange={(e) => setAlertEmail(e.target.value)}
                className="input-field"
              />
            </div>
            <button type="submit" disabled={savingAlert} className="btn-primary w-full sm:w-auto">
              {savingAlert ? "Saving…" : "Save alert"}
            </button>
          </form>
        </div>
      </div>

      {/* Comparison table */}
      <section className="card overflow-hidden">
        <div className="border-b border-line px-5 py-4 sm:px-6">
          <h2 className="text-lg font-semibold text-ink">Store comparison</h2>
          <p className="text-sm text-muted">Live prices ranked cheapest first</p>
        </div>
        {pricesLoading ? (
          <div className="space-y-3 p-5">
            <Skeleton className="h-14" />
            <Skeleton className="h-14" />
          </div>
        ) : currentPrices.length === 0 ? (
          <p className="p-6 text-sm text-muted">No prices yet — run price collection.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px] text-left text-sm">
              <thead className="bg-canvas text-xs uppercase tracking-wide text-muted">
                <tr>
                  <th className="px-5 py-3 font-medium">Store</th>
                  <th className="px-5 py-3 font-medium">Price</th>
                  <th className="px-5 py-3 font-medium">Availability</th>
                  <th className="px-5 py-3 font-medium">Updated</th>
                  <th className="px-5 py-3 font-medium" />
                </tr>
              </thead>
              <tbody>
                {currentPrices.map((row, index) => (
                  <tr
                    key={`${row.store}-${index}`}
                    className={`border-t border-line ${
                      index === 0 ? "bg-primary-soft/40" : "bg-surface"
                    }`}
                  >
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        {row.store_logo ? (
                          <img src={row.store_logo} alt="" className="h-6 w-6 object-contain" />
                        ) : null}
                        <span className="font-semibold text-ink">{row.store}</span>
                        {index === 0 && <span className="badge badge-cheap">Cheapest</span>}
                      </div>
                    </td>
                    <td className="tabular px-5 py-4 text-base font-bold text-ink">
                      {formatINR(row.price)}
                      {index > 0 && lowest && (
                        <span className="ml-2 text-xs font-normal text-danger">
                          +{formatINR(Number(row.price) - Number(lowest.price))}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={`inline-flex items-center gap-1 text-sm ${
                          row.in_stock ? "text-primary" : "text-danger"
                        }`}
                      >
                        {row.in_stock ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
                        {row.in_stock ? "In stock" : "Out of stock"}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-muted">
                      {row.last_updated
                        ? new Date(row.last_updated).toLocaleString("en-IN", {
                            day: "numeric",
                            month: "short",
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : "—"}
                    </td>
                    <td className="px-5 py-4">
                      {row.product_url && (
                        <a
                          href={row.product_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-accent hover:underline"
                        >
                          Open <ExternalLink size={12} />
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {historyLoading ? (
        <Skeleton className="h-80" />
      ) : (
        <PriceHistoryChart data={history ?? []} />
      )}

      {stats?.last_change && (
        <div className="card flex items-center gap-3 p-4">
          <TrendingDown size={18} className="text-primary" />
          <p className="text-sm text-muted">
            Last change at <span className="font-medium text-ink">{stats.last_change.store}</span>:{" "}
            {formatINR(stats.last_change.from)} → {formatINR(stats.last_change.to)} (
            {Number(stats.last_change.delta) >= 0 ? "+" : ""}
            {formatINR(stats.last_change.delta)})
          </p>
        </div>
      )}
    </div>
  );
}

export default ProductDetails;
