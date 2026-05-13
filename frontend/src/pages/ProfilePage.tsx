import { useTranslation } from 'react-i18next';

export default function ProfilePage() {
  const { t } = useTranslation();
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-[--color-text-heading] mb-6">{t('nav.profile')}</h1>
      <div className="border border-border rounded-lg p-6 text-secondary">
        Profile settings will be available after sign-in.
      </div>
    </div>
  );
}