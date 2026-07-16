import { ArrowRight, Heart, TrendingDown, TrendingUp, Minus } from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { useWishlist } from "../../hooks/useWishlist";
import ProductImage from "../common/ProductImage";
import StoreLogo from "../common/StoreLogo";

function formatINR(value) {
  if (value == null || value === "") return "—";
  return `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

function extractUnit(name) {
  const match = (name || "").match(/(\d+(?:\.\d+)?)\s?(kg|g|gm|ml|l|ltr|pack|pcs)\b/i);
  return match ? `${match[1]}${match[2].toLowerCase()}` : null;
}

function TrendIcon({ trend }) {
  if (trend === "down") return <TrendingDown size={14} className="text-primary" aria-hidden />;
  if (trend === "up") return <TrendingUp size={14} className="text-danger" aria-hidden />;
  if (trend === "flat") return <Minus size={14} className="text-muted" aria-hidden />;
  return null;
}

function ProductCard({ product }) {
  const { isWishlisted, toggleWishlist } = useWishlist();
  const wishlisted = isWishlisted(product.id);

  const lowest = product.lowest_price;
  const highest = product.highest_price;
  const savings = product.savings;
  const store = product.cheapest_store;
  const unit = extractUnit(product.name);

  return (
    <motion.article
      whileHover={{ y: -3 }}
      transition={{ duration: 0.15 }}
      className="card card-hover group relative overflow-hidden p-5"
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
        <Heart size={16} className={wishlisted ? "fill-danger text-danger" : "text-muted"} />
      </button>

      <Link
        to={`/products/${product.id}`}
        className="block rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
        aria-label={`View ${product.name}`}
      >
        <div className="mb-4 flex h-36 items-center justify-center overflow-hidden rounded-xl bg-canvas">
          <ProductImage src={product.image_url} alt={product.name} />
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

        <p className="mb-3 flex items-center gap-1.5 truncate text-xs text-muted">
          <span className="truncate">
            {product.brand}
            {product.category ? ` · ${product.category}` : ""}
          </span>
          {unit && (
            <span className="shrink-0 rounded-md bg-canvas px-1.5 py-0.5 text-[10px] font-medium text-slate-600">
              {unit}
            </span>
          )}
        </p>

        <div className="mb-4 flex items-end justify-between gap-2">
          <div className="flex items-center gap-2">
            {store && (
              <span className="flex items-center gap-1.5 rounded-lg bg-canvas px-2 py-1 text-[11px] font-semibold text-slate-700">
                <StoreLogo name={store} size={16} />
                {store}
              </span>
            )}
            <TrendIcon trend={product.trend} />
          </div>
          <div className="text-right leading-tight">
            <span className="tabular block text-lg font-bold text-ink">{formatINR(lowest)}</span>
            {highest != null && Number(highest) > Number(lowest) && (
              <span className="tabular text-[11px] text-muted line-through">
                {formatINR(highest)}
              </span>
            )}
          </div>
        </div>
      </Link>

      <Link to={`/products/${product.id}`} className="btn-primary w-full !py-2 text-center text-xs">
        Compare <ArrowRight size={14} />
      </Link>
    </motion.article>
  );
}

export default ProductCard;
