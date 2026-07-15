import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Compass } from "lucide-react";

function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-canvas px-6 text-center">
      <motion.span
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-soft text-primary"
      >
        <Compass size={28} />
      </motion.span>
      <h1 className="text-6xl font-bold tracking-tight text-ink">404</h1>
      <p className="max-w-sm text-muted">
        This page doesn't exist, or it moved somewhere we haven't tracked yet.
      </p>
      <Link to="/" className="btn-primary mt-2">
        Back to home
      </Link>
    </div>
  );
}

export default NotFound;
