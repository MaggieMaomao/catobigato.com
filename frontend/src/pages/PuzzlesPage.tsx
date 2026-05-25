import { useTranslation } from 'react-i18next';

export default function PuzzlesPage() {
  const { t } = useTranslation();
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-[--ink] mb-6">{t('nav.puzzles')}</h1>
      <p className="text-secondary">Puzzle management coming in Phase 4.</p>
    </div>
  );
}