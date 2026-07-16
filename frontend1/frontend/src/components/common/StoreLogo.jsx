import { useState } from "react";

/**
 * Self-hosted store logo (public/logos/*.svg) with a colored initials fallback.
 * No remote CDN dependencies.
 */
const STORE_STYLES = {
  blinkit: "bg-yellow-100 text-yellow-800",
  zepto: "bg-violet-100 text-violet-800",
  instamart: "bg-orange-100 text-orange-800",
  bigbasket: "bg-lime-100 text-lime-800",
};

function slugify(name) {
  const slug = (name || "").trim().toLowerCase().replace(/\s+/g, "-");
  return slug === "swiggy-instamart" ? "instamart" : slug;
}

function StoreLogo({ name, src, size = 24, className = "" }) {
  const [failed, setFailed] = useState(false);
  const slug = slugify(name);
  const logoSrc = src || `/logos/${slug}.svg`;

  if (failed || !slug) {
    const initials = (name || "?").slice(0, 2).toUpperCase();
    return (
      <span
        className={`inline-flex items-center justify-center rounded-lg text-[10px] font-bold ${
          STORE_STYLES[slug] ?? "bg-slate-100 text-slate-700"
        } ${className}`}
        style={{ width: size, height: size }}
        aria-label={name}
      >
        {initials}
      </span>
    );
  }

  return (
    <img
      src={logoSrc}
      alt={name || "store"}
      width={size}
      height={size}
      className={`object-contain ${className}`}
      loading="lazy"
      onError={() => setFailed(true)}
    />
  );
}

export default StoreLogo;
