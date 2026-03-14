import Link from 'next/link';

export default function Header() {
  return (
    <header className="border-b bg-white">
      <div className="container-page flex items-center justify-between py-4">
        <Link href="/" className="text-xl font-bold text-slate-900 no-underline">
          Course Aggregator
        </Link>
        <nav className="flex gap-4 text-sm font-medium">
          <Link href="/">Home</Link>
          <Link href="/courses">Courses</Link>
        </nav>
      </div>
    </header>
  );
}
