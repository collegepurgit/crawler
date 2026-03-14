import seoKeywordConfig from '../config/seo-keywords.json';
import { API_BASE_URL, PAGE_SIZE } from '../services/api';

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

function escapeXml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function buildSitemapXml(urls) {
  const body = urls
    .map(
      (url) => `  <url>\n    <loc>${escapeXml(url)}</loc>\n  </url>`
    )
    .join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</urlset>`;
}

async function apiRequest(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

async function fetchAllCourseSlugs() {
  const firstPage = await apiRequest(`/courses?limit=${PAGE_SIZE}&offset=0`);
  const total = Number(firstPage.total || 0);
  const courses = [...(firstPage.courses || [])];

  for (let offset = PAGE_SIZE; offset < total; offset += PAGE_SIZE) {
    const pageData = await apiRequest(`/courses?limit=${PAGE_SIZE}&offset=${offset}`);
    courses.push(...(pageData.courses || []));
  }

  return courses
    .map((course) => course.slug)
    .filter(Boolean);
}

export async function getServerSideProps({ res }) {
  const urls = new Set([
    `${SITE_URL}/`,
    `${SITE_URL}/courses`,
  ]);

  try {
    const [courseSlugs, categoriesData, providersData] = await Promise.all([
      fetchAllCourseSlugs(),
      apiRequest('/categories'),
      apiRequest('/providers'),
    ]);

    for (const slug of courseSlugs) {
      urls.add(`${SITE_URL}/course/${encodeURIComponent(slug)}`);
    }

    for (const category of categoriesData.categories || []) {
      if (category?.slug) {
        urls.add(`${SITE_URL}/category/${encodeURIComponent(category.slug)}`);
      }
    }

    for (const provider of providersData.providers || []) {
      if (provider?.name) {
        urls.add(`${SITE_URL}/provider/${encodeURIComponent(provider.name)}`);
      }
    }
  } catch {
    // Keep base sitemap URLs even if backend is unavailable.
  }

  for (const entry of seoKeywordConfig.entries || []) {
    if (entry?.slug) {
      urls.add(`${SITE_URL}/${encodeURIComponent(entry.slug)}`);
    }
  }

  const xml = buildSitemapXml(Array.from(urls));
  res.setHeader('Content-Type', 'text/xml');
  res.write(xml);
  res.end();

  return { props: {} };
}

export default function SitemapXml() {
  return null;
}
