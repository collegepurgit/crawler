export function buildSeo({
  title,
  description,
  url = 'http://localhost:3000',
  image = 'https://images.unsplash.com/photo-1513258496099-48168024aec0?auto=format&fit=crop&w=1200&q=80'
}) {
  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url,
      image
    }
  };
}
