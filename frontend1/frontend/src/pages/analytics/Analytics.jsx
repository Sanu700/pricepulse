import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Store, PiggyBank } from "lucide-react";
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
import StatCard from "../../components/dashboard/StatCard";
import ComingSoon from "../../components/common/ComingSoon";

// Entirely mock data — no analytics endpoint exists on the backend yet.
const monthlyTrend = [
  { month: "Feb", avg: 412 },
  { month: "Mar", avg: 398 },
  { month: "Apr", avg: 405 },
  { month: "May", avg: 389 },
  { month: "Jun", avg: 371 },
  { month: "Jul", avg: 360 },
];

const storeAverages = [
  { store: "BigBasket", avg: 388 },
  { store: "Blinkit", avg: 402 },
  { store: "Zepto", avg: 395 },
];

function Analytics() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
            Analytics
          </h1>
          <p className="mt-2 text-zinc-500 dark:text-zinc-400">
            Trends across stores and products.
          </p>
        </div>
        <ComingSoon label="Mock data" />
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <StatCard title="Avg. basket price" value="₹360" icon={PiggyBank} trend={-4.2} trendLabel="vs last month" />
        <StatCard title="Cheapest store" value="BigBasket" icon={Store} />
        <StatCard title="Price volatility" value="Low" icon={TrendingUp} />
      </div>

      <motion.section initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card p-6">
        <div className="mb-6 flex items-center gap-2">
          <BarChart3 size={18} className="text-brand-600" />
          <h2 className="text-lg font-semibold">Monthly average price trend</h2>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={monthlyTrend}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-zinc-200 dark:stroke-zinc-800" />
            <XAxis dataKey="month" tick={{ fontSize: 12, fill: "#a1a1aa" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 12, fill: "#a1a1aa" }} axisLine={false} tickLine={false} width={40} />
            <Tooltip />
            <Line type="monotone" dataKey="avg" stroke="#7c3aed" strokeWidth={2.5} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </motion.section>

      <motion.section initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card p-6">
        <h2 className="mb-6 text-lg font-semibold">Average price by store</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={storeAverages}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-zinc-200 dark:stroke-zinc-800" />
            <XAxis dataKey="store" tick={{ fontSize: 12, fill: "#a1a1aa" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 12, fill: "#a1a1aa" }} axisLine={false} tickLine={false} width={40} />
            <Tooltip />
            <Bar dataKey="avg" fill="#7c3aed" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </motion.section>
    </div>
  );
}

export default Analytics;
