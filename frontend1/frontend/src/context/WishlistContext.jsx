import { createContext, useEffect, useState } from "react";

// UI-only wishlist. No backend endpoint exists for this yet, so it's
// persisted locally the same way auth tokens are (localStorage), following
// the existing project convention rather than introducing a new pattern.
export const WishlistContext = createContext();

const STORAGE_KEY = "wishlist";

export function WishlistProvider({ children }) {
  const [items, setItems] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) ?? [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }, [items]);

  const isWishlisted = (id) => items.some((p) => p.id === id);

  const toggleWishlist = (product) => {
    setItems((prev) =>
      prev.some((p) => p.id === product.id)
        ? prev.filter((p) => p.id !== product.id)
        : [...prev, product]
    );
  };

  return (
    <WishlistContext.Provider value={{ items, isWishlisted, toggleWishlist }}>
      {children}
    </WishlistContext.Provider>
  );
}
