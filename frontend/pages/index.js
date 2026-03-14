import Head from 'next/head';
import { useCallback, useState } from 'react';

import CategoryList from '../components/CategoryList';
import CourseList from '../components/CourseList';
import Footer from '../components/Footer';
import Header from '../components/Header';
import ProviderList from '../components/ProviderList';
import SearchBar from '../components/SearchBar';
import { getCategories, getCourses, getProviders, searchCourses } from '../services/api';
import { buildSeo } from '../utils/seo';

export default function HomePage({ categories, providers, featuredCourses }) {
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = useCallback(async (query) => {
    if (!query) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const data = await searchCourses(query);
      setSearchResults(data.courses || []);
    } catch {
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  const seo = buildSeo({
    title: 'Course Aggregator | Discover Top Online Courses',
    description: 'Search and browse featured online courses by category and provider.'
  });

  return (
    <>
      <Head>
        <title>{seo.title}</title>
        <meta name="description" content={seo.description} />
        <meta property="og:title" content={seo.openGraph.title} />
        <meta property="og:description" content={seo.openGraph.description} />
        <meta property="og:url" content={seo.openGraph.url} />
        <meta property="og:image" content={seo.openGraph.image} />
      </Head>

      <Header />

      <main className="container-page space-y-10 py-10">
        <section className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-bold">Find your next course</h1>
          <p className="text-slate-600">Search thousands of courses from top providers.</p>
          <SearchBar onSearch={handleSearch} placeholder="Search for Python, AI, data science..." />
          {isSearching && <p className="text-sm text-slate-500">Searching...</p>}
          {!!searchResults.length && (
            <div className="space-y-3">
              <h2 className="text-xl font-semibold">Search Results</h2>
              <CourseList courses={searchResults} />
            </div>
          )}
        </section>

        <section className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Popular Categories</h2>
          <CategoryList categories={categories} />
        </section>

        <section className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Featured Courses</h2>
          <CourseList courses={featuredCourses} />
        </section>

        <section className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Browse by Provider</h2>
          <ProviderList providers={providers} />
        </section>
      </main>

      <Footer />
    </>
  );
}

export async function getServerSideProps() {
  try {
    const [categoriesData, providersData, coursesData] = await Promise.all([
      getCategories(),
      getProviders(),
      getCourses(1)
    ]);

    return {
      props: {
        categories: categoriesData.categories || [],
        providers: providersData.providers || [],
        featuredCourses: coursesData.courses || []
      }
    };
  } catch {
    return {
      props: {
        categories: [],
        providers: [],
        featuredCourses: []
      }
    };
  }
}
