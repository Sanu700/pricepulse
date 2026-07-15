import { createContext, useState } from "react";

export const AuthContext = createContext();

export function AuthProvider({ children }) {

    const [token, setToken] = useState(
        localStorage.getItem("access") || "dev-token"
    );

    const login = ({ access, refresh }) => {

        localStorage.setItem("access", "dev-token");
        localStorage.setItem("refresh", refresh || "");

        setToken("dev-token");

    };

    const logout = () => {

        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        setToken(null);

    };

    return (

        <AuthContext.Provider
            value={{
                token,
                login,
                logout,
                isAuthenticated: !!token,
            }}
        >

            {children}

        </AuthContext.Provider>

    );

}