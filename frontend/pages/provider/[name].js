import Head from 'next/head';
import Link from 'next/link';

import CourseList from '../../components/CourseList';
import Footer from '../../components/Footer';
import Header from '../../components/Header';
import { getCoursesByProvider } from '../../services/api';
import { buildSeo } from '../../utils/seo';

function sortByRating(courses = []) {
  return [...courses].sort((a, b) => (Number(b.rating) || 0) - (Number(a.rating) || 0));
}

export default function ProviderPage({ name, courses }) {
  const seo = buildSeo({
    title: `Provider: ${name} | Course Aggregator`,
    description: `Courses from provider ${name}.`
  });

  const topCourses = sortByRating(courses).slice(0, 5);

  return (
    <>
      <Head>
        <title>{seo.title}</title>
        <meta name="description" content={seo.description} />
        <meta property="og:title" content={seo.openGraph.title} />
        <meta property="og:description" content={seo.openGraph.description} />
        <meta property="og:url" content={seo.openGraph.url} />
      </Head>
      <Header />
      <main className="container-page space-y-6 py-10">
        <h1 className="text-3xl font-bold">Provider: {name}</h1>

        <section className="rounded-xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Top courses from {name}</h2>
          <ul className="mt-3 list-inside list-disc space-y-1">
            {topCourses.map((course) => (
              <li key={course.slug}>
                <Link href={`/course/${course.slug}`}>{course.title}</Link>
              </li>
            ))}
          </ul>
        </section>

        <CourseList courses={courses} />
      </main>
      <Footer />
    </>
  );
}

export async function getServerSideProps({ params }) {
  try {
    const data = await getCoursesByProvider(params.name);
    return {
      props: {
        name: params.name,
        courses: data.courses || []
      }
    };
  } catch {
    return {
      props: {
        name: params.name,
        courses: []
      }
    };
  }
}
