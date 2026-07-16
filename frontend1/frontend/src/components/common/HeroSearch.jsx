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
  const [focused, setFocused] = useState(false);
  const [loading, setLoading] = useState(false);
  const wrapRef = useRef(null);
  const timer = useRef(null);
  const requestIdRef = useRef(0);
  const query = value?.trim() ?? "";
  const showDropdown = focused && query.length >= 2;

  useEffect(() => {
    function onDocClick(e) {
      if (!wrapRef.current?.contains(e.target)) setFocused(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  useEffect(() => {
    if (query.length < 2) {
      return;
    }

    clearTimeout(timer.current);
    const requestId = ++requestIdRef.current;
    timer.current = setTimeout(async () => {
      setLoading(true);
      try {
        const rows = await searchSuggestions(query);
        if (requestId === requestIdRef.current) {
          setSuggestions(rows);
        }
      } catch {
        if (requestId === requestIdRef.current) {
          setSuggestions([]);
        }
      } finally {
        if (requestId === requestIdRef.current) {
          setLoading(false);
        }
      }
    }, 220);

    return () => clearTimeout(timer.current);
  }, [query]);

  const pad = size === "lg" ? "py-4 pl-12 pr-12 text-base" : "py-2.5 pl-10 pr-10 text-sm";

  return (
    <div ref={wrapRef} className="relative w-full">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          setFocused(false);
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
          onFocus={() => setFocused(true)}
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
              setFocused(false);
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-1 text-muted hover:bg-canvas hover:text-ink"
            aria-label="Clear search"
          >
            <X size={16} />
          </button>
        )}
      </form>

      {showDropdown && (
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
                onClick={() => setFocused(false)}
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
