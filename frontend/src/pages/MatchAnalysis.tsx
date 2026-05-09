import { useState } from 'react';
import { useResumes } from '../hooks/useResumes';
import { useMatch } from '../hooks/useMatch';
import Button from '../components/shared/Button';
import MatchScoreCard from '../components/matches/MatchScoreCard';
import SkillGapAnalysis from '../components/matches/SkillGapAnalysis';
import Suggestions from '../components/matches/Suggestions';
import toast from 'react-hot-toast';

export default function MatchAnalysis() {
  const { resumesQuery } = useResumes();
  const { runMatchMutation } = useMatch();
  const [selectedResume, setSelectedResume] = useState('');
  const [jdText, setJdText] = useState('');
  const [jdCompany, setJdCompany] = useState('');
  const [jdRole, setJdRole] = useState('');
  const [result, setResult] = useState<any>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedResume || !jdText.trim()) return toast.error('Select a resume and enter JD text');
    runMatchMutation.mutate(
      { resume_id: selectedResume, jd_text: jdText, jd_company: jdCompany, jd_role: jdRole },
      {
        onSuccess: (data) => setResult(data),
      }
    );
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Match Analysis</h1>
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-4 mb-8">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Select Resume</label>
          <select
            value={selectedResume}
            onChange={(e) => setSelectedResume(e.target.value)}
            className="w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">-- Choose a resume --</option>
            {resumesQuery.data?.map((r) => (
              <option key={r.id} value={r.id}>{r.version_name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Job Description</label>
          <textarea
            rows={8}
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            className="w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Paste the full job description here..."
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <input
            type="text"
            placeholder="Company (optional)"
            value={jdCompany}
            onChange={(e) => setJdCompany(e.target.value)}
            className="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500"
          />
          <input
            type="text"
            placeholder="Role (optional)"
            value={jdRole}
            onChange={(e) => setJdRole(e.target.value)}
            className="border-gray-300 rounded-md shadow-sm focus:ring-indigo-500"
          />
        </div>
        <Button type="submit" isLoading={runMatchMutation.isPending}>Run Match</Button>
      </form>

      {result && (
        <div className="bg-white p-6 rounded-lg shadow space-y-6">
          <MatchScoreCard score={result.overall_score} label={`${result.jd_role || 'Role'} @ ${result.jd_company || 'Company'}`} />
          <div className="grid grid-cols-3 gap-4 text-center">
            <div><p className="font-medium">Keyword</p><p>{result.keyword_score.toFixed(2)}</p></div>
            <div><p className="font-medium">Semantic</p><p>{result.semantic_score.toFixed(2)}</p></div>
            <div><p className="font-medium">Taxonomy</p><p>{result.taxonomy_score.toFixed(2)}</p></div>
          </div>
          <SkillGapAnalysis matched={result.matched_skills} missing={result.missing_skills} />
          <Suggestions suggestions={result.suggestions} />
        </div>
      )}
    </div>
  );
}