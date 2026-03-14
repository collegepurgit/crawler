import Link from 'next/link';

export default function CategoryList({ categories = [] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {categories.map((category) => (
        <Link
          key={category.slug}
          href={`/category/${category.slug}`}
          className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800 no-underline hover:bg-blue-200"
        >
          {category.name}
        </Link>
      ))}
    </div>
  );
}
