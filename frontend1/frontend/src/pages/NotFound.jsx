import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Compass } from "lucide-react";

function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-zinc-50 px-6 text-center dark:bg-zinc-950">
      <motion.span
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-400"
      >
        <Compass size={28} />
      </motion.span>
      <h1 className="text-6xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">404</h1>
      <p className="max-w-sm text-zinc-500 dark:text-zinc-400">
        This page doesn't exist, or it moved somewhere we haven't tracked yet.
      </p>
      <Link
        to="/"
        className="mt-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-700"
      >
        Back to dashboard
      </Link>
    </div>
  );
}

export default NotFound;
