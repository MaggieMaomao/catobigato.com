import './i18n'
import './App.css'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { lazy, Suspense, useState, useRef, useCallback } from 'react'
import { useAuth } from './auth/AuthProvider'
import { useTheme } from './theme/ThemeProvider'

// Eagerly-loaded pages
import HomePage from './pages/HomePage'
import CalculatorPage from './pages/CalculatorPage'
import ProfilePage from './pages/ProfilePage'
import KeycloakCallbackPage from './pages/KeycloakCallback'
import LoginErrorPage from './pages/LoginError'

// Lazy-loaded pages
const LearningPage = lazy(() => import('./pages/LearningPage'))
const PuzzlesPage = lazy(() => import('./pages/PuzzlesPage'))
const SocialPage = lazy(() => import('./pages/SocialPage'))
const VisualMathPage = lazy(() => import('./pages/VisualMathPage'))

// ── Nav tree data ────────────────────────────────────────────────────────────
const NAV_TREE = [
  {
    id: 'tutor',
    nameKey: 'nav.tutor',
    blurbKey: 'navTree.tutor.blurb',
    route: '/',
    items: [
      { id: 'chat', icon: '✦', nameKey: 'navTree.tutor.chat' },
      { id: 'tutorbot', icon: '▣', nameKey: 'navTree.tutor.tutorbot' },
      { id: 'cowriter', icon: '✎', nameKey: 'navTree.tutor.cowriter' },
      { id: 'book', icon: '≣', nameKey: 'navTree.tutor.book' },
      { id: 'knowledge', icon: '◉', nameKey: 'navTree.tutor.knowledge' },
      { id: 'memory', icon: '✿', nameKey: 'navTree.tutor.memory' },
    ],
  },
  {
    id: 'calculator',
    nameKey: 'nav.calculator',
    blurbKey: 'navTree.calculator.blurb',
    route: '/calculator',
    items: [
      { id: 'basic', icon: '+', nameKey: 'navTree.calculator.basic' },
      { id: 'sci', icon: 'ƒ', nameKey: 'navTree.calculator.scientific' },
      { id: 'calc', icon: '∫', nameKey: 'navTree.calculator.calculus' },
      { id: 'alg', icon: 'x', nameKey: 'navTree.calculator.algebra' },
      { id: 'graph', icon: '⊹', nameKey: 'navTree.calculator.graphing' },
      { id: 'custom', icon: 'ƒₓ', nameKey: 'navTree.calculator.custom' },
    ],
  },
  {
    id: 'learning',
    nameKey: 'nav.learning',
    blurbKey: 'navTree.learning.blurb',
    route: '/learning',
    items: [
      { id: 'notes', icon: '✎', nameKey: 'navTree.learning.notes' },
      { id: 'sets', icon: '⊟', nameKey: 'navTree.learning.sets' },
      { id: 'exams', icon: '⏱', nameKey: 'navTree.learning.exams' },
      { id: 'practice', icon: '↻', nameKey: 'navTree.learning.practice' },
      { id: 'corrections', icon: '✓', nameKey: 'navTree.learning.corrections' },
      { id: 'stats', icon: '▦', nameKey: 'navTree.learning.stats' },
    ],
  },
  {
    id: 'puzzles',
    nameKey: 'nav.puzzles',
    blurbKey: 'navTree.puzzles.blurb',
    route: '/puzzles',
    items: [
      { id: 'browse', icon: '☷', nameKey: 'navTree.puzzles.browse' },
      { id: 'daily', icon: '★', nameKey: 'navTree.puzzles.daily' },
      { id: 'create', icon: '+', nameKey: 'navTree.puzzles.create' },
      { id: 'mine', icon: '❤', nameKey: 'navTree.puzzles.mine' },
      { id: 'aligned', icon: '▦', nameKey: 'navTree.puzzles.aligned' },
      { id: 'import', icon: '⇣', nameKey: 'navTree.puzzles.import' },
    ],
  },
  {
    id: 'social',
    nameKey: 'nav.social',
    blurbKey: 'navTree.social.blurb',
    route: '/social',
    items: [
      { id: 'friends', icon: '♡', nameKey: 'navTree.social.friends' },
      { id: 'groups', icon: '◉', nameKey: 'navTree.social.groups' },
      { id: 'messages', icon: '✉', nameKey: 'navTree.social.messages' },
      { id: 'feed', icon: '≣', nameKey: 'navTree.social.feed' },
      { id: 'board', icon: '♔', nameKey: 'navTree.social.board' },
      { id: 'calendar', icon: '▢', nameKey: 'navTree.social.calendar' },
    ],
  },
  {
    id: 'visual',
    nameKey: 'nav.visual_math',
    blurbKey: 'navTree.visual.blurb',
    route: '/visual-math',
    items: [
      { id: 'math', icon: 'ƒ', nameKey: 'navTree.visual.math' },
      { id: 'phys', icon: '⟨ψ⟩', nameKey: 'navTree.visual.phys' },
      { id: 'chem', icon: '⚗', nameKey: 'navTree.visual.chem' },
      { id: 'bio', icon: '🧬', nameKey: 'navTree.visual.bio' },
      { id: 'lit', icon: '¶', nameKey: 'navTree.visual.lit' },
      { id: 'arts', icon: '✦', nameKey: 'navTree.visual.arts' },
    ],
  },
] as const

export { NAV_TREE }

// ── ROOT ─────────────────────────────────────────────────────────────────────
export default function App() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="flex flex-col min-h-svh" style={{ background: 'var(--bg)', color: 'var(--ink)' }}>
      <Header mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

      {/* Mobile nav drawer */}
      {mobileOpen && <MobileNav onClose={() => setMobileOpen(false)} />}

      <main className="flex-1 w-full relative z-[2]">
        <Suspense
          fallback={
            <div className="flex items-center justify-center h-64">
              <div
                className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin"
                style={{ borderColor: 'var(--orange)', borderTopColor: 'transparent' }}
              />
            </div>
          }
        >
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/calculator/*" element={<CalculatorPage />} />
            <Route path="/auth/callback" element={<KeycloakCallbackPage />} />
            <Route path="/auth/login-error" element={<LoginErrorPage />} />
            <Route path="/learning/*" element={<ProtectedPage><LearningPage /></ProtectedPage>} />
            <Route path="/puzzles" element={<PuzzlesPage />} />
            <Route path="/social" element={<SocialPage />} />
            <Route path="/visual-math" element={<VisualMathPage />} />
            <Route path="/profile" element={<ProtectedPage><ProfilePage /></ProtectedPage>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </main>

      <Footer />
    </div>
  )
}

// ── HEADER ───────────────────────────────────────────────────────────────────
function Header({
  mobileOpen,
  setMobileOpen,
}: {
  mobileOpen: boolean
  setMobileOpen: (v: boolean) => void
}) {
  const { t } = useTranslation()
  const [openId, setOpenId] = useState<string | null>(null)
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const enter = useCallback((id: string) => {
    if (closeTimer.current) clearTimeout(closeTimer.current)
    setOpenId(id)
  }, [])

  const leave = useCallback(() => {
    if (closeTimer.current) clearTimeout(closeTimer.current)
    closeTimer.current = setTimeout(() => setOpenId(null), 160)
  }, [])

  return (
    <header
      className="sticky top-0 z-50"
      style={{
        height: 'var(--header-h)',
        display: 'grid',
        gridTemplateColumns: 'auto 1fr auto',
        alignItems: 'center',
        gap: 32,
        padding: '0 24px',
        background: 'var(--nav-bg)',
        backdropFilter: 'blur(12px) saturate(140%)',
        WebkitBackdropFilter: 'blur(12px) saturate(140%)',
        borderBottom: '0.5px solid var(--rule)',
      }}
    >
      {/* Brand */}
      <a href="/" className="flex items-center gap-[9px] no-underline" style={{ fontFamily: 'var(--font-serif)', fontSize: 21, letterSpacing: '-0.01em', color: 'var(--ink)' }}>
        <LogoMark size={26} />
        <span>Cato<span style={{ fontStyle: 'italic', color: 'var(--orange)' }}>Bigato</span></span>
      </a>

      {/* Desktop nav with mega-dropdowns */}
      <nav
        className="hidden lg:flex items-center gap-[2px] justify-self-center"
        onMouseLeave={leave}
      >
        {NAV_TREE.map((group) => (
          <div
            key={group.id}
            className="relative"
            onMouseEnter={() => enter(group.id)}
            onFocus={() => enter(group.id)}
          >
            <button
              type="button"
              className="inline-flex items-center gap-[5px] text-[13.5px] font-medium px-3 py-[7px] border-0 bg-transparent rounded-[var(--r-1)] whitespace-nowrap transition-colors duration-150"
              style={{
                color: openId === group.id ? 'var(--ink)' : 'var(--ink-soft)',
                background: openId === group.id ? 'var(--rule-soft)' : 'transparent',
              }}
              aria-haspopup="true"
              aria-expanded={openId === group.id}
              onClick={() => setOpenId(openId === group.id ? null : group.id)}
            >
              {t(group.nameKey)}
              <svg width="9" height="6" viewBox="0 0 9 6" fill="none" style={{ transition: 'transform .2s', transform: openId === group.id ? 'rotate(180deg)' : 'none' }}>
                <path d="M 1 1 L 4.5 5 L 8 1" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" fill="none" />
              </svg>
            </button>
            {openId === group.id && (
              <Megamenu group={group} onClose={() => setOpenId(null)} />
            )}
          </div>
        ))}
      </nav>

      {/* Right controls */}
      <div className="flex items-center gap-2">
        <LanguageSwitcher />
        <ThemeToggleButton />
        <UserMenu />
        {/* Mobile hamburger */}
        <button
          className="lg:hidden p-2 rounded-md"
          style={{ color: 'var(--ink-soft)' }}
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? (
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
          ) : (
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
          )}
        </button>
      </div>

      {/* Backdrop for closing mega on click-away */}
      {openId && (
        <div
          className="fixed z-[49]"
          style={{ inset: 'var(--header-h) 0 0 0', background: 'transparent' }}
          onClick={() => setOpenId(null)}
          aria-hidden="true"
        />
      )}
    </header>
  )
}

// ── MEGAMENU ─────────────────────────────────────────────────────────────────
function Megamenu({ group, onClose }: { group: typeof NAV_TREE[number]; onClose: () => void }) {
  const { t } = useTranslation()

  return (
    <div
      className="absolute z-[60]"
      role="menu"
      style={{
        top: 'calc(100% + 8px)',
        left: '50%',
        transform: 'translateX(-50%)',
        width: 560,
        background: 'var(--bg)',
        border: '0.5px solid var(--rule)',
        borderRadius: 14,
        padding: 18,
        display: 'grid',
        gridTemplateColumns: '190px 1fr',
        gap: 16,
        boxShadow: 'var(--shadow-mega)',
        animation: 'mega-in .18s ease-out',
      }}
    >
      {/* Arrow */}
      <div
        style={{
          position: 'absolute',
          top: -6,
          left: '50%',
          transform: 'translateX(-50%) rotate(45deg)',
          width: 10,
          height: 10,
          background: 'var(--bg)',
          borderLeft: '0.5px solid var(--rule)',
          borderTop: '0.5px solid var(--rule)',
        }}
      />
      {/* Left panel */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
          background: 'var(--bg-2)',
          margin: '-18px 0 -18px -18px',
          padding: 18,
          borderRight: '0.5px solid var(--rule)',
          borderRadius: '14px 0 0 14px',
        }}
      >
        <div style={{ fontFamily: 'var(--font-serif)', fontSize: 19, letterSpacing: '-0.01em', color: 'var(--ink)' }}>
          {t(group.nameKey)}
        </div>
        <div style={{ fontSize: 12, color: 'var(--ink-soft)', lineHeight: 1.45 }}>
          {t(group.blurbKey)}
        </div>
        <div style={{ flex: 1 }} />
        <a
          href={group.route}
          onClick={onClose}
          className="inline-flex items-center gap-[6px] self-start transition-colors duration-150 hover:text-white"
          style={{
            fontSize: 12,
            fontWeight: 600,
            color: 'var(--orange-d)',
            padding: '7px 12px',
            background: 'var(--bg)',
            border: '0.5px solid var(--rule)',
            borderRadius: 999,
          }}
        >
          {t('pillars.open')} {t(group.nameKey)}
          <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
            <path d="M3 6 H 9 M 6 3 L 9 6 L 6 9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </a>
      </div>
      {/* Right grid */}
      <div className="grid grid-cols-2 gap-[2px] content-start" role="menubar">
        {group.items.map((it) => (
          <a
            key={it.id}
            href={`${group.route}#${group.id}-${it.id}`}
            className="flex items-center gap-[10px] p-[9px_10px] rounded-lg text-[13px] transition-colors duration-[120ms]"
            style={{ color: 'var(--ink)' }}
            role="menuitem"
            onClick={onClose}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--bg-2)'
              e.currentTarget.style.color = 'var(--orange-d)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.color = 'var(--ink)'
            }}
          >
            <span
              className="w-[26px] h-[26px] grid place-items-center rounded-[7px] shrink-0"
              style={{
                background: 'var(--bg-2)',
                fontFamily: 'var(--font-serif)',
                fontStyle: 'italic',
                fontSize: 14,
                color: 'var(--orange-d)',
              }}
            >
              {it.icon}
            </span>
            <span className="font-medium">{t(it.nameKey)}</span>
          </a>
        ))}
      </div>
    </div>
  )
}

// ── MOBILE NAV ───────────────────────────────────────────────────────────────
function MobileNav({ onClose }: { onClose: () => void }) {
  const { t } = useTranslation()

  return (
    <div className="fixed inset-0 z-40 lg:hidden" onClick={onClose}>
      <div
        className="absolute left-0 right-0 shadow-lg overflow-y-auto"
        style={{
          top: 'var(--header-h)',
          maxHeight: 'calc(100vh - var(--header-h))',
          background: 'var(--bg)',
          borderBottom: '0.5px solid var(--rule)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <nav className="p-4 flex flex-col gap-1">
          {NAV_TREE.map((group) => (
            <a
              key={group.id}
              href={group.route}
              onClick={onClose}
              className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors"
              style={{ color: 'var(--ink-soft)' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--bg-2)'; e.currentTarget.style.color = 'var(--ink)' }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--ink-soft)' }}
            >
              {t(group.nameKey)}
            </a>
          ))}
        </nav>
      </div>
    </div>
  )
}

// ── FOOTER ───────────────────────────────────────────────────────────────────
function Footer() {
  const { t } = useTranslation()

  return (
    <footer
      className="relative z-[2] flex items-center justify-between px-6 text-[11.5px]"
      style={{
        height: 'var(--footer-h)',
        borderTop: '0.5px solid var(--rule)',
        background: 'var(--nav-bg)',
        color: 'var(--ink-muted)',
      }}
    >
      <div className="flex items-center gap-[14px]">
        <span className="inline-flex items-center gap-[6px]">
          <LogoMark size={14} withRing={false} />
          <span style={{ fontWeight: 600, color: 'var(--ink-soft)' }}>
            Cato<span style={{ fontStyle: 'italic', color: 'var(--orange)' }}>Bigato</span>
          </span>
        </span>
        <span className="w-[3px] h-[3px] rounded-full opacity-50" style={{ background: 'var(--ink-muted)' }} />
        <span>&copy; 2025 &middot; {t('footer.madeWith')}</span>
      </div>
      <div className="hidden sm:flex items-center gap-[14px]">
        <a href="#" className="hover:text-[var(--ink)] transition-colors">{t('footer.about')}</a>
        <a href="#" className="hover:text-[var(--ink)] transition-colors">{t('footer.blog')}</a>
        <a href="#" className="hover:text-[var(--ink)] transition-colors">{t('footer.privacy')}</a>
        <a href="#" className="hover:text-[var(--ink)] transition-colors">{t('footer.terms')}</a>
        <a href="#" className="hover:text-[var(--ink)] transition-colors">{t('footer.contact')}</a>
        <span className="w-[3px] h-[3px] rounded-full opacity-50" style={{ background: 'var(--ink-muted)' }} />
        <span>v0.9 &middot; purr</span>
      </div>
    </footer>
  )
}

// ── LOGO MARK ────────────────────────────────────────────────────────────────
export function LogoMark({ size = 28, withRing = true }: { size?: number; withRing?: boolean }) {
  return (
    <span
      style={{
        display: 'inline-block',
        width: size,
        height: size,
        borderRadius: '50%',
        overflow: 'hidden',
        boxShadow: withRing ? '0 0 0 1px var(--rule)' : 'none',
        flexShrink: 0,
        verticalAlign: 'middle',
      }}
      aria-label="Catobi logo"
    >
      <img
        src="/assets/catobi-avatar.png"
        alt=""
        width={size}
        height={size}
        style={{ display: 'block', width: '100%', height: '100%' }}
      />
    </span>
  )
}

// ── LANGUAGE SWITCHER ────────────────────────────────────────────────────────
function LanguageSwitcher() {
  const { i18n } = useTranslation()
  const langs = [
    { code: 'en', label: 'EN' },
    { code: 'zh', label: '中' },
    { code: 'fr', label: 'FR' },
  ]

  return (
    <div
      className="hidden sm:inline-flex items-center gap-[2px] h-[28px] px-[2px] rounded-full text-[11px] font-semibold"
      style={{ background: 'var(--rule-soft)', color: 'var(--ink-muted)' }}
    >
      {langs.map((l) => (
        <button
          key={l.code}
          className="border-0 bg-transparent h-[24px] px-[9px] rounded-full transition-all duration-150"
          style={
            i18n.language === l.code
              ? { background: 'var(--bg)', color: 'var(--ink)', boxShadow: '0 1px 2px var(--rule-soft)' }
              : { color: 'inherit' }
          }
          onClick={() => i18n.changeLanguage(l.code)}
        >
          {l.label}
        </button>
      ))}
    </div>
  )
}

// ── THEME TOGGLE ─────────────────────────────────────────────────────────────
function ThemeToggleButton() {
  const { t } = useTranslation()
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      className="w-[30px] h-[30px] rounded-full border-0 inline-grid place-items-center transition-all duration-150"
      style={{ background: 'var(--rule-soft)', color: 'var(--ink-soft)' }}
      onClick={toggleTheme}
      title={t(theme === 'dark' ? 'theme.toLight' : 'theme.toDark')}
      aria-label={t(theme === 'dark' ? 'theme.toLight' : 'theme.toDark')}
    >
      {theme === 'dark' ? (
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <circle cx="8" cy="8" r="3" fill="currentColor" />
          {[0, 45, 90, 135, 180, 225, 270, 315].map((a) => (
            <line key={a} x1="8" y1="1.5" x2="8" y2="3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" transform={`rotate(${a} 8 8)`} />
          ))}
        </svg>
      ) : (
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M13 9.5 A 6 6 0 1 1 6.5 3 A 5 5 0 0 0 13 9.5 Z" fill="currentColor" />
        </svg>
      )}
    </button>
  )
}

// ── USER MENU ────────────────────────────────────────────────────────────────
function UserMenu() {
  const { t } = useTranslation()
  const { isAuthenticated, displayName, username, avatar, login, logout } = useAuth()
  const [open, setOpen] = useState(false)

  if (!isAuthenticated) {
    return (
      <button
        onClick={login}
        className="inline-flex items-center gap-[6px] h-[30px] px-[14px] border-0 rounded-full text-[12.5px] font-semibold transition-colors duration-150"
        style={{ background: 'var(--ink)', color: 'var(--bg)', letterSpacing: '0.01em' }}
        onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--orange-d)' }}
        onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--ink)' }}
      >
        {t('auth.signIn')}
        <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
          <path d="M3 6 H 9 M 6 3 L 9 6 L 6 9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
    )
  }

  const name = displayName || username || 'User'

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-[32px] h-[32px] p-0 rounded-full grid place-items-center overflow-hidden cursor-pointer transition-all duration-150"
        style={{
          background: 'var(--cream)',
          border: '1.5px solid var(--bg)',
          boxShadow: '0 0 0 1px var(--rule)',
        }}
        title={t('auth.signOut')}
      >
        {avatar ? (
          <img src={avatar} alt={name} className="block w-full h-full object-cover" />
        ) : (
          <img src="/assets/catobi-avatar.png" alt="Catobi" className="block w-full h-full" />
        )}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div
            className="absolute right-0 mt-1 w-44 rounded-[14px] overflow-hidden z-20"
            style={{
              background: 'var(--bg)',
              border: '0.5px solid var(--rule)',
              boxShadow: 'var(--shadow-mega)',
            }}
          >
            <a
              href="/profile"
              className="flex items-center gap-2 px-4 py-2.5 text-sm transition-colors"
              style={{ color: 'var(--ink)' }}
              onClick={() => setOpen(false)}
            >
              {t('nav.profile')}
            </a>
            <div style={{ borderTop: '0.5px solid var(--rule)' }} />
            <button
              onClick={() => { setOpen(false); logout() }}
              className="w-full text-left flex items-center gap-2 px-4 py-2.5 text-sm transition-colors border-0 bg-transparent cursor-pointer"
              style={{ color: 'var(--color-error, #ef4444)' }}
            >
              {t('auth.signOut')}
            </button>
          </div>
        </>
      )}
    </div>
  )
}

// ── PROTECTED PAGE WRAPPER ───────────────────────────────────────────────────
function ProtectedPage({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation()
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 p-16 text-center">
        <p style={{ color: 'var(--ink-muted)' }}>
          {t('auth.login_required', 'Please sign in to access this page.')}
        </p>
      </div>
    )
  }
  return <>{children}</>
}
