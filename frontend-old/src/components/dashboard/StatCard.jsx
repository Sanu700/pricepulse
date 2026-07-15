function StatCard({ title, value }) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

      <p className="text-gray-500">
        {title}
      </p>

      <h2 className="mt-4 text-4xl font-bold text-purple-600">
        {value}
      </h2>

    </div>
  );
}

export default StatCard;