import Link from 'next/link';

export default function InternalCourseLinks({ courses = [], title = 'Explore related courses' }) {
  if (!courses.length) return null;

  return (
    <section className="rounded-xl bg-white p-5 shadow-sm">
      <h2 className="text-xl font-semibold">{title}</h2>
      <ul className="mt-3 list-inside list-disc space-y-1">
        {courses.map((course) => (
          <li key={course.slug}>
            <Link href={`/course/${course.slug}`}>{course.title}</Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
