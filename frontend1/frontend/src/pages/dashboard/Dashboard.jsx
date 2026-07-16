import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Package,
  Store,
  TrendingDown,
  PiggyBank,
  Bell,
  ArrowRight,
} from "lucide-react";
import { useAnalytics, useProducts } from "../../hooks/useProducts";
import { useWishlist } from "../../hooks/useWishlist";
import StatCard from "../../components/dashboard/StatCard";
import Skeleton from "../../components/common/Skeleton";
import ErrorState from "../../components/common/ErrorState";
import EmptyState from "../../components/common/EmptyState";

function formatINR(v) {
  if (v == null) return "—";
  return `₹${Number(v).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

function Dashboard() {
  const { data: products, isLoading, error } = useProducts();
  const { data: analytics, isLoading: analyticsLoading, error: analyticsError } = useAnalytics();
  const { items: wishlist } = useWishlist();

  if (isLoading || analyticsLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-28" />
        <div className="grid gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      </div>
    );
  }

  if (error || analyticsError) {
    return <ErrorState description="Dashboard data unavailable. Check API connectivity." />;
  }

  const list = products ?? [];
  const drops = analytics?.recent_drops ?? [];
  const trending = analytics?.trending_products ?? [];

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold tracking-tight text-ink">Dashboard</h1>
        <p className="mt-1 text-muted">
          Your savings pulse across {analytics?.stores_compared ?? 3} stores.
        </p>
      </motion.div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Tracked products" value={analytics?.products_tracked ?? list.length} icon={Package} />
        <StatCard title="Average savings" value={formatINR(analytics?.average_savings)} icon={PiggyBank} />
        <StatCard
          title="Biggest drop"
          value={
            analytics?.biggest_drop
              ? formatINR(analytics.biggest_drop.savings)
              : "—"
          }
          icon={TrendingDown}
        />
        <StatCard title="Wishlist items" value={wishlist.length} icon={Bell} />
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <section className="card p-5 lg:col-span-3">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-ink">Recent alerts</h2>
            <Link to="/wishlist" className="text-sm font-medium text-primary hover:underline">
              Wishlist
            </Link>
          </div>
          {drops.length === 0 ? (
            <EmptyState
              icon={TrendingDown}
              title="No drops yet"
              description="Price drops appear here after the collector refreshes prices."
            />
          ) : (
            <div className="space-y-2">
              {drops.map((d) => (
                <Link
                  key={`${d.product_id}-${d.store}`}
                  to={`/products/${d.product_id}`}
                  className="flex items-center justify-between rounded-xl border border-line px-4 py-3 transition hover:bg-canvas"
                >
                  <div>
                    <p className="font-medium text-ink">{d.product}</p>
                    <p className="text-xs text-muted">{d.store}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted line-through">{formatINR(d.from)}</p>
                    <p className="flex items-center justify-end gap-1 font-semibold text-primary">
                      <TrendingDown size={14} />
                      {formatINR(d.to)}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="card p-5 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-ink">Trending</h2>
            <Store size={16} className="text-muted" />
          </div>
          <div className="space-y-3">
            {trending.slice(0, 6).map((p) => (
              <Link
                key={p.id}
                to={`/products/${p.id}`}
                className="flex items-center justify-between text-sm"
              >
                <span className="truncate text-ink">{p.name}</span>
                <span className="tabular font-semibold text-primary">{formatINR(p.lowest_price)}</span>
              </Link>
            ))}
            {trending.length === 0 && (
              <p className="text-sm text-muted">Collect prices to see trends.</p>
            )}
          </div>
          <Link to="/products" className="btn-primary mt-6 w-full">
            Browse products <ArrowRight size={14} />
          </Link>
        </section>
      </div>

      {analytics?.store_averages?.length > 0 && (
        <section className="card p-5">
          <h2 className="mb-4 text-lg font-semibold text-ink">Store price index</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            {analytics.store_averages.map((s) => (
              <div key={s.store} className="rounded-xl border border-line bg-canvas p-4">
                <p className="text-sm font-medium text-muted">{s.store}</p>
                <p className="tabular mt-1 text-2xl font-bold text-ink">{formatINR(s.avg)}</p>
                <p className="text-xs text-muted">{s.count} SKUs</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default Dashboard;
