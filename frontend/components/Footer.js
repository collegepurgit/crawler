export default function Footer() {
  return (
    <footer className="mt-12 border-t bg-white">
      <div className="container-page py-6 text-sm text-slate-500">
        © {new Date().getFullYear()} Course Aggregator. Discover your next course.
      </div>
    </footer>
  );
}
