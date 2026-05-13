import { useTranslation } from 'react-i18next';

export default function LearningPage() {
  const { t } = useTranslation();
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-[--color-text-heading] mb-6">{t('nav.learning')}</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {[
          { key: 'notes', title: t('learning.notes'), href: '/learning/notes' },
          { key: 'questionSets', title: t('learning.questionSets'), href: '/learning/question-sets' },
          { key: 'exams', title: t('learning.exams'), href: '/learning/exams' },
          { key: 'statistics', title: t('learning.statistics'), href: '/learning/statistics' },
        ].map((item) => (
          <a key={item.key} href={item.href} className="p-6 border border-border rounded-lg hover:border-primary transition-colors">
            <h3 className="text-lg font-semibold text-[--color-text-heading]">{item.title}</h3>
          </a>
        ))}
      </div>
    </div>
  );
}