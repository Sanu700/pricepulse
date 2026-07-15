import { motion } from "framer-motion";
import { User, Moon, Sun, LogOut, Mail, ShieldCheck } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { useTheme } from "../../hooks/useTheme";
import ComingSoon from "../../components/common/ComingSoon";

function Profile() {
  const { logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl dark:text-zinc-50">
          Profile
        </h1>
        <p className="mt-2 text-zinc-500 dark:text-zinc-400">Manage your account and preferences.</p>
      </div>

      {/* Account info — GET /accounts/profile/ isn't wired up here yet */}
      <motion.section initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Account</h2>
          <ComingSoon />
        </div>
        <div className="flex items-center gap-4">
          <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-400">
            <User size={24} />
          </span>
          <div>
            <p className="font-medium text-zinc-900 dark:text-zinc-100">Your account details</p>
            <p className="flex items-center gap-1.5 text-sm text-zinc-500 dark:text-zinc-400">
              <Mail size={13} /> Connect this section to see your real profile.
            </p>
          </div>
        </div>
      </motion.section>

      {/* Theme — real, functional */}
      <motion.section initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card p-6">
        <h2 className="mb-5 text-lg font-semibold">Appearance</h2>
        <div className="flex items-center justify-between rounded-xl border border-zinc-100 p-4 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
              {theme === "dark" ? <Moon size={18} /> : <Sun size={18} />}
            </span>
            <div>
              <p className="font-medium text-zinc-900 dark:text-zinc-100">Dark mode</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Currently {theme === "dark" ? "on" : "off"}
              </p>
            </div>
          </div>
          <button
            onClick={toggleTheme}
            className={`relative h-7 w-12 rounded-full transition ${
              theme === "dark" ? "bg-brand-600" : "bg-zinc-300"
            }`}
            aria-label="Toggle dark mode"
          >
            <motion.span
              layout
              className="absolute top-1 h-5 w-5 rounded-full bg-white shadow"
              style={{ left: theme === "dark" ? "26px" : "4px" }}
            />
          </button>
        </div>
      </motion.section>

      {/* Security — mock */}
      <motion.section initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Security</h2>
          <ComingSoon />
        </div>
        <div className="flex items-center gap-3 text-sm text-zinc-500 dark:text-zinc-400">
          <ShieldCheck size={16} /> Password changes and sessions will appear here.
        </div>
      </motion.section>

      <button
        onClick={logout}
        className="flex w-full items-center justify-center gap-2 rounded-xl border border-rose-200 py-3 text-sm font-medium text-rose-600 transition hover:bg-rose-50 dark:border-rose-900/50 dark:hover:bg-rose-950/30"
      >
        <LogOut size={16} /> Log out
      </button>
    </div>
  );
}

export default Profile;
