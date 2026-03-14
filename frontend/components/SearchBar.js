import { useEffect, useState } from 'react';

export default function SearchBar({ onSearch, placeholder = 'Search courses...' }) {
  const [value, setValue] = useState('');

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (onSearch) onSearch(value.trim());
    }, 350);
    return () => clearTimeout(timeout);
  }, [value, onSearch]);

  return (
    <div className="w-full">
      <input
        type="text"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder={placeholder}
        className="w-full rounded-md border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none ring-blue-300 focus:ring"
      />
    </div>
  );
}
