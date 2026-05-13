import { useCallback, useEffect, useState } from "react";
import keycloak from "../auth/keycloak";

export interface AuthUser {
  sub: string;
  email: string;
  name: string;
  username: string;
  accessToken: string;
  refreshToken: string;
}

interface UseAuthReturn {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
  register: () => void;
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const initKeycloak = useCallback(async () => {
    try {
      const authenticated = await keycloak.init({
        onLoad: "check-sso",
        silentCheckSsoRedirectUri: window.location.origin + "/silent-check-sso.html",
        pkceMethod: "S256",
        enableLogging: import.meta.env.DEV,
      });

      if (authenticated) {
        const tokenParsed = keycloak.tokenParsed;
        setUser({
          sub: tokenParsed?.sub || "",
          email: tokenParsed?.email || "",
          name: tokenParsed?.name || tokenParsed?.preferred_username || "",
          username: tokenParsed?.preferred_username || "",
          accessToken: keycloak.token || "",
          refreshToken: keycloak.refreshToken || "",
        });

        // Set up token refresh
        keycloak.updateToken(300).catch((err) => {
          console.error("[Keycloak] Token refresh failed:", err);
        });
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error("[Keycloak] Initialization error:", error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    initKeycloak();

    // Listen for token refresh events
    keycloak.onAuthRefreshSuccess = () => {
      console.log("[Keycloak] Token refreshed");
    };
  }, [initKeycloak]);

  const login = useCallback(() => {
    keycloak.login({ redirectUri: window.location.origin });
  }, []);

  const logout = useCallback(() => {
    keycloak.logout({
      redirectUri: window.location.origin,
    });
  }, []);

  const register = useCallback(() => {
    keycloak.register({
      redirectUri: window.location.origin,
    });
  }, []);

  return {
    user,
    isAuthenticated: keycloak.authenticated || false,
    isLoading,
    login,
    logout,
    register,
  };
}