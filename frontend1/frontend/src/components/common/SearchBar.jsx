import { Search, X } from "lucide-react";

function SearchBar({ value, onChange, placeholder = "Search products..." }) {
  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-muted" size={18} />
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="input-field py-3 pl-10 pr-10"
      />
      {value && (
        <button
          type="button"
          onClick={() => onChange({ target: { value: "" } })}
          aria-label="Clear search"
          className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted hover:text-ink"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}

export default SearchBar;
