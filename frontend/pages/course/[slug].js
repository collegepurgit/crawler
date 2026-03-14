import Head from 'next/head';
import Link from 'next/link';

import Footer from '../../components/Footer';
import Header from '../../components/Header';
import { getCourse, getCoursesByCategory } from '../../services/api';
import { buildSeo } from '../../utils/seo';

function slugifyCategory(name = '') {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-');
}

function sortByRating(courses = []) {
  return [...courses].sort((a, b) => (Number(b.rating) || 0) - (Number(a.rating) || 0));
}

export default function CourseDetailPage({ course, relatedCourses }) {
  const seo = buildSeo({
    title: course ? `${course.title} | Course Aggregator` : 'Course Not Found | Course Aggregator',
    description: course?.description || 'Explore detailed course information.'
  });

  if (!course) {
    return (
      <>
        <Head>
          <title>{seo.title}</title>
          <meta name="description" content={seo.description} />
        </Head>
        <Header />
        <main className="container-page py-16">
          <h1 className="text-3xl font-bold">Course not found</h1>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Head>
        <title>{seo.title}</title>
        <meta name="description" content={seo.description} />
        <meta property="og:title" content={seo.openGraph.title} />
        <meta property="og:description" content={seo.openGraph.description} />
        <meta property="og:url" content={seo.openGraph.url} />
        <meta property="og:image" content={course.image_url || seo.openGraph.image} />
      </Head>
      <Header />
      <main className="container-page py-10 space-y-6">
        <article className="grid gap-8 rounded-xl bg-white p-6 shadow-sm lg:grid-cols-[2fr_1fr]">
          <div className="space-y-4">
            <h1 className="text-3xl font-bold">{course.title}</h1>
            <p className="text-slate-600">Provider: {course.provider}</p>
            <p className="text-amber-600">⭐ {course.rating ?? 'N/A'}</p>
            <p className="leading-7 text-slate-700">{course.description || 'No description provided.'}</p>

            <div>
              <h2 className="font-semibold">Instructors</h2>
              <ul className="list-inside list-disc text-slate-700">
                {(course.instructors || []).map((instructor) => (
                  <li key={instructor}>{instructor}</li>
                ))}
              </ul>
            </div>

            <div>
              <h2 className="font-semibold">Categories</h2>
              <div className="mt-2 flex flex-wrap gap-2">
                {(course.categories || []).map((category) => {
                  const categorySlug = slugifyCategory(category);
                  return (
                    <Link
                      key={category}
                      href={`/category/${categorySlug}`}
                      className="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-700 no-underline hover:bg-blue-200"
                    >
                      {category}
                    </Link>
                  );
                })}
              </div>
            </div>

            <a
              href={course.course_url}
              target="_blank"
              rel="noreferrer"
              className="inline-block rounded-md bg-blue-600 px-5 py-3 font-semibold text-white no-underline hover:bg-blue-700"
            >
              Enroll Now
            </a>
          </div>

          <div>
            <img
              src={course.image_url || 'https://placehold.co/700x500?text=Course'}
              alt={course.title}
              className="w-full rounded-lg object-cover"
            />
          </div>
        </article>

        <section className="rounded-xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Related courses in the same category</h2>
          {relatedCourses.length ? (
            <ul className="mt-3 list-inside list-disc space-y-1">
              {relatedCourses.map((item) => (
                <li key={item.slug}>
                  <Link href={`/course/${item.slug}`}>{item.title}</Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-slate-600">No related courses available right now.</p>
          )}
        </section>
      </main>
      <Footer />
    </>
  );
}

export async function getServerSideProps({ params, res }) {
  try {
    const course = await getCourse(params.slug);
    const firstCategory = (course.categories || [])[0] || '';
    const categorySlug = slugifyCategory(firstCategory);

    let relatedCourses = [];
    if (categorySlug) {
      const categoryData = await getCoursesByCategory(categorySlug);
      relatedCourses = sortByRating(categoryData.courses || [])
        .filter((item) => item.slug !== params.slug)
        .slice(0, 6);
    }

    return { props: { course, relatedCourses } };
  } catch {
    res.statusCode = 404;
    return { props: { course: null, relatedCourses: [] } };
  }
}
