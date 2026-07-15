import { Package, ArrowRight, Heart, TrendingDown, TrendingUp, Minus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { useWishlist } from "../../hooks/useWishlist";

const STORE_COLORS = {
  Blinkit: "bg-yellow-100 text-yellow-800",
  Zepto: "bg-purple-100 text-purple-800",
  Instamart: "bg-orange-100 text-orange-800",
};

function formatINR(value) {
  if (value == null || value === "") return "—";
  return `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

function TrendIcon({ trend }) {
  if (trend === "down") return <TrendingDown size={14} className="text-primary" />;
  if (trend === "up") return <TrendingUp size={14} className="text-danger" />;
  if (trend === "flat") return <Minus size={14} className="text-muted" />;
  return null;
}

function ProductCard({ product }) {
  const navigate = useNavigate();
  const { isWishlisted, toggleWishlist } = useWishlist();
  const wishlisted = isWishlisted(product.id);

  const lowest = product.lowest_price;
  const savings = product.savings;
  const store = product.cheapest_store;

  return (
    <motion.article
      whileHover={{ y: -3 }}
      transition={{ duration: 0.15 }}
      onClick={() => navigate(`/products/${product.id}`)}
      className="card card-hover group relative cursor-pointer overflow-hidden p-5"
    >
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          toggleWishlist(product);
          toast.success(wishlisted ? "Removed from wishlist" : "Saved to wishlist");
        }}
        aria-label={wishlisted ? "Remove from wishlist" : "Add to wishlist"}
        className="absolute right-3 top-3 z-10 flex h-9 w-9 items-center justify-center rounded-full border border-line bg-surface/95 shadow-sm transition hover:scale-105"
      >
        <Heart
          size={16}
          className={wishlisted ? "fill-danger text-danger" : "text-muted"}
        />
      </button>

      <div className="mb-4 flex h-36 items-center justify-center overflow-hidden rounded-xl bg-canvas">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="h-full w-full object-contain p-3"
            loading="lazy"
          />
        ) : (
          <Package size={48} className="text-slate-300" />
        )}
      </div>

      <div className="mb-2 flex flex-wrap gap-1.5">
        {lowest != null && (
          <span className="badge badge-cheap">Cheapest {formatINR(lowest)}</span>
        )}
        {savings != null && Number(savings) > 0 && (
          <span className="badge badge-accent">Save {formatINR(savings)}</span>
        )}
      </div>

      <h2 className="mb-1 line-clamp-2 text-[15px] font-semibold leading-snug text-ink">
        {product.name}
      </h2>

      <p className="mb-3 truncate text-xs text-muted">
        {product.brand}
        {product.category ? ` · ${product.category}` : ""}
      </p>

      <div className="mb-4 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {store && (
            <span
              className={`rounded-lg px-2 py-0.5 text-[11px] font-semibold ${
                STORE_COLORS[store] ?? "bg-slate-100 text-slate-700"
              }`}
            >
              {store}
            </span>
          )}
          <TrendIcon trend={product.trend} />
        </div>
        <span className="tabular text-lg font-bold text-ink">{formatINR(lowest)}</span>
      </div>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/products/${product.id}`);
          }}
          className="btn-primary flex-1 !py-2 text-xs"
        >
          Compare <ArrowRight size={14} />
        </button>
      </div>
    </motion.article>
  );
}

export default ProductCard;
