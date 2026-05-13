import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import keycloak from "../auth/keycloak";

export default function LoginError() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleRetry = () => {
    keycloak.login({ redirectUri: window.location.origin });
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center max-w-md p-8">
        <h1 className="text-2xl font-bold text-error mb-4">
          {t("auth.login_failed", "Sign in failed")}
        </h1>
        <p className="text-secondary mb-6">
          {t(
            "auth.error_message",
            "There was a problem signing you in. Please try again."
          )}
        </p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={handleRetry}
            className="px-4 py-2 bg-primary text-white rounded hover:opacity-90 transition-opacity"
          >
            {t("auth.try_again", "Try Again")}
          </button>
          <button
            onClick={() => navigate("/")}
            className="px-4 py-2 border border-border text-secondary rounded hover:border-primary hover:text-primary transition-colors"
          >
            {t("common.go_home", "Go Home")}
          </button>
        </div>
      </div>
    </div>
  );
}