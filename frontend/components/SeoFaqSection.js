export default function SeoFaqSection({ faqs = [] }) {
  if (!faqs.length) return null;

  return (
    <section className="rounded-xl bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-semibold">Frequently Asked Questions</h2>
      <div className="mt-4 space-y-4">
        {faqs.map((faq) => (
          <article key={faq.question}>
            <h3 className="font-semibold text-slate-900">{faq.question}</h3>
            <p className="mt-1 text-slate-600">{faq.answer}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
