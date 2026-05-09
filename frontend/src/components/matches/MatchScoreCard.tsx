interface Props {
  score: number;
  label?: string;
}

export default function MatchScoreCard({ score, label = 'Overall Match' }: Props) {
  const percent = Math.round(score * 100);
  const color = percent >= 70 ? 'text-green-600' : percent >= 50 ? 'text-yellow-600' : 'text-red-600';
  return (
    <div className="text-center">
      <div className={`text-4xl font-bold ${color}`}>{percent}%</div>
      <div className="text-sm text-gray-500">{label}</div>
    </div>
  );
}