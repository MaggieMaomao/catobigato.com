import { useTranslation } from 'react-i18next';

export default function SocialPage() {
  const { t } = useTranslation();
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-[--color-text-heading] mb-6">{t('nav.social')}</h1>
      <p className="text-secondary">Social features coming in Phase 5.</p>
    </div>
  );
}