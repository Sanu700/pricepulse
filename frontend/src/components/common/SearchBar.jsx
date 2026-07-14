import { Search } from "lucide-react";

function SearchBar({ value, onChange }) {
  return (
    <div className="relative">
      <Search
        className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
        size={18}
      />

      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder="Search products..."
        className="w-full rounded-lg border py-2 pl-10 pr-4"
      />
    </div>
  );
}

export default SearchBar;