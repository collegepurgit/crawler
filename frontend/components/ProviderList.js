import Link from 'next/link';

export default function ProviderList({ providers = [] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {providers.map((provider) => (
        <Link
          key={provider.name}
          href={`/provider/${encodeURIComponent(provider.name)}`}
          className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-800 no-underline hover:bg-emerald-200"
        >
          {provider.name}
        </Link>
      ))}
    </div>
  );
}
