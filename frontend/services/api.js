const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const PAGE_SIZE = 20;

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

export async function getCourses(page = 1, filters = {}) {
  const offset = (page - 1) * PAGE_SIZE;
  const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(offset) });

  if (filters.category) params.set('category', filters.category);
  if (filters.provider) params.set('provider', filters.provider);

  return request(`/courses?${params.toString()}`);
}

export async function getCourse(slug) {
  return request(`/course/${encodeURIComponent(slug)}`);
}

export async function getCategories() {
  return request('/categories');
}

export async function getProviders() {
  return request('/providers');
}

export async function searchCourses(query) {
  return request(`/search?q=${encodeURIComponent(query)}`);
}

export async function getCoursesByCategory(slug) {
  return request(`/category/${encodeURIComponent(slug)}`);
}

export async function getCoursesByProvider(name) {
  return request(`/provider/${encodeURIComponent(name)}`);
}

export { API_BASE_URL, PAGE_SIZE };
