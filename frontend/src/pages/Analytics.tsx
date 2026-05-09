import { useAnalytics } from '../hooks/useAnalytics';

export default function Analytics() {
  const { funnelQuery, resumeComparisonQuery, scoreCallbackQuery, trendsQuery } = useAnalytics();
  const { data: funnel } = funnelQuery;
  const { data: resumeComp } = resumeComparisonQuery;
  const { data: scoreCallback } = scoreCallbackQuery;
  const { data: trends } = trendsQuery; // default weekly

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-bold">Analytics</h1>
      <section className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-2">Funnel</h2>
        <div className="grid grid-cols-7 gap-2 text-center">
          {funnel?.stages.map((stage) => (
            <div key={stage.status} className="bg-gray-50 p-2 rounded">
              <p className="text-xs capitalize">{stage.status}</p>
              <p className="text-lg font-bold">{stage.count}</p>
            </div>
          ))}
        </div>
        <p className="mt-2 text-sm">Response Rate: {(funnel?.overall_response_rate ?? 0 * 100).toFixed(0)}% | Interview Rate: {(funnel?.interview_rate ?? 0 * 100).toFixed(0)}%</p>
      </section>
      <ResumeComparisonComp data={resumeComp} />
      <ScoreCallbackComp data={scoreCallback} />
      <TrendsComp data={trends} />
    </div>
  );
}

// You could break these into separate component files; here they're inline for brevity.
function ResumeComparisonComp({ data }: any) {
  if (!data) return null;
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-lg font-semibold mb-2">Resume Performance</h2>
      <p className="text-sm text-gray-600 mb-2">{data.recommendation}</p>
      <ul className="space-y-1">
        {data.versions.map((v: any) => (
          <li key={v.resume_id} className="flex justify-between text-sm">
            <span>Resume {v.resume_id.slice(0,8)}...</span>
            <span>{v.response_rate.toFixed(0)}% response ({v.total_sent} apps)</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ScoreCallbackComp({ data }: any) {
  if (!data) return null;
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-lg font-semibold mb-2">Score vs Callback</h2>
      <p className="text-sm mb-2">{data.sweet_spot}</p>
      <div className="grid grid-cols-10 gap-1">
        {data.buckets.map((b: any) => (
          <div key={b.range_label} className="text-center text-xs">
            <div className="h-8 bg-indigo-100 rounded" style={{ height: `${b.response_rate*100}px` }}></div>
            <p className="truncate">{b.range_label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function TrendsComp({ data }: any) {
  if (!data) return null;
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-lg font-semibold mb-2">Weekly Trends</h2>
      <ul className="space-y-1">
        {data.data_points.map((p: any) => (
          <li key={p.period} className="flex justify-between text-sm">
            <span>{p.period}</span>
            <span>{p.applications} apps | {p.response_rate.toFixed(0)}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}