import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { LogoMark, NAV_TREE } from '../App'

// ── Data ─────────────────────────────────────────────────────────────────────
const SUBJECTS = [
  { id: 'math', accent: 'var(--c-math)', icon: 'ƒ', nameKey: 'subjects.math' },
  { id: 'phys', accent: 'var(--c-phys)', icon: '⟨ψ⟩', nameKey: 'subjects.physics' },
  { id: 'chem', accent: 'var(--c-chem)', icon: '⚗', nameKey: 'subjects.chemistry' },
  { id: 'bio', accent: 'var(--c-bio)', icon: '🧬', nameKey: 'subjects.biology' },
  { id: 'lit', accent: 'var(--c-lit)', icon: '¶', nameKey: 'subjects.literacy' },
  { id: 'art', accent: 'var(--c-art)', icon: '✦', nameKey: 'subjects.arts' },
]

const PILLAR_ACCENTS: Record<string, string> = {
  tutor: 'var(--orange)',
  calculator: 'var(--c-math)',
  learning: 'var(--c-phys)',
  puzzles: 'var(--c-art)',
  social: 'var(--c-bio)',
  visual: 'var(--c-chem)',
}

const FLOW_NUMS = ['I', 'II', 'III', 'IV', 'V']

export default function HomePage() {
  return (
    <>
      <Hero />
      <FeaturePillars />
      <TutorPreview />
      <CalcPreview />
      <SubjectsStrip />
      <Flow />
      <Ribbon />
      <Quote />
    </>
  )
}

// ── HERO ─────────────────────────────────────────────────────────────────────
function Hero() {
  const { t } = useTranslation()

  return (
    <section
      className="hero-section relative mx-auto"
      style={{
        display: 'grid',
        gridTemplateColumns: '1.05fr 1fr',
        gap: 48,
        alignItems: 'center',
        maxWidth: 1240,
        padding: '64px 32px 72px',
      }}
    >
      <div>
        {/* Eyebrow */}
        <div
          className="inline-flex items-center gap-2 mb-[18px]"
          style={{ fontSize: 12, fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--ink-muted)' }}
        >
          <span className="w-[6px] h-[6px] rounded-full" style={{ background: 'var(--orange)', boxShadow: '0 0 0 4px rgba(232,116,59,0.15)' }} />
          {t('hero.eyebrow')}
        </div>

        {/* Headline */}
        <h1
          style={{
            fontFamily: 'var(--font-serif)',
            fontWeight: 400,
            fontSize: 'clamp(44px, 5.8vw, 78px)',
            lineHeight: 1.04,
            letterSpacing: '-0.02em',
            color: 'var(--ink)',
            margin: '0 0 22px',
            textWrap: 'balance',
          }}
        >
          {t('hero.title_pre')}
          <em style={{ fontStyle: 'italic', color: 'var(--orange)', position: 'relative' }}>
            {t('hero.title_em')}
            <span
              style={{
                content: '""',
                position: 'absolute',
                left: '2%',
                right: '2%',
                bottom: -2,
                height: 6,
                background: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 6' preserveAspectRatio='none'><path d='M1 4 Q 25 0 50 3 T 99 3' fill='none' stroke='%23E8743B' stroke-width='1.6' stroke-linecap='round' opacity='0.6'/></svg>") center/100% 100% no-repeat`,
                display: 'block',
              }}
            />
          </em>
          {t('hero.title_post')}
        </h1>

        {/* Lede */}
        <p
          style={{
            fontSize: 17.5,
            lineHeight: 1.55,
            color: 'var(--ink-soft)',
            maxWidth: '50ch',
            margin: '0 0 30px',
          }}
        >
          {t('hero.lede')}
        </p>

        {/* CTAs */}
        <div className="flex items-center gap-3 flex-wrap">
          <a
            href="#tutor"
            className="inline-flex items-center gap-2 h-[44px] px-5 rounded-full text-sm font-semibold text-white no-underline transition-transform duration-[120ms] hover:-translate-y-[1px]"
            style={{
              background: 'var(--orange)',
              boxShadow: '0 1px 0 rgba(255,255,255,0.35) inset, 0 6px 18px -8px rgba(201,90,34,0.6)',
              letterSpacing: '0.01em',
              border: '1px solid transparent',
            }}
          >
            {t('hero.startLearning')}
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 7 H 11 M 7 3 L 11 7 L 7 11" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </a>
          <button
            className="inline-flex items-center gap-2 h-[44px] px-5 rounded-full text-sm font-semibold transition-transform duration-[120ms] hover:-translate-y-[1px]"
            style={{ background: 'transparent', color: 'var(--ink)', border: '1px solid var(--rule)' }}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.4" /><path d="M 5.5 4.5 L 9.5 7 L 5.5 9.5 Z" fill="currentColor" /></svg>
            {t('hero.watchDemo')}
          </button>
        </div>

        {/* Meta stats */}
        <div className="flex gap-6 mt-[38px]">
          {[
            { num: <>12<span style={{ color: 'var(--orange)' }}>+</span></>, label: t('hero.subjects') },
            { num: '4.9', label: t('hero.rating') },
            { num: '73k', label: t('hero.solved') },
          ].map((stat, i) => (
            <div key={i} className="flex flex-col gap-[2px]">
              <div style={{ fontFamily: 'var(--font-serif)', fontSize: 28, color: 'var(--ink)', letterSpacing: '-0.01em', lineHeight: 1 }}>{stat.num}</div>
              <div style={{ fontSize: 11.5, color: 'var(--ink-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Hero stage — mascot */}
      <div className="relative w-full justify-self-end" style={{ aspectRatio: '1 / 1', maxWidth: 540 }}>
        <MascotHero />
        {/* Floating cards */}
        <FloatCard pos={{ top: '8%', left: '-2%' }} delay="0s" icon="ƒ" iconBg="var(--c-math)" title={t('hero.floatSolve')} sub="x² − 5x + 6 = 0" />
        <FloatCard pos={{ top: '18%', right: '-4%' }} delay="1.2s" icon="⚗" iconBg="var(--c-chem)" title={t('hero.floatBalance')} sub="C₃H₈ + O₂ → ?" />
        <FloatCard pos={{ bottom: '16%', left: '-6%' }} delay="2.4s" icon="¶" iconBg="var(--c-lit)" title={t('hero.floatEssay')} sub={t('hero.floatEssaySub')} />
        <FloatCard pos={{ bottom: '4%', right: '0%' }} delay="3.6s" icon="★" iconBg="var(--orange)" title={t('hero.floatStreak')} sub={t('hero.floatStreakSub')} />
      </div>
    </section>
  )
}

function FloatCard({ pos, delay, icon, iconBg, title, sub }: {
  pos: React.CSSProperties
  delay: string
  icon: string
  iconBg: string
  title: string
  sub: string
}) {
  return (
    <div
      className="float-card absolute flex items-center gap-[9px] text-xs"
      style={{
        ...pos,
        background: 'var(--bg)',
        border: '0.5px solid var(--rule)',
        borderRadius: 12,
        padding: '10px 12px',
        boxShadow: 'var(--shadow-float)',
        animation: `floaty 5s ease-in-out infinite`,
        animationDelay: delay,
      }}
    >
      <div
        className="w-7 h-7 rounded-lg grid place-items-center text-white"
        style={{ background: iconBg, fontFamily: 'var(--font-serif)', fontSize: 14 }}
      >
        {icon}
      </div>
      <div>
        <div style={{ fontWeight: 600, color: 'var(--ink)' }}>{title}</div>
        <div style={{ color: 'var(--ink-muted)', fontSize: 11 }}>{sub}</div>
      </div>
    </div>
  )
}

// ── MASCOT HERO ──────────────────────────────────────────────────────────────
function MascotHero() {
  return (
    <div className="relative w-full h-full grid place-items-center" aria-hidden="true">
      <div
        className="absolute rounded-full"
        style={{
          inset: '8% 6% 12% 6%',
          background: 'radial-gradient(circle at 50% 45%, #FBE7C9 0%, rgba(251,231,201,0.45) 55%, transparent 75%)',
        }}
      />
      <svg viewBox="0 0 540 540" className="absolute inset-0 w-full h-full">
        <defs>
          <radialGradient id="sky-disc" cx="50%" cy="40%" r="50%">
            <stop offset="0%" stopColor="#DDEDF4" stopOpacity="0.85" />
            <stop offset="60%" stopColor="#DDEDF4" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#DDEDF4" stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx="270" cy="230" r="180" fill="url(#sky-disc)" className="sky-disc" />
        <ellipse cx="170" cy="160" rx="28" ry="6" fill="white" opacity="0.6" className="sky-cloud" />
        <ellipse cx="380" cy="210" rx="22" ry="5" fill="white" opacity="0.6" className="sky-cloud" />
        <ellipse cx="150" cy="260" rx="18" ry="4" fill="white" opacity="0.55" className="sky-cloud" />
      </svg>
      <img
        src="/assets/catobi-body.png"
        alt="Catobi"
        className="relative z-[2]"
        style={{
          width: '78%',
          height: 'auto',
          maxHeight: '92%',
          objectFit: 'contain',
          filter: 'drop-shadow(0 14px 24px rgba(201,90,34,0.18))',
        }}
      />
    </div>
  )
}

// ── FEATURE PILLARS ──────────────────────────────────────────────────────────
function FeaturePillars() {
  const { t } = useTranslation()
  const hero = 'tutor'
  const big = ['calculator', 'visual']
  const small = ['learning', 'puzzles', 'social']

  return (
    <section className="mx-auto pt-4" style={{ maxWidth: 1240, padding: '16px 32px 64px' }} id="pillars">
      <SectionTag text={t('pillars.tag')} />
      <div className="flex items-end justify-between gap-6 mb-7">
        <h2 style={{ fontFamily: 'var(--font-serif)', fontWeight: 400, fontSize: 'clamp(32px, 3.6vw, 46px)', lineHeight: 1.02, letterSpacing: '-0.015em', margin: 0 }}>
          {t('pillars.title_pre')}<em style={{ fontStyle: 'italic', color: 'var(--orange)' }}>{t('pillars.title_em')}</em>{t('pillars.title_post')}
        </h2>
        <p className="hidden md:block" style={{ fontSize: 14.5, color: 'var(--ink-soft)', maxWidth: '40ch', margin: 0 }}>{t('pillars.desc')}</p>
      </div>
      <div className="flex flex-col gap-[14px]">
        {/* Hero pillar — full width */}
        <div className="grid" style={{ gridTemplateColumns: '1fr' }}>
          <PillarCard id={hero} variant="hero" />
        </div>
        {/* Big row */}
        <div className="pillars-row-big grid gap-[14px]" style={{ gridTemplateColumns: '1.05fr 1fr' }}>
          {big.map((id) => <PillarCard key={id} id={id} variant="big" />)}
        </div>
        {/* Small row */}
        <div className="pillars-row-small grid gap-[14px]" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
          {small.map((id) => <PillarCard key={id} id={id} variant="small" />)}
        </div>
      </div>
    </section>
  )
}

function PillarCard({ id, variant }: { id: string; variant: 'hero' | 'big' | 'small' }) {
  const { t } = useTranslation()
  const group = NAV_TREE.find((g) => g.id === id)
  if (!group) return null
  const accent = PILLAR_ACCENTS[id] || 'var(--orange)'

  return (
    <article
      className={`${variant === 'hero' ? 'pillar-hero' : ''} relative rounded-[var(--r-3)] overflow-hidden transition-all duration-200 hover:-translate-y-[3px]`}
      style={{
        background: 'var(--bg)',
        border: '0.5px solid var(--rule)',
        padding: variant === 'hero' ? 32 : 24,
        display: variant === 'hero' ? 'grid' : 'flex',
        flexDirection: 'column',
        gap: variant === 'hero' ? 36 : 18,
        gridTemplateColumns: variant === 'hero' ? '1fr 1.05fr' : undefined,
        minHeight: variant === 'big' ? 360 : variant === 'hero' ? 340 : undefined,
        ['--accent' as string]: accent,
        boxShadow: 'none',
      }}
      onMouseEnter={(e) => { e.currentTarget.style.boxShadow = '0 24px 50px -28px rgba(42,30,18,0.25)' }}
      onMouseLeave={(e) => { e.currentTarget.style.boxShadow = 'none' }}
    >
      {/* Left bar on hover */}
      <div
        className="absolute left-0 top-0 bottom-0 w-[3px] opacity-0 transition-opacity duration-200"
        style={{ background: accent }}
      />

      <div style={{ maxWidth: variant === 'hero' ? '46ch' : undefined }}>
        <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: accent, marginBottom: 8 }}>
          {t(`pillar.${id}.tag`)}
        </div>
        <h3
          style={{
            fontFamily: 'var(--font-serif)',
            fontWeight: 400,
            fontSize: variant === 'hero' ? 'clamp(32px, 3.8vw, 46px)' : variant === 'big' ? 34 : 28,
            lineHeight: 1.05,
            letterSpacing: '-0.015em',
            margin: '0 0 10px',
            textWrap: 'balance',
          }}
        >
          {t(`pillar.${id}.title_pre`)}
          <em style={{ fontStyle: 'italic', color: accent }}>{t(`pillar.${id}.title_em`)}</em>
          {t(`pillar.${id}.title_post`, '')}
        </h3>
        <p style={{ fontSize: 13.5, color: 'var(--ink-soft)', margin: 0, lineHeight: 1.55 }}>
          {t(`pillar.${id}.desc`)}
        </p>
      </div>

      {/* Items */}
      <div
        className="flex flex-col gap-1 mt-auto"
        style={{
          display: variant === 'big' || variant === 'hero' ? 'grid' : 'flex',
          gridTemplateColumns: variant === 'big' || variant === 'hero' ? '1fr 1fr' : undefined,
          gap: variant === 'big' || variant === 'hero' ? '0 18px' : 4,
        }}
      >
        {group.items.map((it, i) => (
          <a
            key={it.id}
            href={`${group.route}#${group.id}-${it.id}`}
            className="grid items-center gap-3 py-[10px] px-1 text-[13px] transition-all duration-150 no-underline group"
            style={{
              gridTemplateColumns: '26px 1fr auto',
              borderTop: i === 0 ? 'none' : '0.5px solid var(--rule-soft)',
              color: 'var(--ink)',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = accent; e.currentTarget.style.paddingLeft = '8px' }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--ink)'; e.currentTarget.style.paddingLeft = '4px' }}
          >
            <span
              style={{
                fontFamily: 'var(--font-serif)',
                fontStyle: 'italic',
                fontSize: 15,
                color: accent,
                width: 26,
                textAlign: 'center',
              }}
            >
              {it.icon}
            </span>
            <span className="font-medium">{t(it.nameKey)}</span>
            <span style={{ fontSize: 13, color: 'var(--ink-muted)', opacity: 0, transform: 'translateX(-4px)', transition: 'opacity .15s, transform .15s' }}>↗</span>
          </a>
        ))}
      </div>
    </article>
  )
}

// ── TUTOR PREVIEW ────────────────────────────────────────────────────────────
function TutorPreview() {
  const { t } = useTranslation()
  const [mode, setMode] = useState('chat')

  const RAIL = [
    { id: 'new', icon: '+', label: t('tutorPreview.newChat'), hi: true },
    { id: 'chat', icon: '✦', label: t('navTree.tutor.chat'), active: true },
    { id: 'tutorbot', icon: '▣', label: t('navTree.tutor.tutorbot') },
    { id: 'cowriter', icon: '✎', label: t('navTree.tutor.cowriter') },
    { id: 'book', icon: '≣', label: t('navTree.tutor.book') },
    { id: 'knowledge', icon: '◉', label: t('navTree.tutor.knowledge') },
    { id: 'memory', icon: '✿', label: t('navTree.tutor.memory') },
  ]

  const examples = [
    t('tutorPreview.example1'),
    t('tutorPreview.example2'),
    t('tutorPreview.example3'),
    t('tutorPreview.example4'),
  ]

  return (
    <section className="mx-auto pt-2 pb-16" style={{ maxWidth: 1240, padding: '8px 32px 64px' }} id="tutor">
      <SectionTag text={t('tutorPreview.tag')} />
      <div className="flex items-end justify-between gap-6 mb-7">
        <h2 style={{ fontFamily: 'var(--font-serif)', fontWeight: 400, fontSize: 'clamp(32px, 3.6vw, 46px)', lineHeight: 1.02, letterSpacing: '-0.015em', margin: 0 }}>
          {t('tutorPreview.title_pre')}<em style={{ fontStyle: 'italic', color: 'var(--orange)' }}>{t('tutorPreview.title_em')}</em>{t('tutorPreview.title_post')}
        </h2>
        <p className="hidden md:block" style={{ fontSize: 14.5, color: 'var(--ink-soft)', maxWidth: '40ch', margin: 0 }}>{t('tutorPreview.desc')}</p>
      </div>

      {/* Dark tutor window */}
      <div
        className="mt-7 rounded-[18px] overflow-hidden relative"
        style={{
          background: '#1B1410',
          boxShadow: '0 40px 80px -30px rgba(42,30,18,0.45), 0 0 0 0.5px var(--rule)',
          color: '#FAF1E2',
        }}
      >
        {/* Chrome bar */}
        <div
          className="grid items-center h-[38px] px-4"
          style={{
            gridTemplateColumns: '1fr auto 1fr',
            background: 'rgba(255,255,255,0.025)',
            borderBottom: '0.5px solid rgba(255,255,255,0.06)',
          }}
        >
          <div className="flex gap-[6px]">
            <span className="w-[11px] h-[11px] rounded-full" style={{ background: '#F25C57' }} />
            <span className="w-[11px] h-[11px] rounded-full" style={{ background: '#F5BD49' }} />
            <span className="w-[11px] h-[11px] rounded-full" style={{ background: '#5BCC59' }} />
          </div>
          <div className="text-xs font-medium text-center" style={{ color: 'rgba(250,241,226,0.7)' }}>{t('tutorPreview.newChat')}</div>
          <div className="hidden md:flex justify-end gap-[6px]">
            <span className="text-[11px] px-[10px] py-1 rounded-[6px]" style={{ color: 'rgba(250,241,226,0.55)', border: '0.5px solid rgba(250,241,226,0.08)' }}>{t('tutorPreview.saveNotebook')}</span>
            <span className="text-[11px] px-[10px] py-1 rounded-[6px]" style={{ color: 'rgba(250,241,226,0.55)', border: '0.5px solid rgba(250,241,226,0.08)' }}>{t('tutorPreview.activity')}</span>
          </div>
        </div>

        <div className="tutor-body grid min-h-[460px]" style={{ gridTemplateColumns: '168px 1fr' }}>
          {/* Left rail */}
          <aside
            className="tutor-rail hidden md:flex flex-col gap-1 p-[14px_10px]"
            style={{ background: '#120C08', borderRight: '0.5px solid rgba(255,255,255,0.05)' }}
          >
            <div className="flex items-center gap-2 px-2 pb-3 mb-1" style={{ borderBottom: '0.5px solid rgba(255,255,255,0.05)' }}>
              <LogoMark size={20} />
              <span style={{ fontFamily: 'var(--font-serif)', fontSize: 16, letterSpacing: '-0.01em', color: '#FAF1E2' }}>CatoBigato</span>
            </div>
            <div className="flex flex-col gap-[2px] flex-1">
              {RAIL.map((item) => (
                <button
                  key={item.id}
                  className="flex items-center gap-[10px] py-[7px] px-[10px] border-0 rounded-[7px] cursor-pointer text-[12.5px] transition-colors duration-[120ms]"
                  style={{
                    background: item.active ? 'rgba(255,255,255,0.06)' : item.hi ? 'transparent' : 'transparent',
                    color: item.active || item.hi ? '#FAF1E2' : 'rgba(250,241,226,0.65)',
                  }}
                >
                  <span
                    className="w-5 h-5 grid place-items-center rounded-[5px] shrink-0 text-xs"
                    style={{
                      background: item.active || item.hi ? 'var(--orange)' : 'rgba(255,255,255,0.04)',
                      color: item.active || item.hi ? '#1B1410' : 'rgba(250,241,226,0.85)',
                      fontFamily: 'var(--font-serif)',
                      fontStyle: item.active ? 'normal' : 'italic',
                    }}
                  >
                    {item.icon}
                  </span>
                  <span className="font-medium whitespace-nowrap">{item.label}</span>
                </button>
              ))}
            </div>
            <div style={{ borderTop: '0.5px solid rgba(255,255,255,0.05)', paddingTop: 8 }}>
              <button
                className="flex items-center gap-[10px] py-[7px] px-[10px] border-0 rounded-[7px] cursor-pointer text-[12.5px]"
                style={{ background: 'transparent', color: 'rgba(250,241,226,0.65)' }}
              >
                <span className="w-5 h-5 grid place-items-center rounded-[5px] text-xs" style={{ background: 'rgba(255,255,255,0.04)', color: 'rgba(250,241,226,0.85)' }}>⚙</span>
                <span className="font-medium whitespace-nowrap">{t('tutorPreview.settings')}</span>
              </button>
            </div>
          </aside>

          {/* Main area */}
          <div className="grid place-items-center p-8 relative overflow-hidden">
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                background: 'radial-gradient(circle at 20% 30%, rgba(232,116,59,0.08), transparent 50%), radial-gradient(circle at 80% 70%, rgba(244,168,106,0.05), transparent 50%)',
              }}
            />
            <div className="w-full max-w-[720px] flex flex-col gap-[22px] relative z-[1]">
              {/* Greeting */}
              <div className="flex items-center justify-center gap-3">
                <img src="/assets/catobi-avatar.png" alt="Catobi" className="w-9 h-9 rounded-full" />
                <h3 style={{ fontFamily: 'var(--font-serif)', fontWeight: 400, fontStyle: 'italic', fontSize: 'clamp(28px, 3vw, 38px)', letterSpacing: '-0.01em', color: '#FAF1E2', margin: 0 }}>
                  {t('tutorPreview.greeting')}
                </h3>
              </div>

              {/* Input box */}
              <div
                className="flex flex-col gap-[14px] p-4 rounded-[14px] transition-colors duration-150"
                style={{ background: 'rgba(255,255,255,0.035)', border: '0.5px solid rgba(255,255,255,0.1)' }}
              >
                <div className="flex items-start gap-1 p-[4px_6px] min-h-[56px]" style={{ fontSize: 14.5, color: 'rgba(250,241,226,0.45)' }}>
                  {t('tutorPreview.placeholder')}
                  <span className="inline-block w-[1.5px] h-[18px] mt-[1px]" style={{ background: 'var(--orange)', animation: 'blink 1.1s infinite' }} />
                </div>
                <div className="flex items-center gap-[6px] flex-wrap">
                  {/* Mode selector */}
                  <div className="inline-flex items-center gap-[2px] p-[2px] pr-2 rounded-lg" style={{ background: 'rgba(255,255,255,0.04)', border: '0.5px solid rgba(255,255,255,0.06)' }}>
                    {[
                      { id: 'chat', label: t('navTree.tutor.chat') },
                      { id: 'tutorbot', label: t('navTree.tutor.tutorbot') },
                      { id: 'cowriter', label: t('navTree.tutor.cowriter') },
                    ].map((m) => (
                      <button
                        key={m.id}
                        className="border-0 bg-transparent text-[11.5px] font-medium py-[5px] px-[10px] rounded-[6px] cursor-pointer transition-colors duration-[120ms]"
                        style={{
                          color: mode === m.id ? '#FAF1E2' : 'rgba(250,241,226,0.55)',
                          background: mode === m.id ? 'var(--bg-2)' : 'transparent',
                          boxShadow: mode === m.id ? '0 1px 2px rgba(0,0,0,0.3)' : 'none',
                        }}
                        onClick={() => setMode(m.id)}
                      >
                        {m.label}
                      </button>
                    ))}
                  </div>
                  <ToolButton label={t('tutorPreview.attach')} icon="📎" />
                  <ToolButton label="Knowledge" icon="◉" />
                  <div className="flex-1" />
                  <span
                    className="inline-flex items-center gap-[6px] px-[10px] py-[6px] rounded-lg text-[11px] cursor-pointer"
                    style={{ background: 'rgba(255,255,255,0.04)', border: '0.5px solid rgba(255,255,255,0.06)', color: 'rgba(250,241,226,0.65)', fontFamily: 'var(--font-mono)' }}
                  >
                    <span className="w-[6px] h-[6px] rounded-full" style={{ background: 'var(--orange-l)', boxShadow: '0 0 0 2px rgba(244,168,106,0.2)' }} />
                    CatoBigato 
                  </span>
                  <button
                    className="w-8 h-8 rounded-full border-0 grid place-items-center cursor-pointer ml-[2px] transition-all duration-150"
                    style={{ background: 'var(--orange)', color: '#1B1410' }}
                    title={t('tutorPreview.send')}
                  >
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                      <path d="M 8 13 L 8 3 M 4 7 L 8 3 L 12 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Example chips */}
              <div className="flex items-center gap-2 flex-wrap mt-1">
                <span className="text-[11px] font-semibold mr-1" style={{ letterSpacing: '0.06em', textTransform: 'uppercase', color: 'rgba(250,241,226,0.4)' }}>{t('tutorPreview.chipLabel')}</span>
                {examples.map((ex, i) => (
                  <button
                    key={i}
                    className="border-0 rounded-full py-2 px-[14px] text-xs cursor-pointer transition-all duration-[120ms]"
                    style={{ background: 'rgba(255,255,255,0.025)', border: '0.5px solid rgba(255,255,255,0.1)', color: 'rgba(250,241,226,0.78)' }}
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function ToolButton({ label, icon }: { label: string; icon: string }) {
  return (
    <button
      className="inline-flex items-center gap-[6px] px-[10px] py-[6px] rounded-lg text-[11.5px] cursor-pointer border-0 transition-colors duration-[120ms]"
      style={{ background: 'rgba(255,255,255,0.04)', border: '0.5px solid rgba(255,255,255,0.06)', color: 'rgba(250,241,226,0.65)' }}
    >
      <span style={{ fontSize: 12 }}>{icon}</span>
      {label}
    </button>
  )
}

// ── CALC PREVIEW ─────────────────────────────────────────────────────────────
function CalcPreview() {
  const { t } = useTranslation()

  return (
    <section className="mx-auto" style={{ maxWidth: 1240, padding: '24px 32px 64px' }} id="calculator">
      <div className="calc-grid grid gap-10 items-center" style={{ gridTemplateColumns: '1fr 1.1fr' }}>
        <div>
          <SectionTag text={t('calcPreview.tag')} />
          <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: 'clamp(28px, 3vw, 40px)', margin: '0 0 14px', fontWeight: 400, letterSpacing: '-0.015em', lineHeight: 1.05 }}>
            {t('calcPreview.title_pre')}<em style={{ fontStyle: 'italic', color: 'var(--orange)' }}>{t('calcPreview.title_em')}</em>
          </h3>
          <p style={{ color: 'var(--ink-soft)', fontSize: 14.5, maxWidth: '44ch' }}>{t('calcPreview.desc')}</p>
          <ul className="flex flex-col gap-2 mt-[18px] p-0 list-none">
            {[t('calcPreview.list1'), t('calcPreview.list2'), t('calcPreview.list3'), t('calcPreview.list4')].map((item, i) => (
              <li key={i} className="flex gap-[10px] items-start text-[13.5px]" style={{ color: 'var(--ink)' }}>
                <svg className="shrink-0 mt-1" width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M2 7 L 6 11 L 12 3" stroke="var(--orange)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                {item}
              </li>
            ))}
          </ul>
        </div>

        {/* Calc screen */}
        <div
          className="rounded-[18px] p-[18px] relative overflow-hidden"
          style={{
            background: 'var(--ink)',
            color: '#FAF5EC',
            boxShadow: '0 30px 60px -30px rgba(42,30,18,0.5)',
            fontFamily: 'var(--font-mono)',
          }}
        >
          <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(circle at 20% 0%, rgba(232,116,59,0.1), transparent 50%)' }} />
          {/* Tabs */}
          <div className="flex gap-1 mb-3 relative">
            {[{ label: t('calcPreview.tabSolve'), on: true }, { label: t('calcPreview.tabGraph') }, { label: t('calcPreview.tabNotes') }].map((tab, i) => (
              <button
                key={i}
                className="text-[11px] py-1 px-[10px] rounded-full border-0"
                style={{
                  background: tab.on ? 'var(--orange)' : 'rgba(255,255,255,0.06)',
                  color: tab.on ? 'white' : 'rgba(250,245,236,0.6)',
                }}
              >
                {tab.label}
              </button>
            ))}
            <span className="ml-auto text-[11px]" style={{ background: 'transparent', color: 'rgba(250,245,236,0.4)' }}>x² · √ · π</span>
          </div>
          {/* Expression */}
          <div
            className="flex items-center gap-2 text-[22px] p-[12px_14px] rounded-[10px] mb-3 relative z-[1]"
            style={{ background: 'rgba(255,255,255,0.04)' }}
          >
            <span style={{ color: 'rgba(250,245,236,0.45)' }}>∫</span>
            <span>(3x² + 2x) dx</span>
            <span className="inline-block w-[2px] h-[22px]" style={{ background: 'var(--orange)', animation: 'blink 1.1s infinite' }} />
          </div>
          {/* Result */}
          <div className="text-[13px] px-[14px] pb-[14px]" style={{ color: 'rgba(250,245,236,0.55)' }}>
            <span style={{ color: 'var(--orange-l)' }}>cato </span>
            <span>= </span>
            <b style={{ color: 'var(--orange-l)', fontWeight: 600 }}>x³ + x² + C</b>
            <div className="mt-2 text-[11.5px] leading-[1.5]" style={{ color: 'rgba(250,245,236,0.5)' }}>
              {t('calcPreview.explain')} ✨
            </div>
          </div>
          {/* Graph */}
          <div className="rounded-[10px] h-[180px] relative z-[1]" style={{ background: 'rgba(255,255,255,0.03)' }}>
            <svg width="100%" height="100%" viewBox="0 0 400 180" preserveAspectRatio="none">
              {[...Array(8)].map((_, i) => <line key={`v${i}`} x1={i * 50} y1="0" x2={i * 50} y2="180" stroke="rgba(250,245,236,0.06)" />)}
              {[...Array(4)].map((_, i) => <line key={`h${i}`} x1="0" y1={i * 45} x2="400" y2={i * 45} stroke="rgba(250,245,236,0.06)" />)}
              <line x1="0" y1="135" x2="400" y2="135" stroke="rgba(250,245,236,0.25)" strokeWidth="1" />
              <line x1="60" y1="0" x2="60" y2="180" stroke="rgba(250,245,236,0.25)" strokeWidth="1" />
              <path d="M 0 178 Q 80 150 140 130 Q 200 100 260 60 Q 320 30 400 5" stroke="var(--orange)" strokeWidth="2.5" fill="none" strokeLinecap="round" />
              <path d="M 0 165 Q 100 155 200 120 Q 300 60 400 -20" stroke="rgba(244,168,106,0.55)" strokeWidth="1.5" fill="none" strokeDasharray="3 3" />
              <circle cx="260" cy="60" r="4" fill="var(--orange)" />
              <circle cx="260" cy="60" r="8" fill="var(--orange)" opacity="0.25" />
            </svg>
          </div>
        </div>
      </div>
    </section>
  )
}

// ── SUBJECTS STRIP ───────────────────────────────────────────────────────────
function SubjectsStrip() {
  const { t } = useTranslation()

  return (
    <section className="mx-auto pb-8" style={{ maxWidth: 1240, padding: '24px 32px 32px' }}>
      <div className="subjects-head grid items-end gap-6 mb-7" style={{ gridTemplateColumns: '1fr auto' }}>
        <div>
          <SectionTag text={t('subjectsStrip.tag')} />
          <h2 style={{ fontFamily: 'var(--font-serif)', fontWeight: 400, fontSize: 'clamp(32px, 3.6vw, 46px)', lineHeight: 1.02, letterSpacing: '-0.015em', margin: 0 }}>
            {t('subjectsStrip.title_pre')}<em style={{ fontStyle: 'italic', color: 'var(--orange)' }}>{t('subjectsStrip.title_em')}</em>{t('subjectsStrip.title_post')}
          </h2>
        </div>
        <p className="hidden md:block" style={{ fontSize: 14.5, color: 'var(--ink-soft)', maxWidth: '36ch', margin: 0 }}>{t('subjectsStrip.desc')}</p>
      </div>
      <div className="subjects-grid grid gap-[10px]" style={{ gridTemplateColumns: 'repeat(6, 1fr)' }}>
        {SUBJECTS.map((s) => (
          <a
            key={s.id}
            href={`#visual-${s.id}`}
            className="flex items-center gap-[10px] p-[14px_16px] rounded-full transition-all duration-150 no-underline hover:-translate-y-[2px]"
            style={{
              ['--accent' as string]: s.accent,
              background: 'var(--bg)',
              border: '0.5px solid var(--rule)',
            }}
          >
            <span
              className="w-7 h-7 rounded-full grid place-items-center shrink-0 text-sm"
              style={{
                background: `color-mix(in oklab, ${s.accent} 14%, var(--bg))`,
                color: s.accent,
                fontFamily: 'var(--font-serif)',
                fontStyle: s.icon.length > 1 ? 'normal' : 'italic',
              }}
            >
              {s.icon}
            </span>
            <span className="text-[13.5px] font-medium" style={{ color: 'var(--ink)' }}>{t(s.nameKey)}</span>
          </a>
        ))}
      </div>
    </section>
  )
}

// ── FLOW (How It Works) ──────────────────────────────────────────────────────
function Flow() {
  const { t } = useTranslation()

  return (
    <section
      id="how"
      style={{
        background: 'var(--bg-2)',
        borderTop: '0.5px solid var(--rule)',
        borderBottom: '0.5px solid var(--rule)',
        padding: '72px 32px',
      }}
    >
      <div className="mx-auto" style={{ maxWidth: 1240 }}>
        <SectionTag text={t('flow.tag')} />
        <div className="flex items-end justify-between gap-6 mb-3">
          <h2 style={{ fontFamily: 'var(--font-serif)', fontWeight: 400, fontSize: 'clamp(32px, 3.6vw, 46px)', lineHeight: 1.02, letterSpacing: '-0.015em', margin: 0 }}>
            {t('flow.title_pre')}<em style={{ fontStyle: 'italic', color: 'var(--orange)' }}>{t('flow.title_em')}</em>{t('flow.title_post')}
          </h2>
          <p className="hidden md:block" style={{ fontSize: 14.5, color: 'var(--ink-soft)', maxWidth: '40ch', margin: 0 }}>{t('flow.desc')}</p>
        </div>
        <div className="flow-grid grid mt-9 relative" style={{ gridTemplateColumns: 'repeat(5, 1fr)', gap: 0 }}>
          {FLOW_NUMS.map((n, i) => (
            <div key={i} className="relative px-[18px]">
              {i < 4 && (
                <div
                  className="flow-arrow absolute w-5 h-3"
                  style={{
                    right: -10,
                    top: 22,
                    background: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 12'><path d='M1 6 H 16 M 11 1 L 18 6 L 11 11' fill='none' stroke='%23E8743B' stroke-width='1.4' stroke-linecap='round' stroke-linejoin='round' opacity='0.65'/></svg>") center/contain no-repeat`,
                  }}
                />
              )}
              <div style={{ fontFamily: 'var(--font-serif)', fontStyle: 'italic', fontSize: 38, color: 'var(--orange)', lineHeight: 1, marginBottom: 8, letterSpacing: '-0.02em' }}>{n}</div>
              <h4 style={{ fontFamily: 'var(--font-serif)', fontSize: 22, fontWeight: 400, letterSpacing: '-0.01em', margin: '0 0 8px' }}>{t(`flow.step${i + 1}_title`)}</h4>
              <p style={{ fontSize: 13, color: 'var(--ink-soft)', margin: 0, lineHeight: 1.5 }}>{t(`flow.step${i + 1}_desc`)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// ── RIBBON ────────────────────────────────────────────────────────────────────
function Ribbon() {
  const { t } = useTranslation()
  const cells = [
    { num: <>73<em style={{ fontStyle: 'italic', color: 'var(--orange)' }}>k</em></>, label: t('ribbon.label1') },
    { num: <><em style={{ fontStyle: 'italic', color: 'var(--orange)' }}>4.9</em>/5</>, label: t('ribbon.label2') },
    { num: '12+', label: t('ribbon.label3') },
    { num: <>2<em style={{ fontStyle: 'italic', color: 'var(--orange)' }}>s</em></>, label: t('ribbon.label4') },
  ]

  return (
    <section className="mx-auto" style={{ maxWidth: 1240, padding: '24px 32px 0' }}>
      <div
        className="ribbon-grid grid overflow-hidden"
        style={{
          gridTemplateColumns: 'repeat(4, 1fr)',
          border: '0.5px solid var(--rule)',
          borderRadius: 'var(--r-3)',
          background: 'var(--bg)',
        }}
      >
        {cells.map((cell, i) => (
          <div key={i} className="p-[22px_24px]" style={{ borderRight: i < 3 ? '0.5px solid var(--rule)' : 'none' }}>
            <div style={{ fontFamily: 'var(--font-serif)', fontSize: 40, lineHeight: 1, letterSpacing: '-0.02em', color: 'var(--ink)' }}>{cell.num}</div>
            <div className="mt-2 text-xs font-medium" style={{ color: 'var(--ink-muted)' }}>{cell.label}</div>
          </div>
        ))}
      </div>
    </section>
  )
}

// ── QUOTE ────────────────────────────────────────────────────────────────────
function Quote() {
  const { t } = useTranslation()

  return (
    <section className="mx-auto" style={{ maxWidth: 1240, padding: '24px 32px 64px' }}>
      <div
        className="quote-grid grid items-center gap-7 p-8 mt-12"
        style={{
          gridTemplateColumns: '200px 1fr',
          background: 'var(--bg)',
          border: '0.5px solid var(--rule)',
          borderRadius: 'var(--r-3)',
        }}
      >
        {/* Mascot peek */}
        <div className="w-[200px] h-[200px] relative grid place-items-center">
          <div className="absolute inset-0 rounded-full" style={{ background: 'radial-gradient(circle, #FBE7C9 0%, rgba(251,231,201,0.4) 60%, transparent 80%)' }} />
          <img
            src="/assets/catobi-head.png"
            alt="Catobi"
            className="relative w-[95%] h-[95%] object-contain"
            style={{ filter: 'drop-shadow(0 8px 14px rgba(201,90,34,0.18))' }}
          />
        </div>
        <div>
          <blockquote style={{ fontFamily: 'var(--font-serif)', fontSize: 'clamp(22px, 2.2vw, 30px)', fontWeight: 400, lineHeight: 1.25, letterSpacing: '-0.01em', margin: 0, color: 'var(--ink)' }}>
            {t('quote.text_pre')}<em style={{ fontStyle: 'italic', color: 'var(--orange)' }}>{t('quote.text_em')}</em>{t('quote.text_post')}
          </blockquote>
          <div className="mt-[14px] text-xs font-semibold" style={{ color: 'var(--ink-muted)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            — Catobi · {t('quote.attr')}
          </div>
        </div>
      </div>
    </section>
  )
}

// ── SECTION TAG HELPER ───────────────────────────────────────────────────────
function SectionTag({ text }: { text: string }) {
  return (
    <div
      className="flex items-center gap-2 mb-[14px]"
      style={{ fontSize: 11.5, fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--ink-muted)' }}
    >
      <span className="inline-block w-[18px] h-[1px]" style={{ background: 'currentColor' }} />
      {text}
    </div>
  )
}
