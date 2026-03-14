import Link from 'next/link';

export default function CourseCard({ course }) {
  return (
    <article className="overflow-hidden rounded-lg border bg-white shadow-sm">
      <img
        src={course.image_url || 'https://placehold.co/640x360?text=Course'}
        alt={course.title}
        className="h-44 w-full object-cover"
      />
      <div className="space-y-3 p-4">
        <div>
          <h3 className="line-clamp-2 text-lg font-semibold text-slate-900">{course.title}</h3>
          <p className="text-sm text-slate-600">{course.provider || course.provider_name}</p>
        </div>
        <p className="text-sm font-medium text-amber-600">⭐ {course.rating ?? 'N/A'}</p>
        <Link
          href={`/course/${course.slug}`}
          className="inline-block rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white no-underline hover:bg-blue-700"
        >
          View Course
        </Link>
      </div>
    </article>
  );
}
