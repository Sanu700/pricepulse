import ProductCard from "../../components/products/ProductCard";
import { useProducts } from "../../hooks/useProducts";
import { useState } from "react";
import SearchBar from "../../components/common/SearchBar";

function Products() {

    const { data, isLoading, error } = useProducts();
    const [search, setSearch] = useState("");
    const products = data ?? [];
    const filteredProducts = products.filter((product) =>
  product.name.toLowerCase().includes(search.toLowerCase())
   );

    if (isLoading)
        return <h2>Loading...</h2>;

    if (error)
        return <h2>Error loading products.</h2>;

    return (
  <div>

    <div className="mb-8 flex items-center justify-between">

      <div>

        <h1 className="text-4xl font-bold">
          Products
        </h1>

        <p className="mt-2 text-gray-500">
          Compare prices across stores.
        </p>

      </div>

    </div>

    <div className="mb-8">
      <SearchBar
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
    </div>

    <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">

      {filteredProducts.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
        />
      ))}

    </div>

  </div>
);
}

export default Products;