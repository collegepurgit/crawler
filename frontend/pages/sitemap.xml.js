import {
  buildSitemapIndexXml,
  fetchCoursesTotal,
  MAX_URLS_PER_SITEMAP,
  SITE_URL
} from '../utils/sitemap';

export async function getServerSideProps({ res }) {
  const sitemapUrls = [`${SITE_URL}/sitemaps/static.xml`];

  try {
    const totalCourses = await fetchCoursesTotal();
    const chunks = Math.max(1, Math.ceil(totalCourses / MAX_URLS_PER_SITEMAP));

    for (let i = 0; i < chunks; i += 1) {
      sitemapUrls.push(`${SITE_URL}/sitemaps/courses-${i + 1}.xml`);
    }
  } catch {
    sitemapUrls.push(`${SITE_URL}/sitemaps/courses-1.xml`);
  }

  const xml = buildSitemapIndexXml(sitemapUrls);
  res.setHeader('Content-Type', 'text/xml');
  res.write(xml);
  res.end();

  return { props: {} };
}

export default function SitemapIndexXml() {
  return null;
}
