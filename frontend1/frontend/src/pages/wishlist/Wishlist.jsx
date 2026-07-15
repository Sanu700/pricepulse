import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Heart, Bell, Trash2, Package } from "lucide-react";
import { toast } from "sonner";
import { useWishlist } from "../../hooks/useWishlist";
import EmptyState from "../../components/common/EmptyState";

// Wishlist itself is UI-only and localStorage-backed (see WishlistContext).
// Alerts have no backend support — the modal below is a UI mock only.
function AlertModal({ product, onClose }) {
  const [threshold, setThreshold] = useState("");

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-900/50 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        onClick={(e) => e.stopPropagation()}
        className="card w-full max-w-sm p-6"
      >
        <div className="mb-4 flex items-center gap-2">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-400">
            <Bell size={18} />
          </span>
          <div>
            <h3 className="font-semibold">Set a price alert</h3>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">{product.name}</p>
          </div>
        </div>

        <label className="mb-1 block text-sm font-medium text-zinc-600 dark:text-zinc-400">
          Notify me below
        </label>
        <div className="relative mb-6">
          <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-400">₹</span>
          <input
            type="number"
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
            placeholder="50"
            className="w-full rounded-xl border border-zinc-200 bg-white py-2.5 pl-8 pr-4 text-sm outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-zinc-700 dark:bg-zinc-900"
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 rounded-xl border border-zinc-200 py-2.5 text-sm font-medium text-zinc-600 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              toast.success("Alert saved (demo only — no notifications will be sent)");
              onClose();
            }}
            className="flex-1 rounded-xl bg-brand-600 py-2.5 text-sm font-semibold text-white hover:bg-brand-700"
          >
            Save alert
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
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
          Wishlist
        </h1>
        <p className="mt-2 text-zinc-500 dark:text-zinc-400">
          Products you're keeping an eye on.
        </p>
      </div>

      {items.length === 0 ? (
        <EmptyState
          icon={Heart}
          title="Your wishlist is empty"
          description="Tap the heart on any product to save it here and set price alerts."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <AnimatePresence>
            {items.map((product) => (
              <motion.div
                key={product.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="card p-5"
              >
                <div className="mb-4 flex h-24 items-center justify-center rounded-xl bg-zinc-100 dark:bg-zinc-800">
                  <Package size={36} className="text-brand-500" />
                </div>
                <h3 className="truncate font-semibold text-zinc-900 dark:text-zinc-100">{product.name}</h3>
                <p className="mb-4 truncate text-sm text-zinc-500 dark:text-zinc-400">{product.brand}</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setAlertFor(product)}
                    className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-brand-50 py-2 text-sm font-medium text-brand-700 hover:bg-brand-100 dark:bg-brand-500/10 dark:text-brand-300"
                  >
                    <Bell size={14} /> Alert
                  </button>
                  <button
                    onClick={() => toggleWishlist(product)}
                    aria-label="Remove from wishlist"
                    className="flex items-center justify-center rounded-lg border border-zinc-200 p-2 text-zinc-400 hover:bg-zinc-50 hover:text-rose-500 dark:border-zinc-700 dark:hover:bg-zinc-800"
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
