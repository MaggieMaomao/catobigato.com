import { useTranslation } from 'react-i18next';

export default function HomePage() {
  const { t } = useTranslation();

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Hero section */}
      <div className="py-20 text-center">
        <h1 className="text-5xl font-bold text-[--color-text-heading] mb-4">
          {t('app.name')}
        </h1>
        <p className="text-lg text-secondary mb-8">{t('app.tagline')}</p>

        {/* Feature cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-12 text-left">
          <FeatureCard
            title={t('calculator.title')}
            desc="Basic, scientific, calculus, algebra, and graphing — all in one."
            href="/calculator"
          />
          <FeatureCard
            title={t('learning.notes')}
            desc="Create notes, build question sets, and track your learning."
            href="/learning"
          />
          <FeatureCard
            title={t('nav.puzzles')}
            desc="Practice with curriculum-aligned puzzles and problems."
            href="/puzzles"
          />
          <FeatureCard
            title={t('nav.social')}
            desc="Follow friends, join study groups, share progress."
            href="/social"
          />
          <FeatureCard
            title={t('subjects.physics')}
            desc="Interactive physics formulas and visualizations."
            href="/learning?subject=physics"
          />
          <FeatureCard
            title={t('subjects.math')}
            desc="Custom functions, symbolic math, and graphing tools."
            href="/calculator?mode=algebra"
          />
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ title, desc, href }: { title: string; desc: string; href: string }) {
  return (
    <a
      href={href}
      className="block p-6 rounded-lg border border-border bg-bg hover:border-primary hover:shadow-md transition-all group"
    >
      <h3 className="text-lg font-semibold text-[--color-text-heading] mb-2 group-hover:text-primary transition-colors">
        {title}
      </h3>
      <p className="text-sm text-secondary">{desc}</p>
    </a>
  );
}