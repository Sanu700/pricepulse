import { Package, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

function ProductCard({ product }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/products/${product.id}`)}
      className="group cursor-pointer rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
    >
      <div className="mb-6 flex h-32 items-center justify-center rounded-xl bg-gray-100">
        <Package size={60} className="text-purple-500" />
      </div>

      <h2 className="mb-2 text-xl font-bold text-gray-900">
        {product.name}
      </h2>

      <p className="text-gray-500">
        {product.brand}
      </p>

      <p className="mb-6 text-gray-500">
        {product.category}
      </p>

      <div className="flex items-center justify-between">
        <span className="rounded-full bg-purple-100 px-3 py-1 text-sm font-medium text-purple-700">
          View Details
        </span>

        <ArrowRight
          size={18}
          className="transition group-hover:translate-x-1"
        />
      </div>
    </div>
  );
}

export default ProductCard;