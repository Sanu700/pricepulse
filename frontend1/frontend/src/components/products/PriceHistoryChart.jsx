import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const date = label ? new Date(label).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }) : "";
  return (
    <div className="rounded-xl border border-line bg-surface px-3 py-2 text-sm shadow-[var(--shadow-card-hover)]">
      <p className="text-xs text-muted">{date}</p>
      <p className="tabular font-semibold text-primary">₹{payload[0].value}</p>
      {payload[0].payload?.store && (
        <p className="text-xs text-muted">{payload[0].payload.store}</p>
      )}
    </div>
  );
}

function PriceHistoryChart({ data, title = "Price history" }) {
  const chartData = (data ?? []).map((row) => ({
    ...row,
    price: Number(row.price),
  }));

  if (chartData.length === 0) {
    return (
      <div className="card flex h-72 items-center justify-center p-6">
        <p className="text-sm text-muted">No price history yet — check back after the next refresh.</p>
      </div>
    );
  }

  return (
    <div className="card p-5 sm:p-6">
      <h2 className="mb-5 text-lg font-semibold text-ink">{title}</h2>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#16A34A" stopOpacity={0.28} />
              <stop offset="100%" stopColor="#16A34A" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
          <XAxis
            dataKey="recorded_at"
            tickFormatter={(v) => {
              try {
                return new Date(v).toLocaleDateString("en-IN", { day: "numeric", month: "short" });
              } catch {
                return String(v).slice(5, 10);
              }
            }}
            tick={{ fontSize: 12, fill: "#64748B" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#64748B" }}
            axisLine={false}
            tickLine={false}
            width={48}
            tickFormatter={(v) => `₹${v}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="price"
            stroke="#16A34A"
            strokeWidth={2.5}
            fill="url(#priceGradient)"
            animationDuration={700}
            dot={false}
            activeDot={{ r: 5, fill: "#16A34A", stroke: "#fff", strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PriceHistoryChart;
