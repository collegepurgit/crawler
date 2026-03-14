const SEO_SLUG_PATTERN = /^(best|free|beginner)-(.+)-courses$/;

export function parseSeoSlug(slug) {
  const match = slug?.match(SEO_SLUG_PATTERN);
  if (!match) return null;

  const modifier = match[1];
  const categorySlug = match[2];
  const categoryLabel = categorySlug
    .split('-')
    .filter(Boolean)
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(' ');

  return { modifier, categorySlug, categoryLabel };
}

export function seoPageTitle(modifier, categoryLabel) {
  const prefix = modifier[0].toUpperCase() + modifier.slice(1);
  return `${prefix} ${categoryLabel} Courses Online`;
}

export function seoPageHeading(modifier, categoryLabel) {
  const prefix = modifier[0].toUpperCase() + modifier.slice(1);
  return `${prefix} ${categoryLabel} Courses`;
}

export function seoPageDescription(modifier, categoryLabel) {
  switch (modifier) {
    case 'best':
      return `Explore the best ${categoryLabel} courses available online from top platforms.`;
    case 'free':
      return `Discover free ${categoryLabel} courses to start learning without cost.`;
    case 'beginner':
      return `Find beginner ${categoryLabel} courses designed for newcomers and early learners.`;
    default:
      return `Browse ${categoryLabel} courses online.`;
  }
}

export function seoFaqs(categoryLabel) {
  return [
    {
      question: `How do I start learning ${categoryLabel}?`,
      answer: `Start with beginner-friendly ${categoryLabel} courses, practice consistently, and build small projects to apply what you learn.`
    },
    {
      question: `How long does it take to learn ${categoryLabel}?`,
      answer: `Most learners build foundational ${categoryLabel} skills in a few weeks to a few months depending on pace and prior experience.`
    },
    {
      question: `Are online ${categoryLabel} courses worth it?`,
      answer: `Yes. High-quality online ${categoryLabel} courses provide structured lessons, practical exercises, and flexibility to learn at your own pace.`
    }
  ];
}

export function sortCoursesByRating(courses = []) {
  return [...courses].sort((a, b) => (Number(b.rating) || 0) - (Number(a.rating) || 0));
}
