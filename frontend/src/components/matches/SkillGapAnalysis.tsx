import type { SkillMatch, MissingSkill } from '../../types';

interface Props {
  matched: SkillMatch[];
  missing: MissingSkill[];
}

export default function SkillGapAnalysis({ matched, missing }: Props) {
  return (
    <div>
      <h3 className="font-semibold mb-2">Skill Analysis</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h4 className="text-sm font-medium text-green-700 mb-1">Matched ({matched.length})</h4>
          <ul className="space-y-1">
            {matched.map((s, idx) => (
              <li key={idx} className="text-sm bg-green-50 px-2 py-1 rounded">{s.skill}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-medium text-red-700 mb-1">Missing ({missing.length})</h4>
          <ul className="space-y-1">
            {missing.map((s, idx) => (
              <li key={idx} className="text-sm bg-red-50 px-2 py-1 rounded">
                {s.skill} {s.category && <span className="text-xs text-gray-500">({s.category})</span>}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}