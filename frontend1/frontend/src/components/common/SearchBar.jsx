import { Search, X } from "lucide-react";

function SearchBar({ value, onChange, placeholder = "Search products..." }) {
  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-400" size={18} />
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full rounded-xl border border-zinc-200 bg-white py-3 pl-10 pr-10 text-sm outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-zinc-700 dark:bg-zinc-900"
      />
      {value && (
        <button
          onClick={() => onChange({ target: { value: "" } })}
          aria-label="Clear search"
          className="absolute right-3.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}

export default SearchBar;
