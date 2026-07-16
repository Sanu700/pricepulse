import { useState } from "react";

const PLACEHOLDER = "/images/product-placeholder.svg";

/**
 * Product image with graceful fallback — never leaves a broken <img>.
 * On error (or when no src is provided) it renders the local placeholder,
 * so we never show random remote imagery or broken image icons.
 */
function ProductImage({ src, alt = "", className = "h-full w-full object-contain p-3" }) {
  const [failed, setFailed] = useState(false);
  const resolvedSrc = !src || failed ? PLACEHOLDER : src;

  return (
    <img
      src={resolvedSrc}
      alt={alt || "Product image"}
      className={className}
      loading="lazy"
      decoding="async"
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
    />
  );
}

export default ProductImage;
