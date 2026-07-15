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
  return (
    <div className="card px-3 py-2 text-sm shadow-soft-lg">
      <p className="text-zinc-400">{label?.slice?.(5, 10) ?? label}</p>
      <p className="tabular font-semibold text-brand-600 dark:text-brand-400">
        ₹{payload[0].value}
      </p>
    </div>
  );
}

function PriceHistoryChart({ data }) {
  return (
    <div className="card p-6">
      <h2 className="mb-6 text-xl font-semibold">Price history</h2>

      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#7c3aed" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" className="stroke-zinc-200 dark:stroke-zinc-800" />

          <XAxis
            dataKey="recorded_at"
            tickFormatter={(value) => value.slice(5, 10)}
            tick={{ fontSize: 12, fill: "#a1a1aa" }}
            axisLine={false}
            tickLine={false}
          />

          <YAxis
            tick={{ fontSize: 12, fill: "#a1a1aa" }}
            axisLine={false}
            tickLine={false}
            width={48}
          />

          <Tooltip content={<CustomTooltip />} />

          <Area
            type="monotone"
            dataKey="price"
            stroke="#7c3aed"
            strokeWidth={2.5}
            fill="url(#priceGradient)"
            animationDuration={800}
            dot={false}
            activeDot={{ r: 5, fill: "#7c3aed" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PriceHistoryChart;
