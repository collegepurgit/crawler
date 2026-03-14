import {
  buildUrlsetXml,
  fetchCourseUrlsChunk,
  fetchCoursesTotal,
  fetchStaticUrls,
  MAX_URLS_PER_SITEMAP
} from '../../utils/sitemap';

function parseCourseChunk(sitemapId) {
  const match = sitemapId.match(/^courses-(\d+)$/);
  if (!match) return null;

  const chunkNumber = Number(match[1]);
  if (!Number.isInteger(chunkNumber) || chunkNumber <= 0) return null;
  return chunkNumber - 1;
}

export async function getServerSideProps({ params, res }) {
  const sitemapId = params?.sitemapId || '';

  try {
    if (sitemapId === 'static') {
      const staticUrls = await fetchStaticUrls();
      const xml = buildUrlsetXml(staticUrls);
      res.setHeader('Content-Type', 'text/xml');
      res.write(xml);
      res.end();
      return { props: {} };
    }

    const chunkIndex = parseCourseChunk(sitemapId);
    if (chunkIndex === null) {
      return { notFound: true };
    }

    const totalCourses = await fetchCoursesTotal();
    const maxChunkIndex = Math.max(0, Math.ceil(totalCourses / MAX_URLS_PER_SITEMAP) - 1);
    if (chunkIndex > maxChunkIndex) {
      return { notFound: true };
    }

    const courseUrls = await fetchCourseUrlsChunk(chunkIndex);
    const xml = buildUrlsetXml(courseUrls);
    res.setHeader('Content-Type', 'text/xml');
    res.write(xml);
    res.end();
    return { props: {} };
  } catch {
    if (sitemapId === 'static' || sitemapId === 'courses-1') {
      const xml = buildUrlsetXml([]);
      res.setHeader('Content-Type', 'text/xml');
      res.write(xml);
      res.end();
      return { props: {} };
    }

    return { notFound: true };
  }
}

export default function SitemapChunkXml() {
  return null;
}
