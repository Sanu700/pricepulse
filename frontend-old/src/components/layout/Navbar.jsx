import { Search, ShoppingBag } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

function Navbar() {
  const { logout, isAuthenticated } = useAuth();

  return (
    <nav className="flex items-center justify-between border-b bg-white px-8 py-4 shadow-sm">
      <Link to="/" className="text-2xl font-bold text-purple-600">
        PricePulse
      </Link>

      <div className="relative w-96">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
          size={18}
        />
        <input
          type="text"
          placeholder="Search products..."
          className="w-full rounded-lg border py-2 pl-10 pr-4 focus:border-purple-500 focus:outline-none"
        />
      </div>

      <div className="flex items-center gap-6">
        <Link to="/products" className="flex items-center gap-2">
          <ShoppingBag size={20} />
          Products
        </Link>

        {isAuthenticated && (
          <button
            onClick={logout}
            className="rounded-lg bg-red-500 px-4 py-2 text-white hover:bg-red-600"
          >
            Logout
          </button>
        )}
      </div>
    </nav>
  );
}

export default Navbar;