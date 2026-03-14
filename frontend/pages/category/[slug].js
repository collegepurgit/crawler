import Head from 'next/head';
import Link from 'next/link';

import CourseList from '../../components/CourseList';
import Footer from '../../components/Footer';
import Header from '../../components/Header';
import { getCoursesByCategory } from '../../services/api';
import { buildSeo } from '../../utils/seo';

export default function CategoryPage({ slug, courses }) {
  const seo = buildSeo({
    title: `Category: ${slug} | Course Aggregator`,
    description: `Courses in category ${slug}.`
  });

  const seoLinks = [
    { href: `/best-${slug}-courses`, label: `Best ${slug} courses` },
    { href: `/free-${slug}-courses`, label: `Free ${slug} courses` },
    { href: `/beginner-${slug}-courses`, label: `Beginner ${slug} courses` }
  ];

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
        <h1 className="text-3xl font-bold">Category: {slug}</h1>

        <section className="rounded-xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Explore more {slug} guides</h2>
          <ul className="mt-3 list-inside list-disc space-y-1">
            {seoLinks.map((item) => (
              <li key={item.href}>
                <Link href={item.href}>{item.label}</Link>
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
    const data = await getCoursesByCategory(params.slug);
    return {
      props: {
        slug: params.slug,
        courses: data.courses || []
      }
    };
  } catch {
    return {
      props: {
        slug: params.slug,
        courses: []
      }
    };
  }
}
