import { useParams } from "react-router-dom";
import { useProduct } from "../../hooks/useProducts";
import { useProductPrices } from "../../hooks/useProductPrices";

function ProductDetails() {
  const { id } = useParams();

  const { data, isLoading, error } = useProduct(id);
  const { data: prices, isLoading: pricesLoading } = useProductPrices(id);
  if (isLoading) return <h1>Loading...</h1>;

  if (error) return <h1>Something went wrong.</h1>;

  const product = data ?? {};
  const currentPrices = prices ?? [];

  return (
    <div className="grid grid-cols-2 gap-10">

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
        <div className="mt-8 rounded-xl border p-5">

    <h2 className="text-xl font-semibold mb-4">
        Current Prices
    </h2>

    {pricesLoading ? (
        <p>Loading prices...</p>
    ) : (

        <div className="space-y-3">

            {currentPrices.map((price) => (

                <div
                    key={price.store}
                    className="flex justify-between border-b pb-2"
                >
                    <span>{price.store}</span>

                    <span className="font-semibold">
                        ₹{price.price}
                    </span>

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