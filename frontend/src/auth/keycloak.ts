import Keycloak from "keycloak-js";

// Keycloak configuration for catobigato realm on KeyToMarvel.com
const keycloakConfig = {
  url: import.meta.env.VITE_KEYCLOAK_URL + "/realms/" + import.meta.env.VITE_KEYCLOAK_REALM,
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID,
  realm: import.meta.env.VITE_KEYCLOAK_REALM,
};

// Singleton Keycloak instance
const keycloak = new Keycloak(keycloakConfig);

// Enable debug logging in development
if (import.meta.env.DEV) {
  keycloak.onAuthRefreshError = () => {
    console.error("[Keycloak] Auth refresh error");
  };
  keycloak.onAuthLogout = () => {
    console.log("[Keycloak] User logged out");
  };
}

export default keycloak;