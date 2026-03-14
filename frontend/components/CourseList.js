import CourseCard from './CourseCard';

export default function CourseList({ courses = [] }) {
  if (!courses.length) {
    return <p className="rounded-md bg-white p-4 text-slate-600">No courses found.</p>;
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {courses.map((course) => (
        <CourseCard key={course.slug} course={course} />
      ))}
    </div>
  );
}
