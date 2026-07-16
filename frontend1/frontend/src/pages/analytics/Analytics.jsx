import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { BarChart3, Store, PiggyBank, TrendingDown } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
} from "recharts";
import { useAnalytics } from "../../hooks/useProducts";
import StatCard from "../../components/dashboard/StatCard";
import Skeleton from "../../components/common/Skeleton";
import ErrorState from "../../components/common/ErrorState";

function formatINR(v) {
  if (v == null) return "—";
  return `₹${Number(v).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

function Analytics() {
  const { data, isLoading, error } = useAnalytics();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-20" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
        </div>
        <Skeleton className="h-72" />
      </div>
    );
  }

  if (error) {
    return <ErrorState description="Analytics unavailable." />;
  }

  const daily = (data?.daily_average ?? []).map((r) => ({
    day: r.day ? new Date(r.day).toLocaleDateString("en-IN", { day: "numeric", month: "short" }) : "",
    avg: Number(r.avg),
  }));

  const storeAverages = (data?.store_averages ?? []).map((s) => ({
    store: s.store,
    avg: Number(s.avg),
  }));

  const cheapest = data?.store_averages?.[0]?.store ?? "—";

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-ink">Analytics</h1>
        <p className="mt-1 text-muted">Trends computed from live price history</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="Avg. price" value={formatINR(data?.average_price)} icon={PiggyBank} />
        <StatCard title="Cheapest store" value={cheapest} icon={Store} />
        <StatCard
          title="Biggest drop"
          value={data?.biggest_drop ? formatINR(data.biggest_drop.savings) : "—"}
          icon={TrendingDown}
        />
      </div>

      <motion.section initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card p-5 sm:p-6">
        <div className="mb-5 flex items-center gap-2">
          <BarChart3 size={18} className="text-primary" />
          <h2 className="text-lg font-semibold text-ink">Daily average price</h2>
        </div>
        {daily.length === 0 ? (
          <p className="py-16 text-center text-sm text-muted">
            Not enough history yet. Run <code className="rounded bg-canvas px-1">collect_prices</code>.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={daily}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
              <XAxis dataKey="day" tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} width={40} />
              <Tooltip />
              <Line type="monotone" dataKey="avg" stroke="#16A34A" strokeWidth={2.5} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </motion.section>

      <motion.section initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card p-5 sm:p-6">
        <h2 className="mb-5 text-lg font-semibold text-ink">Average price by store</h2>
        {storeAverages.length === 0 ? (
          <p className="py-12 text-center text-sm text-muted">No store averages yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={storeAverages}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
              <XAxis dataKey="store" tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: "#64748B" }} axisLine={false} tickLine={false} width={40} />
              <Tooltip />
              <Bar dataKey="avg" fill="#16A34A" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </motion.section>

      {data?.recent_drops?.length > 0 && (
        <section className="card p-5">
          <h2 className="mb-4 text-lg font-semibold text-ink">Recent drops</h2>
          <div className="space-y-2">
            {data.recent_drops.map((d) => (
              <Link
                key={`${d.product_id}-${d.store}`}
                to={`/products/${d.product_id}`}
                className="flex items-center justify-between rounded-xl border border-line px-4 py-3 hover:bg-canvas"
              >
                <div>
                  <p className="font-medium text-ink">{d.product}</p>
                  <p className="text-xs text-muted">{d.store}</p>
                </div>
                <p className="tabular font-semibold text-primary">-{formatINR(d.savings)}</p>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default Analytics;
