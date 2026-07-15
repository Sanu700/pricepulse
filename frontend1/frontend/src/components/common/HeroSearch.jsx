import { useEffect, useRef, useState } from "react";
import { Search, X } from "lucide-react";
import { Link } from "react-router-dom";
import { searchSuggestions } from "../../services/productService";

function formatINR(value) {
  if (value == null) return null;
  return `₹${Number(value).toFixed(0)}`;
}

/**
 * Hero / navbar search with live suggestions from the products API.
 */
export default function HeroSearch({
  value,
  onChange,
  onSubmit,
  placeholder = "Search atta, milk, oil, snacks…",
  autoFocus = false,
  size = "lg",
}) {
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const wrapRef = useRef(null);
  const timer = useRef(null);

  useEffect(() => {
    function onDocClick(e) {
      if (!wrapRef.current?.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  useEffect(() => {
    const q = value?.trim() ?? "";
    if (q.length < 2) {
      setSuggestions([]);
      setOpen(false);
      return;
    }

    clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      setLoading(true);
      try {
        const rows = await searchSuggestions(q);
        setSuggestions(rows);
        setOpen(true);
      } catch {
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }, 220);

    return () => clearTimeout(timer.current);
  }, [value]);

  const pad = size === "lg" ? "py-4 pl-12 pr-12 text-base" : "py-2.5 pl-10 pr-10 text-sm";

  return (
    <div ref={wrapRef} className="relative w-full">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          setOpen(false);
          onSubmit?.(value);
        }}
        className="relative"
      >
        <Search
          className={`pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-muted ${
            size === "lg" ? "" : "left-3"
          }`}
          size={size === "lg" ? 20 : 16}
        />
        <input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => suggestions.length > 0 && setOpen(true)}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className={`input-field ${pad} shadow-sm`}
          aria-label="Search products"
          autoComplete="off"
        />
        {value && (
          <button
            type="button"
            onClick={() => {
              onChange("");
              setSuggestions([]);
              setOpen(false);
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-1 text-muted hover:bg-canvas hover:text-ink"
            aria-label="Clear search"
          >
            <X size={16} />
          </button>
        )}
      </form>

      {open && (
        <div className="absolute left-0 right-0 top-[calc(100%+6px)] z-50 overflow-hidden rounded-2xl border border-line bg-surface shadow-[var(--shadow-card-hover)]">
          {loading && (
            <p className="px-4 py-3 text-sm text-muted">Searching…</p>
          )}
          {!loading && suggestions.length === 0 && (
            <p className="px-4 py-3 text-sm text-muted">No matches — press Enter to browse all</p>
          )}
          {!loading &&
            suggestions.map((p) => (
              <Link
                key={p.id}
                to={`/products/${p.id}`}
                onClick={() => setOpen(false)}
                className="flex items-center justify-between gap-3 border-b border-line px-4 py-3 last:border-0 hover:bg-canvas"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-ink">{p.name}</p>
                  <p className="truncate text-xs text-muted">
                    {p.brand}
                    {p.cheapest_store ? ` · cheapest at ${p.cheapest_store}` : ""}
                  </p>
                </div>
                {p.lowest_price != null && (
                  <span className="tabular shrink-0 text-sm font-semibold text-primary">
                    {formatINR(p.lowest_price)}
                  </span>
                )}
              </Link>
            ))}
        </div>
      )}
    </div>
  );
}
