import type { Suggestion } from '../../types';

export default function Suggestions({ suggestions }: { suggestions: Suggestion[] }) {
  if (!suggestions?.length) return null;
  return (
    <div>
      <h3 className="font-semibold mb-2">Suggestions</h3>
      <ul className="space-y-2">
        {suggestions.map((s, idx) => (
          <li key={idx} className="p-2 bg-blue-50 rounded text-sm">
            <strong>{s.section} ({s.action}):</strong> {s.text}
          </li>
        ))}
      </ul>
    </div>
  );
}