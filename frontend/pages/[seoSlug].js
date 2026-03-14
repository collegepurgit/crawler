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

function buildEntryMetadata(seoEntry) {
  return buildSeo({
    title: seoEntry.title || `${seoEntry.heading} Online`,
    description: seoEntry.description,
    url: seoEntry.canonical_url || `${seoKeywordConfig?.site_url || 'http://localhost:3000'}${seoEntry.url_path || `/${seoEntry.slug}`}`,
  });
}

export default function SeoCourseListingPage({ seoEntry, courses, total, limit, page }) {
  const pageSeo = buildEntryMetadata(seoEntry);

  return (
    <>
      <Head>
        <title>{seoEntry.title || pageSeo.title}</title>
        <meta name="description" content={seoEntry.description || pageSeo.description} />
        <meta property="og:title" content={seoEntry.og_title || pageSeo.openGraph.title} />
        <meta property="og:description" content={seoEntry.og_description || pageSeo.openGraph.description} />
        <meta property="og:url" content={seoEntry.og_url || pageSeo.openGraph.url} />
        <meta property="og:image" content={pageSeo.openGraph.image} />
        <meta name="robots" content="index,follow" />
        <link rel="canonical" href={seoEntry.canonical_url || pageSeo.openGraph.url} />
      </Head>

      <Header />

      <SeoCategoryTemplate
        seoSlug={seoEntry.slug}
        heading={seoEntry.heading}
        intro={seoEntry.description}
        courses={courses}
        total={total}
        limit={limit}
        page={page}
        faqs={seoFaqs(seoEntry.category)}
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
        seoEntry,
        courses: ranked.slice(offset, offset + PAGE_SIZE),
        total: ranked.length,
        limit: PAGE_SIZE,
        page
      }
    };
  } catch {
    return {
      props: {
        seoEntry,
        courses: [],
        total: 0,
        limit: PAGE_SIZE,
        page
      }
    };
  }
}
