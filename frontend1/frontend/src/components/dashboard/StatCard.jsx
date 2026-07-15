import { motion } from "framer-motion";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";

function StatCard({ title, value, icon: Icon, trend, trendLabel }) {
  const isUp = typeof trend === "number" && trend >= 0;

  return (
    <motion.div whileHover={{ y: -2 }} transition={{ duration: 0.15 }} className="card p-5">
      <div className="flex items-start justify-between">
        <p className="text-sm font-medium text-muted">{title}</p>
        {Icon && (
          <span className="rounded-xl bg-primary-soft p-2 text-primary">
            <Icon size={16} />
          </span>
        )}
      </div>
      <h2 className="tabular mt-3 text-2xl font-bold tracking-tight text-ink sm:text-3xl">{value}</h2>
      {typeof trend === "number" && (
        <div
          className={`mt-2 flex items-center gap-1 text-sm font-medium ${
            isUp ? "text-primary" : "text-danger"
          }`}
        >
          {isUp ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          <span>{Math.abs(trend)}%</span>
          {trendLabel && <span className="font-normal text-muted">{trendLabel}</span>}
        </div>
      )}
    </motion.div>
  );
}

export default StatCard;
