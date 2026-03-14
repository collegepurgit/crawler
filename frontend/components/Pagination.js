import Link from 'next/link';

export default function Pagination({ page, total, limit, basePath, extraQuery = {} }) {
  const hasPrev = page > 1;
  const hasNext = page * limit < total;

  const buildHref = (targetPage) => {
    const params = new URLSearchParams({ ...extraQuery, page: String(targetPage) });
    return `${basePath}?${params.toString()}`;
  };

  return (
    <div className="mt-8 flex items-center justify-between">
      {hasPrev ? (
        <Link href={buildHref(page - 1)} className="rounded border px-4 py-2 text-sm no-underline">
          ← Previous
        </Link>
      ) : (
        <span className="rounded border px-4 py-2 text-sm text-slate-400">← Previous</span>
      )}

      <p className="text-sm text-slate-600">
        Page {page} · Showing {Math.min(limit, Math.max(total - (page - 1) * limit, 0))} of {total}
      </p>

      {hasNext ? (
        <Link href={buildHref(page + 1)} className="rounded border px-4 py-2 text-sm no-underline">
          Next →
        </Link>
      ) : (
        <span className="rounded border px-4 py-2 text-sm text-slate-400">Next →</span>
      )}
    </div>
  );
}
