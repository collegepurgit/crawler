import Head from 'next/head';

import seoKeywordConfig from '../config/seo-keywords.json';
import Footer from '../components/Footer';
import Header from '../components/Header';
import SeoCategoryTemplate from '../components/SeoCategoryTemplate';
import { getCoursesByCategory, PAGE_SIZE, searchCourses } from '../services/api';
import { buildSeo } from '../utils/seo';
import { seoFaqs, sortCoursesByRating } from '../utils/seoPages';

function getSeoEntryBySlug(slug) {
  const entries = seoKeywordConfig?.entries || [];
  return entries.find((entry) => entry.slug === slug) || null;
}

export default function SeoCourseListingPage({ seoSlug, heading, description, categoryLabel, courses, total, limit, page }) {
  const pageSeo = buildSeo({
    title: heading + ' Online',
    description,
    url: `http://localhost:3000/${seoSlug}`
  });

  return (
    <>
      <Head>
        <title>{pageSeo.title}</title>
        <meta name="description" content={pageSeo.description} />
        <meta property="og:title" content={pageSeo.openGraph.title} />
        <meta property="og:description" content={pageSeo.openGraph.description} />
        <meta property="og:url" content={pageSeo.openGraph.url} />
        <meta property="og:image" content={pageSeo.openGraph.image} />
        <meta name="robots" content="index,follow" />
        <link rel="canonical" href={`http://localhost:3000/${seoSlug}`} />
      </Head>

      <Header />

      <SeoCategoryTemplate
        seoSlug={seoSlug}
        heading={heading}
        intro={description}
        courses={courses}
        total={total}
        limit={limit}
        page={page}
        faqs={seoFaqs(categoryLabel)}
      />

      <Footer />
    </>
  );
}

export async function getServerSideProps({ params, query }) {
  const seoEntry = getSeoEntryBySlug(params.seoSlug);
  if (!seoEntry) {
    return { notFound: true };
  }

  const page = Math.max(1, Number(query.page || 1));

  try {
    let ranked = [];

    if (seoEntry.source === 'category') {
      const data = await getCoursesByCategory(seoEntry.category_slug);
      ranked = sortCoursesByRating(data.courses || []);
    } else {
      const searchData = await searchCourses(seoEntry.keyword);
      ranked = sortCoursesByRating(searchData.courses || []);
    }

    const offset = (page - 1) * PAGE_SIZE;

    return {
      props: {
        seoSlug: params.seoSlug,
        heading: seoEntry.heading,
        description: seoEntry.description,
        categoryLabel: seoEntry.category,
        courses: ranked.slice(offset, offset + PAGE_SIZE),
        total: ranked.length,
        limit: PAGE_SIZE,
        page
      }
    };
  } catch {
    return {
      props: {
        seoSlug: params.seoSlug,
        heading: seoEntry.heading,
        description: seoEntry.description,
        categoryLabel: seoEntry.category,
        courses: [],
        total: 0,
        limit: PAGE_SIZE,
        page
      }
    };
  }
}
