import { useParams } from "react-router-dom";
import { useProduct } from "../../hooks/useProducts";
import { useProductPrices } from "../../hooks/useProductPrices";
import { useProductHistory } from "../../hooks/useProductHistory";
import PriceHistoryChart from "../../components/products/PriceHistoryChart";

function ProductDetails() {
  const { id } = useParams();

  const { data, isLoading, error } = useProduct(id);
  const { data: prices, isLoading: pricesLoading } = useProductPrices(id);
  const { data: history, isLoading: historyLoading } = useProductHistory(id);
  if (isLoading) return <h1>Loading...</h1>;

  if (error) return <h1>Something went wrong.</h1>;

  const product = data ?? {};
  const currentPrices = prices ?? [];
  const priceHistory = history ?? [];

  return (
    <div className="grid grid-cols-2 gap-10">
      {priceHistory.length > 0 && (
        <div className="col-span-2 mb-8">
          <PriceHistoryChart data={priceHistory} />
        </div>
      )}

      <div className="flex items-center justify-center rounded-xl border bg-gray-100 h-96">
        <p className="text-gray-500">Product Image</p>
      </div>

      <div>

        <h1 className="text-4xl font-bold">
          {product.name}
        </h1>

        <div className="mt-6 space-y-3">

          <p>
            <span className="font-semibold">Brand:</span> {product.brand}
          </p>

          <p>
            <span className="font-semibold">Category:</span> {product.category}
          </p>

          <p>
            <span className="font-semibold">Barcode:</span> {product.barcode}
          </p>

        </div>

        <div className="mt-8 rounded-xl border p-5">

          <h2 className="text-xl font-semibold mb-3">
            Description
          </h2>

          <p>
            {product.description}
          </p>

        
        {currentPrices.length > 0 && (

<div className="mb-6 rounded-lg bg-green-100 p-4">

    <p className="font-semibold">

        🏆 Lowest Price

    </p>

    <p>

        {currentPrices[0].store} • ₹{currentPrices[0].price}

    </p>

</div>

)}</div>
        <div className="mt-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

  <h2 className="mb-6 text-2xl font-bold">
    Current Prices
  </h2>

  {pricesLoading ? (
    <p>Loading prices...</p>
  ) : (
    <div className="space-y-4">

      {prices.map((price, index) => (

        <div
          key={price.store}
          className="flex items-center justify-between rounded-xl border p-4 hover:bg-gray-50"
        >

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 font-bold text-purple-600">
              {index + 1}
            </div>

            <div>

              <h3 className="font-semibold">
                {price.store}
              </h3>

              <p className="text-sm text-gray-500">
                {price.in_stock ? "In Stock" : "Out of Stock"}
              </p>

            </div>

          </div>

          <div className="text-2xl font-bold text-purple-600">
            ₹{price.price}
          </div>

        </div>

      ))}

    </div>
  )}

</div>


      </div>

    </div>
  );
}

export default ProductDetails;