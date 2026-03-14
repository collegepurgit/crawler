import seoKeywordConfig from '../config/seo-keywords.json';
import { API_BASE_URL } from '../services/api';

export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';
export const MAX_URLS_PER_SITEMAP = 5000;
export const COURSE_FETCH_LIMIT = 1000;

export function escapeXml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export function buildUrlsetXml(urls) {
  const body = urls
    .map((url) => `  <url>\n    <loc>${escapeXml(url)}</loc>\n  </url>`)
    .join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</urlset>`;
}

export function buildSitemapIndexXml(sitemapUrls) {
  const body = sitemapUrls
    .map((url) => `  <sitemap>\n    <loc>${escapeXml(url)}</loc>\n  </sitemap>`)
    .join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</sitemapindex>`;
}

export async function apiRequest(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

export async function fetchCoursePage(offset = 0, limit = COURSE_FETCH_LIMIT) {
  return apiRequest(`/courses?limit=${limit}&offset=${offset}`);
}

export async function fetchCoursesTotal() {
  const firstPage = await fetchCoursePage(0, 1);
  return Number(firstPage.total || 0);
}

export async function fetchStaticUrls() {
  const urls = new Set([`${SITE_URL}/`, `${SITE_URL}/courses`]);

  try {
    const [categoriesData, providersData] = await Promise.all([
      apiRequest('/categories'),
      apiRequest('/providers')
    ]);

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
    // Keep minimum static URLs if API unavailable.
  }

  for (const entry of seoKeywordConfig.entries || []) {
    if (entry?.slug) {
      urls.add(`${SITE_URL}/${encodeURIComponent(entry.slug)}`);
    }
  }

  return Array.from(urls);
}

export async function fetchCourseUrlsChunk(chunkIndex) {
  const offset = chunkIndex * MAX_URLS_PER_SITEMAP;
  const data = await fetchCoursePage(offset, MAX_URLS_PER_SITEMAP);

  return (data.courses || [])
    .map((course) => course?.slug)
    .filter(Boolean)
    .map((slug) => `${SITE_URL}/course/${encodeURIComponent(slug)}`);
}
