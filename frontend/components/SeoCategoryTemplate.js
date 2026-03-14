import CourseList from './CourseList';
import Pagination from './Pagination';
import SeoFaqSection from './SeoFaqSection';

export default function SeoCategoryTemplate({
  seoSlug,
  heading,
  intro,
  courses,
  total,
  limit,
  page,
  faqs
}) {
  return (
    <main className="container-page space-y-6 py-10">
      <section className="rounded-xl bg-white p-6 shadow-sm">
        <h1 className="text-3xl font-bold">{heading}</h1>
        <p className="mt-2 text-slate-600">{intro}</p>
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Top Rated Courses</h2>
        <CourseList courses={courses} />
      </section>

      <Pagination page={page} total={total} limit={limit} basePath={`/${seoSlug}`} extraQuery={{}} />

      <SeoFaqSection faqs={faqs} />
    </main>
  );
}
