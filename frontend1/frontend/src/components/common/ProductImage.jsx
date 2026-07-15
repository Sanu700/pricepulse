import { useState } from "react";
import { Package } from "lucide-react";

/**
 * Product image with graceful fallback — never leaves a broken <img>.
 */
function ProductImage({ src, alt = "", className = "h-full w-full object-contain p-3", iconSize = 48 }) {
  const [failed, setFailed] = useState(false);
  const showImage = Boolean(src) && !failed;

  if (!showImage) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-canvas">
        <Package size={iconSize} className="text-slate-300" aria-hidden />
        <span className="sr-only">{alt || "No product image"}</span>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      loading="lazy"
      decoding="async"
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
    />
  );
}

export default ProductImage;
