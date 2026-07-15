import { useState } from "react";
import { Search, ShoppingBag, LogOut, Moon, Sun, Menu, X, Sparkles, Wallet, Heart, LayoutDashboard, User } from "lucide-react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../../hooks/useAuth";
import { useTheme } from "../../hooks/useTheme";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/products", label: "Products", icon: ShoppingBag },
  { to: "/analytics", label: "Analytics", icon: Sparkles },
  { to: "/wishlist", label: "Wishlist", icon: Heart },
  { to: "/basket", label: "Basket", icon: Wallet },
];

function NavItem({ to, label, icon: Icon, end, onClick }) {
  return (
    <NavLink
      to={to}
      end={end}
      onClick={onClick}
      className={({ isActive }) =>
        `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
          isActive
            ? "bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-300"
            : "text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
        }`
      }
    >
      <Icon size={16} />
      {label}
    </NavLink>
  );
}

function Navbar() {
  const { logout, isAuthenticated } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const [query, setQuery] = useState("");
  const [mobileOpen, setMobileOpen] = useState(false);

  function handleSearchSubmit(e) {
    e.preventDefault();
    const trimmed = query.trim();
    navigate(trimmed ? `/products?q=${encodeURIComponent(trimmed)}` : "/products");
    setMobileOpen(false);
  }

  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200/70 dark:border-zinc-800">
      <nav className="glass">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 sm:px-6 lg:px-8">
          <Link to="/" className="flex shrink-0 items-center gap-2">
            <span className="relative flex h-8 w-8 items-center justify-center rounded-xl bg-brand-600 text-white shadow-soft">
              <motion.span
                className="absolute inset-0 rounded-xl bg-brand-500"
                animate={{ opacity: [0.6, 0, 0.6], scale: [1, 1.5, 1] }}
                transition={{ duration: 2.2, repeat: Infinity, ease: "easeOut" }}
              />
              <span className="relative text-sm font-bold">P</span>
            </span>
            <span className="hidden text-lg font-bold tracking-tight sm:inline">
              Price<span className="text-brand-600">Pulse</span>
            </span>
          </Link>

          <form onSubmit={handleSearchSubmit} className="relative hidden max-w-md flex-1 md:block">
            <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={16} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search products, brands, categories..."
              className="w-full rounded-xl border border-zinc-200 bg-white/80 py-2 pl-9 pr-4 text-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-zinc-700 dark:bg-zinc-900/80 dark:placeholder:text-zinc-500"
            />
          </form>

          <div className="ml-auto hidden items-center gap-1 lg:flex">
            {links.map((l) => (
              <NavItem key={l.to} {...l} />
            ))}
          </div>

          <div className="ml-auto flex items-center gap-2 lg:ml-2">
            <button
              onClick={toggleTheme}
              aria-label="Toggle theme"
              className="rounded-lg p-2 text-zinc-500 transition hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
            >
              {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            </button>

            <Link
              to="/profile"
              className="hidden rounded-lg p-2 text-zinc-500 transition hover:bg-zinc-100 hover:text-zinc-900 sm:block dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-zinc-100"
              aria-label="Profile"
            >
              <User size={18} />
            </Link>

            {isAuthenticated && (
              <button
                onClick={logout}
                className="hidden items-center gap-1.5 rounded-lg bg-zinc-900 px-3 py-2 text-sm font-medium text-white transition hover:bg-zinc-700 sm:flex dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200"
              >
                <LogOut size={15} />
                Logout
              </button>
            )}

            <button
              onClick={() => setMobileOpen((v) => !v)}
              className="rounded-lg p-2 text-zinc-500 hover:bg-zinc-100 lg:hidden dark:text-zinc-400 dark:hover:bg-zinc-800"
              aria-label="Toggle menu"
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        <AnimatePresence>
          {mobileOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden border-t border-zinc-200 lg:hidden dark:border-zinc-800"
            >
              <div className="space-y-3 px-4 py-4">
                <form onSubmit={handleSearchSubmit} className="relative">
                  <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={16} />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search products..."
                    className="w-full rounded-xl border border-zinc-200 bg-white py-2 pl-9 pr-4 text-sm outline-none focus:border-brand-500 dark:border-zinc-700 dark:bg-zinc-900"
                  />
                </form>
                <div className="flex flex-col gap-1">
                  {links.map((l) => (
                    <NavItem key={l.to} {...l} onClick={() => setMobileOpen(false)} />
                  ))}
                </div>
                {isAuthenticated && (
                  <button
                    onClick={logout}
                    className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-zinc-900 px-3 py-2 text-sm font-medium text-white dark:bg-white dark:text-zinc-900"
                  >
                    <LogOut size={15} /> Logout
                  </button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>
    </header>
  );
}

export default Navbar;
