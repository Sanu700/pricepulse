import { motion } from "framer-motion";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";

function StatCard({ title, value, icon: Icon, trend, trendLabel }) {
  const isUp = typeof trend === "number" && trend >= 0;

  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.15 }}
      className="card p-6"
    >
      <div className="flex items-start justify-between">
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">{title}</p>
        {Icon && (
          <span className="rounded-lg bg-brand-50 p-2 text-brand-600 dark:bg-brand-500/10 dark:text-brand-400">
            <Icon size={16} />
          </span>
        )}
      </div>

      <h2 className="tabular mt-4 text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
        {value}
      </h2>

      {typeof trend === "number" && (
        <div
          className={`mt-3 flex items-center gap-1 text-sm font-medium ${
            isUp ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"
          }`}
        >
          {isUp ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          <span>{Math.abs(trend)}%</span>
          {trendLabel && <span className="font-normal text-zinc-400">{trendLabel}</span>}
        </div>
      )}
    </motion.div>
  );
}

export default StatCard;
