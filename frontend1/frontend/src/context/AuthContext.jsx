import { createContext, useCallback, useEffect, useMemo, useState } from "react";

export const AuthContext = createContext();

const GUEST_FLAG = "pricepulse_guest";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("access"));
  const [isGuest, setIsGuest] = useState(
    () => localStorage.getItem(GUEST_FLAG) === "1"
  );

  const login = useCallback(({ access, refresh }) => {
    localStorage.setItem("access", access);
    if (refresh) localStorage.setItem("refresh", refresh);
    localStorage.removeItem(GUEST_FLAG);
    setToken(access);
    setIsGuest(false);
  }, []);

  const enterGuestMode = useCallback(() => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.setItem(GUEST_FLAG, "1");
    setToken(null);
    setIsGuest(true);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem(GUEST_FLAG);
    setToken(null);
    setIsGuest(false);
  }, []);

  useEffect(() => {
    function onRefreshed(e) {
      const access = e.detail?.access;
      if (access) setToken(access);
    }
    function onExpired() {
      setToken(null);
      setIsGuest(false);
    }
    window.addEventListener("pricepulse:token-refreshed", onRefreshed);
    window.addEventListener("pricepulse:session-expired", onExpired);
    return () => {
      window.removeEventListener("pricepulse:token-refreshed", onRefreshed);
      window.removeEventListener("pricepulse:session-expired", onExpired);
    };
  }, []);

  const value = useMemo(
    () => ({
      token,
      login,
      logout,
      enterGuestMode,
      isGuest,
      isSignedIn: Boolean(token),
      isAuthenticated: Boolean(token) || isGuest,
    }),
    [token, login, logout, enterGuestMode, isGuest]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
