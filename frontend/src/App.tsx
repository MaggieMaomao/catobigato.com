import "./i18n";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import "./index.css";
import { useAuth } from "./hooks/useAuth";

// Pages
import HomePage from "./pages/HomePage";
import CalculatorPage from "./pages/CalculatorPage";
import ProfilePage from "./pages/ProfilePage";
import KeycloakCallbackPage from "./pages/KeycloakCallback";
import LoginErrorPage from "./pages/LoginError";

// Lazy-loaded page stubs
import { lazy, Suspense } from "react";
const LearningPage = lazy(() => import("./pages/LearningPage"));
const PuzzlesPage = lazy(() => import("./pages/PuzzlesPage"));
const SocialPage = lazy(() => import("./pages/SocialPage"));
const VisualMathPage = lazy(() => import("./pages/VisualMathPage"));

export default function App() {
  const { t } = useTranslation();
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();

  return (
    <BrowserRouter>
      <div className="flex flex-col min-h-svh">
        {/* Sticky Navigation */}
        <nav className="border-b border-border bg-bg px-6 py-3 flex items-center justify-between sticky top-0 z-50">
          <div className="flex items-center gap-6">
            <a
              href="/"
              className="text-xl font-bold text-[--color-text-heading]"
            >
              {t("app.name")}
            </a>
            <div className="flex gap-4 text-sm">
              <NavLink to="/calculator">{t("nav.calculator")}</NavLink>
              <NavLink to="/learning">{t("nav.learning")}</NavLink>
              <NavLink to="/puzzles">{t("nav.puzzles")}</NavLink>
              <NavLink to="/social">{t("nav.social")}</NavLink>
              <NavLink to="/visual-math">{t("nav.visual_math")}</NavLink>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <AuthButton
              user={user}
              isAuthenticated={isAuthenticated}
              isLoading={isLoading}
              login={login}
              logout={logout}
            />
            <a
              href="/profile"
              className="text-sm text-secondary hover:text-primary transition-colors"
            >
              {t("nav.profile")}
            </a>
            <LanguageSwitcher />
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1">
          <Suspense
            fallback={
              <div className="flex items-center justify-center h-64">
                <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
            }
          >
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/calculator/*" element={<CalculatorPage />} />
              <Route path="/auth/callback" element={<KeycloakCallbackPage />} />
              <Route path="/auth/login-error" element={<LoginErrorPage />} />
              <Route
                path="/learning/*"
                element={
                  isAuthenticated ? (
                    <LearningPage />
                  ) : (
                    <div className="p-8 text-center text-secondary">
                      {t("auth.login_required", "Please sign in to access this page.")}
                    </div>
                  )
                }
              />
              <Route path="/puzzles" element={<PuzzlesPage />} />
              <Route path="/social" element={<SocialPage />} />
              <Route path="/visual-math" element={<VisualMathPage />} />
              <Route
                path="/profile"
                element={
                  isAuthenticated ? (
                    <ProfilePage />
                  ) : (
                    <div className="p-8 text-center text-secondary">
                      {t("auth.login_required", "Please sign in to access this page.")}
                    </div>
                  )
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </main>

        {/* Footer */}
        <footer className="border-t border-border py-4 text-center text-xs text-secondary">
          © 2026 CatobiGato — {t("app.tagline")}
        </footer>
      </div>
    </BrowserRouter>
  );
}

// ── Sub-components ───────────────────────────────────────────────────────────

function NavLink({
  to,
  children,
}: {
  to: string;
  children: React.ReactNode;
}) {
  return (
    <a
      href={to}
      className="text-secondary hover:text-[--color-text-heading] transition-colors font-medium"
    >
      {children}
    </a>
  );
}

function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const langs = [
    { code: "en", label: "EN" },
    { code: "zh", label: "中文" },
    { code: "fr", label: "FR" },
  ];
  return (
    <div className="flex gap-1 text-xs">
      {langs.map((lang) => (
        <button
          key={lang.code}
          onClick={() => i18n.changeLanguage(lang.code)}
          className={`px-2 py-1 rounded transition-colors ${
            i18n.language === lang.code
              ? "bg-primary text-white"
              : "text-secondary hover:bg-[--color-bg-secondary]"
          }`}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
}

function AuthButton({
  user,
  isAuthenticated,
  isLoading,
  login,
  logout,
}: {
  user: any;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
}) {
  const { t } = useTranslation();

  if (isLoading) {
    return (
      <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    );
  }
  if (isAuthenticated) {
    return (
      <div className="flex items-center gap-2">
        {user?.avatar_url && (
          <img
            src={user.avatar_url}
            alt={user.name}
            className="w-7 h-7 rounded-full"
          />
        )}
        <span className="text-sm font-medium text-secondary">
          {user?.name || user?.username || "User"}
        </span>
        <button
          onClick={logout}
          className="text-xs px-3 py-1 rounded border border-border text-secondary hover:text-primary hover:border-primary transition-colors"
        >
          {t("auth.logout", "Sign out")}
        </button>
      </div>
    );
  }
  return (
    <button
      onClick={login}
      className="text-xs px-4 py-1.5 rounded bg-primary text-white hover:opacity-90 transition-opacity font-medium"
    >
      {t("auth.login", "Sign in")}
    </button>
  );
}