import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  ShoppingBag,
  BarChart3,
  Heart,
  Wallet,
  User,
  LogOut,
  Menu,
  X,
  Home,
} from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import HeroSearch from "../common/HeroSearch";

const links = [
  { to: "/", label: "Home", icon: Home, end: true },
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/products", label: "Products", icon: ShoppingBag },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
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
            ? "bg-primary-soft text-primary-dark"
            : "text-muted hover:bg-canvas hover:text-ink"
        }`
      }
    >
      <Icon size={16} />
      {label}
    </NavLink>
  );
}

function Navbar() {
  const { logout, isAuthenticated, isGuest } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [mobileOpen, setMobileOpen] = useState(false);

  function goSearch(q) {
    const trimmed = (q ?? query).trim();
    navigate(trimmed ? `/products?q=${encodeURIComponent(trimmed)}` : "/products");
    setMobileOpen(false);
  }

  return (
    <header className="sticky top-0 z-40 border-b border-line/80 bg-surface/90 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link to="/" className="flex shrink-0 items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-sm font-bold text-white shadow-sm">
            P
          </span>
          <span className="hidden text-lg font-bold tracking-tight text-ink sm:inline">
            Price<span className="text-primary">Pulse</span>
          </span>
        </Link>

        <div className="hidden max-w-md flex-1 md:block">
          <HeroSearch
            value={query}
            onChange={setQuery}
            onSubmit={goSearch}
            size="sm"
            placeholder="Search products…"
          />
        </div>

        <div className="ml-auto hidden items-center gap-0.5 xl:flex">
          {links.map((l) => (
            <NavItem key={l.to} {...l} />
          ))}
        </div>

        <div className="ml-auto flex items-center gap-1 xl:ml-2">
          {isGuest && (
            <span className="badge badge-warn hidden sm:inline-flex">Guest</span>
          )}
          <Link to="/profile" className="btn-ghost" aria-label="Profile">
            <User size={18} />
          </Link>
          {isAuthenticated && (
            <button
              type="button"
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="btn-ghost hidden sm:inline-flex"
            >
              <LogOut size={16} />
              <span className="text-sm">Logout</span>
            </button>
          )}
          <button
            type="button"
            onClick={() => setMobileOpen((v) => !v)}
            className="btn-ghost xl:hidden"
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
            className="overflow-hidden border-t border-line xl:hidden"
          >
            <div className="space-y-3 px-4 py-4">
              <HeroSearch value={query} onChange={setQuery} onSubmit={goSearch} size="sm" />
              <div className="flex flex-col gap-1">
                {links.map((l) => (
                  <NavItem key={l.to} {...l} onClick={() => setMobileOpen(false)} />
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

export default Navbar;
