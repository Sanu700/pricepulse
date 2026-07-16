import { Link, Outlet, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import Navbar from "../components/layout/Navbar";

function MainLayout() {
  const location = useLocation();
  const apiDocsUrl = import.meta.env.VITE_API_DOCS_URL;

  return (
    <div className="min-h-screen bg-canvas">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-primary focus:px-3 focus:py-2 focus:text-white"
      >
        Skip to content
      </a>
      <Navbar />
      <main
        id="main-content"
        className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8"
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.16, ease: "easeOut" }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
      <footer className="border-t border-line bg-surface">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-semibold text-ink">PricePulse</p>
              <p className="mt-1 text-sm text-muted">
                Compare grocery prices across Blinkit, Zepto, Instamart, and BigBasket.
              </p>
            </div>
            <nav className="flex flex-wrap gap-4 text-sm font-medium text-muted">
              <Link to="/products" className="hover:text-primary">
                Products
              </Link>
              <Link to="/analytics" className="hover:text-primary">
                Analytics
              </Link>
              <Link to="/dashboard" className="hover:text-primary">
                Dashboard
              </Link>
              {apiDocsUrl && (
                <a
                  href={apiDocsUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-primary"
                >
                  API Docs
                </a>
              )}
            </nav>
          </div>
          <p className="text-xs text-muted">
            Live provider capture is optional and region-dependent; hybrid mode falls back
            to deterministic catalog data when anti-bot protections block access.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default MainLayout;
