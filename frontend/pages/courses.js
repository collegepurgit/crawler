import Head from 'next/head';
import { useRouter } from 'next/router';

import CategoryList from '../components/CategoryList';
import CourseList from '../components/CourseList';
import Footer from '../components/Footer';
import Header from '../components/Header';
import Pagination from '../components/Pagination';
import ProviderList from '../components/ProviderList';
import { getCategories, getCourses, getProviders, PAGE_SIZE } from '../services/api';
import { buildSeo } from '../utils/seo';

export default function CoursesPage({ courses, categories, providers, total, limit, offset }) {
  const router = useRouter();
  const page = Number(router.query.page || 1);
  const activeCategory = router.query.category || '';
  const activeProvider = router.query.provider || '';

  const seo = buildSeo({
    title: 'Courses | Course Aggregator',
    description: 'Browse all available courses with filters and pagination.'
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
      <main className="container-page space-y-8 py-10">
        <section className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-bold">Courses</h1>
          <p className="text-slate-600">Explore online courses and narrow results with filters.</p>
          <div className="grid gap-6 lg:grid-cols-2">
            <div>
              <p className="mb-2 text-sm font-semibold">Filter by Category</p>
              <CategoryList categories={categories} />
            </div>
            <div>
              <p className="mb-2 text-sm font-semibold">Filter by Provider</p>
              <ProviderList providers={providers} />
            </div>
          </div>
          {(activeCategory || activeProvider) && (
            <p className="text-sm text-slate-500">
              Active filters: {activeCategory ? `category=${activeCategory}` : ''}{' '}
              {activeProvider ? `provider=${activeProvider}` : ''}
            </p>
          )}
        </section>

        <CourseList courses={courses} />

        <Pagination
          page={page}
          total={total}
          limit={limit || PAGE_SIZE}
          basePath="/courses"
          extraQuery={{ ...(activeCategory ? { category: activeCategory } : {}), ...(activeProvider ? { provider: activeProvider } : {}) }}
        />

        <p className="text-sm text-slate-500">Offset: {offset}</p>
      </main>
      <Footer />
    </>
  );
}

export async function getServerSideProps({ query }) {
  const page = Math.max(1, Number(query.page || 1));
  const category = query.category || undefined;
  const provider = query.provider || undefined;

  try {
    const [coursesData, categoriesData, providersData] = await Promise.all([
      getCourses(page, { category, provider }),
      getCategories(),
      getProviders()
    ]);

    return {
      props: {
        courses: coursesData.courses || [],
        total: coursesData.total || 0,
        limit: coursesData.limit || PAGE_SIZE,
        offset: coursesData.offset || 0,
        categories: categoriesData.categories || [],
        providers: providersData.providers || []
      }
    };
  } catch {
    return {
      props: {
        courses: [],
        total: 0,
        limit: PAGE_SIZE,
        offset: 0,
        categories: [],
        providers: []
      }
    };
  }
}
