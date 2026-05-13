import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import keycloak from "../auth/keycloak";

export default function KeycloakCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to Keycloak login if not authenticated
    if (!keycloak.authenticated) {
      keycloak.login({ redirectUri: window.location.origin });
      return;
    }

    // Authenticated — redirect home
    navigate("/", { replace: true });
  }, [navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="mt-4 text-secondary">Completing sign in...</p>
      </div>
    </div>
  );
}