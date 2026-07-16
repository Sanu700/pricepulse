import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Package,
  Store,
  TrendingDown,
  PiggyBank,
  Sparkles,
} from "lucide-react";
import { useAnalytics, useProducts, useStores } from "../../hooks/useProducts";
import ProductCard from "../../components/products/ProductCard";
import HeroSearch from "../../components/common/HeroSearch";
import StoreLogo from "../../components/common/StoreLogo";
import Skeleton from "../../components/common/Skeleton";
import ErrorState from "../../components/common/ErrorState";

function formatINR(v) {
  if (v == null) return "—";
  return `₹${Number(v).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

function StatPill({ icon: Icon, label, value }) {
  return (
    <div className="card flex items-center gap-3 px-4 py-3">
      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-soft text-primary">
        <Icon size={18} />
      </span>
      <div>
        <p className="text-xs font-medium text-muted">{label}</p>
        <p className="tabular text-lg font-bold text-ink">{value}</p>
      </div>
    </div>
  );
}

function Home() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const { data: products, isLoading, error } = useProducts({ page_size: 6 });
  const { data: analytics, error: analyticsError } = useAnalytics();
  const { data: stores } = useStores();

  const list = products ?? [];
  const popular = [...list].slice(0, 6);
  const trending = analytics?.trending_products ?? list.slice(0, 4);
  const deals = analytics?.cheapest_deals ?? [];

  function goSearch(q) {
    const trimmed = (q ?? query).trim();
    navigate(trimmed ? `/products?q=${encodeURIComponent(trimmed)}` : "/products");
  }

  if (error) {
    return <ErrorState description="Couldn't load the home feed. Is the backend running?" />;
  }

  return (
    <div className="space-y-12">
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl border border-line bg-surface px-6 py-10 sm:px-10 sm:py-14"
        style={{
          backgroundImage:
            "radial-gradient(ellipse 80% 60% at 100% 0%, rgba(22,163,74,0.08), transparent), radial-gradient(ellipse 50% 40% at 0% 100%, rgba(37,99,235,0.06), transparent)",
        }}
      >
        <div className="relative mx-auto max-w-2xl text-center">
          <p className="mb-3 text-sm font-semibold tracking-wide text-primary">
            PricePulse
          </p>
          <h1 className="text-3xl font-bold tracking-tight text-ink sm:text-4xl lg:text-5xl">
            Find the cheapest grocery deals near you
          </h1>
          <p className="mx-auto mt-3 max-w-lg text-muted">
            Compare live prices across Blinkit, Zepto, Instamart, and BigBasket
            without opening four tabs.
          </p>
          <div className="mx-auto mt-8 max-w-xl">
            <HeroSearch
              value={query}
              onChange={setQuery}
              onSubmit={goSearch}
              autoFocus
            />
          </div>
          <div className="mt-4 flex flex-wrap justify-center gap-2 text-xs text-muted">
            {["Amul Butter", "Tata Salt", "Aashirvaad Atta", "KitKat"].map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => {
                  setQuery(s);
                  goSearch(s);
                }}
                className="rounded-full border border-line bg-canvas px-3 py-1 transition hover:border-primary hover:text-primary"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Stores */}
      <section>
        <div className="mb-4 flex items-end justify-between">
          <div>
            <h2 className="section-title">Stores we compare</h2>
            <p className="section-sub">One search, four grocery providers</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4">
          {(stores?.length ? stores : [
            { id: 1, name: "Blinkit" },
            { id: 2, name: "Zepto" },
            { id: 3, name: "Instamart" },
            { id: 4, name: "BigBasket" },
          ]).map((s) => (
            <div key={s.id ?? s.name} className="card flex flex-col items-center gap-2 p-4 sm:p-6">
              <StoreLogo name={s.name} size={40} />
              <p className="text-sm font-semibold text-ink">{s.name}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatPill icon={Package} label="Products tracked" value={analytics?.products_tracked ?? list.length} />
        <StatPill icon={Store} label="Stores" value={analytics?.stores_compared ?? stores?.length ?? 4} />
        <StatPill icon={PiggyBank} label="Avg. savings" value={formatINR(analytics?.average_savings)} />
        <StatPill
          icon={TrendingDown}
          label="Biggest drop"
          value={
            analytics?.biggest_drop
              ? formatINR(analytics.biggest_drop.savings)
              : "—"
          }
        />
      </section>

      {analyticsError && (
        <ErrorState
          title="Analytics temporarily unavailable"
          description="Product browsing still works, but summary trends couldn't be loaded."
        />
      )}

      {/* Cheapest deals */}
      <section>
        <div className="mb-5 flex items-end justify-between gap-4">
          <div>
            <h2 className="section-title">Cheapest deals today</h2>
            <p className="section-sub">Biggest gaps between stores right now</p>
          </div>
          <Link to="/products" className="btn-ghost text-primary">
            See all <ArrowRight size={14} />
          </Link>
        </div>
        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-28" />
            ))}
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {(deals.length ? deals : list.slice(0, 6)).map((d) => (
              <Link
                key={d.id}
                to={`/products/${d.id}`}
                className="card card-hover flex items-center justify-between gap-3 p-4"
              >
                <div className="min-w-0">
                  <p className="truncate font-semibold text-ink">{d.name}</p>
                  <p className="text-xs text-muted">
                    {d.brand ?? "Grocery"}
                    {d.savings > 0 ? ` · save up to ${formatINR(d.savings)}` : ""}
                  </p>
                </div>
                <span className="tabular shrink-0 text-lg font-bold text-primary">
                  {formatINR(d.lowest_price)}
                </span>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Popular */}
      <section>
        <div className="mb-5 flex items-end justify-between">
          <div>
            <h2 className="section-title">Popular products</h2>
            <p className="section-sub">Frequently compared essentials</p>
          </div>
          <Link to="/products" className="btn-ghost text-primary">
            Browse <ArrowRight size={14} />
          </Link>
        </div>
        {isLoading ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-80" />
            ))}
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {popular.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        )}
      </section>

      {/* Trending */}
      <section className="card p-6">
        <div className="mb-5 flex items-center gap-2">
          <Sparkles size={18} className="text-accent" />
          <h2 className="text-lg font-semibold text-ink">Trending now</h2>
        </div>
        <div className="divide-y divide-line">
          {(trending.length ? trending : list.slice(0, 5)).map((p, i) => (
            <Link
              key={p.id}
              to={`/products/${p.id}`}
              className="flex items-center justify-between gap-3 py-3 transition hover:bg-canvas/80"
            >
              <div className="flex items-center gap-3 min-w-0">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-canvas text-xs font-bold text-muted">
                  {i + 1}
                </span>
                <span className="truncate text-sm font-medium text-ink">{p.name}</span>
              </div>
              <span className="tabular text-sm font-semibold text-primary">
                {formatINR(p.lowest_price)}
              </span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Home;
