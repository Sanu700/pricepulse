import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Eye, EyeOff, LogIn, UserRound } from "lucide-react";
import { toast } from "sonner";
import { login as loginService, register as registerService } from "../../services/authService";
import { useAuth } from "../../hooks/useAuth";

function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, enterGuestMode } = useAuth();
  const redirectTo = location.state?.from?.pathname
    ? `${location.state.from.pathname}${location.state.from.search || ""}`
    : "/";
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (mode === "register") {
        await registerService({ username, email, password });
        toast.success("Account created — signing you in");
      }
      const data = await loginService({ username, password });
      login(data);
      toast.success("Welcome back");
      navigate(redirectTo, { replace: true });
    } catch (error) {
      const msg =
        error?.response?.data?.username?.[0] ||
        error?.response?.data?.password?.[0] ||
        error?.response?.data?.detail ||
        (mode === "register" ? "Could not create account" : "Invalid username or password");
      toast.error(typeof msg === "string" ? msg : "Authentication failed");
      console.error(error);
    } finally {
      setSubmitting(false);
    }
  }

  function handleGuest() {
    enterGuestMode();
    toast.success("Browsing as guest — all product features unlocked");
    navigate(redirectTo, { replace: true });
  }

  return (
    <div
      className="flex min-h-screen items-center justify-center px-4"
      style={{
        background:
          "radial-gradient(ellipse 70% 50% at 50% 0%, rgba(22,163,74,0.1), transparent), #F8FAFC",
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="card w-full max-w-md p-8"
      >
        <div className="mb-8 text-center">
          <span className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-lg font-bold text-white">
            P
          </span>
          <h1 className="text-2xl font-bold text-ink">
            {mode === "login" ? "Welcome back" : "Create account"}
          </h1>
          <p className="mt-1 text-sm text-muted">
            {mode === "login" ? "Sign in to PricePulse" : "Track prices across stores"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="pp-username" className="mb-1.5 block text-sm font-medium text-muted">
              Username
            </label>
            <input
              id="pp-username"
              type="text"
              className="input-field"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={4}
              autoComplete="username"
            />
          </div>

          {mode === "register" && (
            <div>
              <label htmlFor="pp-email" className="mb-1.5 block text-sm font-medium text-muted">
                Email
              </label>
              <input
                id="pp-email"
                type="email"
                className="input-field"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>
          )}

          <div>
            <label htmlFor="pp-password" className="mb-1.5 block text-sm font-medium text-muted">
              Password
            </label>
            <div className="relative">
              <input
                id="pp-password"
                type={showPassword ? "text" : "password"}
                className="input-field pr-11"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
              </button>
            </div>
            {mode === "register" && (
              <p className="mt-1 text-xs text-muted">Min 8 chars, 1 uppercase, 1 number</p>
            )}
          </div>

          <button type="submit" disabled={submitting} className="btn-primary w-full">
            <LogIn size={16} />
            {submitting ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        <button type="button" onClick={handleGuest} className="btn-secondary mt-3 w-full">
          <UserRound size={16} />
          Continue as guest
        </button>

        <button
          type="button"
          onClick={() => setMode((m) => (m === "login" ? "register" : "login"))}
          className="mt-5 w-full text-center text-sm text-muted hover:text-primary"
        >
          {mode === "login" ? (
            <>
              Don't have an account? <span className="font-medium">Create one</span>
            </>
          ) : (
            <>
              Already have an account? <span className="font-medium">Sign in</span>
            </>
          )}
        </button>
      </motion.div>
    </div>
  );
}

export default Login;
