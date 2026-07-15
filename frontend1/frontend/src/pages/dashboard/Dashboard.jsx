import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Package,
  Store,
  Radio,
  TrendingDown,
  TrendingUp,
  Sparkles,
  PiggyBank,
  Search,
  ArrowRight,
} from "lucide-react";
import { useProducts } from "../../hooks/useProducts";
import StatCard from "../../components/dashboard/StatCard";
import Skeleton from "../../components/common/Skeleton";
import ErrorState from "../../components/common/ErrorState";
import ComingSoon from "../../components/common/ComingSoon";

// Mock data: no backend support yet for trends, drops, store comparison, or AI insight.
const trendingProducts = [
  { id: "m1", name: "Amul Gold Milk 1L", change: -8 },
  { id: "m2", name: "Tata Salt 1kg", change: 4 },
  { id: "m3", name: "Aashirvaad Atta 5kg", change: -12 },
];

const priceDrops = [
  { id: "d1", name: "Fortune Sunflower Oil 1L", from: 189, to: 159, store: "BigBasket" },
  { id: "d2", name: "Nescafe Classic 100g", from: 285, to: 249, store: "Blinkit" },
];

const storeComparison = [
  { store: "BigBasket", avgIndex: 96 },
  { store: "Blinkit", avgIndex: 102 },
  { store: "Zepto", avgIndex: 99 },
];

function Dashboard() {
  const { data, isLoading, error } = useProducts();
  const [quickSearch, setQuickSearch] = useState("");

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-40 w-full" />
        <div className="grid gap-6 md:grid-cols-3">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      </div>
    );
  }

  if (error) {
    return <ErrorState description="We couldn't load your dashboard data. Check your connection and try again." />;
  }

  const products = data ?? [];

  return (
    <div className="space-y-10">
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="card relative overflow-hidden p-8 sm:p-10"
      >
        <div className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-brand-500/10 blur-3xl" />
        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700 dark:bg-brand-500/10 dark:text-brand-300">
              <Radio size={12} /> Live tracking across stores
            </span>
            <h1 className="mt-4 text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
              Good to see you back.
            </h1>
            <p className="mt-2 max-w-md text-zinc-500 dark:text-zinc-400">
              {products.length} products tracked across every store you follow. Here's what moved.
            </p>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              window.location.assign(
                quickSearch.trim() ? `/products?q=${encodeURIComponent(quickSearch)}` : "/products"
              );
            }}
            className="relative w-full max-w-sm"
          >
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={16} />
            <input
              value={quickSearch}
              onChange={(e) => setQuickSearch(e.target.value)}
              placeholder="Quick search a product..."
              className="w-full rounded-xl border border-zinc-200 bg-white py-2.5 pl-9 pr-4 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-zinc-700 dark:bg-zinc-900"
            />
          </form>
        </div>
      </motion.section>

      {/* KPI row — real data only */}
      <div className="grid gap-6 md:grid-cols-3">
        <StatCard title="Products tracked" value={products.length} icon={Package} />
        <StatCard title="Stores compared" value="2" icon={Store} />
        <StatCard title="Tracking window" value="24/7" icon={Radio} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent price drops */}
        <section className="card p-6 lg:col-span-2">
          <div className="mb-5 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Recent price drops</h2>
            <ComingSoon />
          </div>
          <div className="space-y-3">
            {priceDrops.map((d) => (
              <div
                key={d.id}
                className="flex items-center justify-between rounded-xl border border-zinc-100 p-4 dark:border-zinc-800"
              >
                <div>
                  <p className="font-medium text-zinc-900 dark:text-zinc-100">{d.name}</p>
                  <p className="text-sm text-zinc-500 dark:text-zinc-400">{d.store}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-zinc-400 line-through">₹{d.from}</p>
                  <p className="flex items-center gap-1 font-semibold text-emerald-600 dark:text-emerald-400">
                    <TrendingDown size={14} /> ₹{d.to}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* AI Insight */}
        <section className="card relative overflow-hidden bg-gradient-to-br from-brand-600 to-brand-800 p-6 text-white">
          <Sparkles className="absolute -right-4 -top-4 h-24 w-24 text-white/10" />
          <div className="relative">
            <span className="inline-flex items-center gap-1 rounded-full bg-white/15 px-2.5 py-1 text-xs font-semibold">
              <Sparkles size={11} /> AI Insight
            </span>
            <p className="mt-4 text-sm leading-relaxed text-white/90">
              Prices on packaged staples tend to dip early in the week. Based on mock trend data, waiting 2–3 days
              could save on your tracked list.
            </p>
            <p className="mt-4 text-xs text-white/60">Coming soon — this card will use real prediction data.</p>
          </div>
        </section>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Trending */}
        <section className="card p-6">
          <div className="mb-5 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Trending products</h2>
            <ComingSoon />
          </div>
          <div className="space-y-3">
            {trendingProducts.map((p) => (
              <div key={p.id} className="flex items-center justify-between text-sm">
                <span className="text-zinc-700 dark:text-zinc-300">{p.name}</span>
                <span
                  className={`flex items-center gap-1 font-medium ${
                    p.change < 0 ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"
                  }`}
                >
                  {p.change < 0 ? <TrendingDown size={14} /> : <TrendingUp size={14} />}
                  {Math.abs(p.change)}%
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Store comparison */}
        <section className="card p-6">
          <div className="mb-5 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Store comparison</h2>
            <ComingSoon />
          </div>
          <div className="space-y-4">
            {storeComparison.map((s) => (
              <div key={s.store}>
                <div className="mb-1 flex justify-between text-sm">
                  <span className="text-zinc-600 dark:text-zinc-400">{s.store}</span>
                  <span className="font-medium">{s.avgIndex}</span>
                </div>
                <div className="h-2 w-full rounded-full bg-zinc-100 dark:bg-zinc-800">
                  <div
                    className="h-2 rounded-full bg-brand-500"
                    style={{ width: `${Math.min(s.avgIndex, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Weekly savings */}
        <section className="card flex flex-col justify-between p-6">
          <div>
            <div className="mb-5 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Weekly savings</h2>
              <ComingSoon />
            </div>
            <div className="flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400">
                <PiggyBank size={20} />
              </span>
              <div>
                <p className="tabular text-2xl font-bold">₹0</p>
                <p className="text-xs text-zinc-400">saved so far — start tracking to see this grow</p>
              </div>
            </div>
          </div>
          <Link
            to="/products"
            className="mt-6 flex items-center justify-center gap-1.5 rounded-xl bg-zinc-900 py-2.5 text-sm font-medium text-white transition hover:bg-zinc-700 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            Browse products <ArrowRight size={14} />
          </Link>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
