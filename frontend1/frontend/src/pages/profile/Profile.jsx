import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { User, LogOut, Mail, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "../../hooks/useAuth";
import { getProfile } from "../../services/authService";
import Skeleton from "../../components/common/Skeleton";

function Profile() {
  const { logout, isGuest, token } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token || isGuest) return;
    setLoading(true);
    getProfile()
      .then(setProfile)
      .catch(() => toast.error("Could not load profile"))
      .finally(() => setLoading(false));
  }, [token, isGuest]);

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-ink">Profile</h1>
        <p className="mt-1 text-muted">Account and session preferences.</p>
      </div>

      <motion.section initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card p-6">
        <h2 className="mb-5 text-lg font-semibold text-ink">Account</h2>
        {isGuest ? (
          <div className="flex items-center gap-4">
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-warning-soft text-warning">
              <User size={24} />
            </span>
            <div>
              <p className="font-medium text-ink">Guest mode</p>
              <p className="text-sm text-muted">Sign in to sync profile and email alerts.</p>
            </div>
          </div>
        ) : loading ? (
          <Skeleton className="h-16" />
        ) : (
          <div className="flex items-center gap-4">
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-soft text-primary">
              <User size={24} />
            </span>
            <div>
              <p className="font-medium text-ink">{profile?.username ?? "Signed in"}</p>
              <p className="flex items-center gap-1.5 text-sm text-muted">
                <Mail size={13} />
                {profile?.email || "No email on file"}
              </p>
              {profile?.city && <p className="text-sm text-muted">{profile.city}</p>}
            </div>
          </div>
        )}
      </motion.section>

      <motion.section initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card p-6">
        <h2 className="mb-3 text-lg font-semibold text-ink">Security</h2>
        <div className="flex items-center gap-3 text-sm text-muted">
          <ShieldCheck size={16} className="text-primary" />
          JWT sessions expire after 30 minutes; refresh tokens last 7 days.
        </div>
      </motion.section>

      <button
        type="button"
        onClick={() => {
          logout();
          navigate("/login");
        }}
        className="flex w-full items-center justify-center gap-2 rounded-xl border border-danger/30 py-3 text-sm font-medium text-danger transition hover:bg-danger-soft"
      >
        <LogOut size={16} /> Log out
      </button>
    </div>
  );
}

export default Profile;
