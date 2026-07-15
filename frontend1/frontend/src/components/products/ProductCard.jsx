import { Package, ArrowRight, Heart } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useWishlist } from "../../hooks/useWishlist";

function ProductCard({ product }) {
  const navigate = useNavigate();
  const { isWishlisted, toggleWishlist } = useWishlist();
  const wishlisted = isWishlisted(product.id);

  // The /products/ list endpoint doesn't return price data today (only
  // /products/{id}/prices/ does), so this badge only appears if the API
  // response happens to include a lowest-price field. It never fetches
  // a second endpoint per card — that would be a new N+1 request pattern,
  // which is exactly the kind of business-logic change that's out of scope here.
  const lowestPrice = product.lowest_price ?? product.current_price ?? null;

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.15 }}
      onClick={() => navigate(`/products/${product.id}`)}
      className="card group relative cursor-pointer p-6 transition-shadow hover:shadow-[var(--shadow-soft-lg)]"
    >
      <button
        onClick={(e) => {
          e.stopPropagation();
          toggleWishlist(product);
        }}
        aria-label={wishlisted ? "Remove from wishlist" : "Add to wishlist"}
        className="absolute right-4 top-4 z-10 flex h-9 w-9 items-center justify-center rounded-full bg-white/90 shadow-soft transition hover:scale-105 dark:bg-zinc-800/90"
      >
        <Heart
          size={16}
          className={wishlisted ? "fill-rose-500 text-rose-500" : "text-zinc-400"}
        />
      </button>

      <div className="mb-6 flex h-32 items-center justify-center rounded-xl bg-zinc-100 dark:bg-zinc-800">
        <Package size={52} className="text-brand-500" />
      </div>

      <h2 className="mb-1 truncate text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        {product.name}
      </h2>

      {lowestPrice && (
        <span className="mb-2 inline-block rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400">
          Lowest ₹{lowestPrice}
        </span>
      )}

      <p className="truncate text-sm text-zinc-500 dark:text-zinc-400">{product.brand}</p>
      <p className="mb-6 truncate text-sm text-zinc-400 dark:text-zinc-500">{product.category}</p>

      <div className="flex items-center justify-between">
        <span className="rounded-full bg-brand-50 px-3 py-1 text-sm font-medium text-brand-700 dark:bg-brand-500/10 dark:text-brand-300">
          View details
        </span>
        <ArrowRight size={18} className="text-zinc-400 transition group-hover:translate-x-1 group-hover:text-brand-600" />
      </div>
    </motion.div>
  );
}

export default ProductCard;
