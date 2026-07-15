import { createContext, useCallback, useMemo, useState } from "react";

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

  const value = useMemo(
    () => ({
      token,
      login,
      logout,
      enterGuestMode,
      isGuest,
      isAuthenticated: Boolean(token) || isGuest,
    }),
    [token, login, logout, enterGuestMode, isGuest]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
