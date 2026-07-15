import { useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Heart, Bell, Trash2, Package } from "lucide-react";
import { toast } from "sonner";
import { useWishlist } from "../../hooks/useWishlist";
import { createPriceAlert } from "../../services/authService";
import EmptyState from "../../components/common/EmptyState";

function AlertModal({ product, onClose }) {
  const [threshold, setThreshold] = useState(
    product.lowest_price ? String(Math.floor(Number(product.lowest_price) * 0.95)) : ""
  );
  const [email, setEmail] = useState("");
  const [saving, setSaving] = useState(false);

  async function save() {
    if (!threshold) {
      toast.error("Enter a target price");
      return;
    }
    setSaving(true);
    try {
      await createPriceAlert({
        product: product.id,
        target_price: threshold,
        email,
      });
      toast.success("Alert saved — you'll be notified on drops");
      onClose();
    } catch {
      toast.error("Could not save alert");
    } finally {
      setSaving(false);
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96 }}
        onClick={(e) => e.stopPropagation()}
        className="card w-full max-w-sm p-6"
      >
        <div className="mb-4 flex items-center gap-2">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-soft text-primary">
            <Bell size={18} />
          </span>
          <div>
            <h3 className="font-semibold text-ink">Set a price alert</h3>
            <p className="text-sm text-muted">{product.name}</p>
          </div>
        </div>

        <label className="mb-1 block text-sm font-medium text-muted">Notify me below</label>
        <div className="relative mb-3">
          <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted">₹</span>
          <input
            type="number"
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
            className="input-field pl-8"
          />
        </div>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email (optional)"
          className="input-field mb-6"
        />

        <div className="flex gap-3">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">
            Cancel
          </button>
          <button type="button" onClick={save} disabled={saving} className="btn-primary flex-1">
            {saving ? "Saving…" : "Save alert"}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

function Wishlist() {
  const { items, toggleWishlist } = useWishlist();
  const [alertFor, setAlertFor] = useState(null);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-ink">Wishlist</h1>
        <p className="mt-1 text-muted">Products you're watching for a better price.</p>
      </div>

      {items.length === 0 ? (
        <EmptyState
          icon={Heart}
          title="Your wishlist is empty"
          description="Tap the heart on any product to save it here and set price alerts."
          action={
            <Link to="/products" className="btn-primary">
              Browse products
            </Link>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <AnimatePresence>
            {items.map((product) => (
              <motion.div
                key={product.id}
                layout
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.96 }}
                className="card p-5"
              >
                <Link to={`/products/${product.id}`} className="mb-4 flex h-24 items-center justify-center rounded-xl bg-canvas">
                  {product.image_url ? (
                    <img src={product.image_url} alt="" className="h-full object-contain p-2" />
                  ) : (
                    <Package size={36} className="text-slate-300" />
                  )}
                </Link>
                <h3 className="truncate font-semibold text-ink">{product.name}</h3>
                <p className="mb-4 truncate text-sm text-muted">{product.brand}</p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setAlertFor(product)}
                    className="flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-primary-soft py-2 text-sm font-medium text-primary-dark hover:bg-primary/15"
                  >
                    <Bell size={14} /> Alert
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      toggleWishlist(product);
                      toast.success("Removed from wishlist");
                    }}
                    aria-label="Remove from wishlist"
                    className="flex items-center justify-center rounded-xl border border-line p-2 text-muted hover:text-danger"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      <AnimatePresence>
        {alertFor && <AlertModal product={alertFor} onClose={() => setAlertFor(null)} />}
      </AnimatePresence>
    </div>
  );
}

export default Wishlist;
