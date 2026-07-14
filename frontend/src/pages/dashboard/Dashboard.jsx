import { useProducts } from "../../hooks/useProducts";
import StatCard from "../../components/dashboard/StatCard";

function Dashboard() {
  const { data, isLoading } = useProducts();
  const products = data ?? [];

  if (isLoading) return <h1>Loading...</h1>;

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold">Dashboard</h1>

      <div className="grid gap-6 md:grid-cols-3">

    <StatCard
        title="Products"
        value={data.length}
    />

    <StatCard
        title="Stores"
        value="2"
    />

    <StatCard
        title="Tracking"
        value="24/7"
    />

</div>
    </div>
  );
}

export default Dashboard;