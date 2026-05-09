import { useAnalytics } from '../hooks/useAnalytics';
import { BarChart3, Briefcase, CheckCircle, TrendingUp } from 'lucide-react';

export default function Dashboard() {
  const { dashboardQuery } = useAnalytics();
  const { data, isLoading, error } = dashboardQuery;

  if (isLoading) return <div className="p-8 text-center">Loading dashboard...</div>;
  if (error) return <div className="p-8 text-center text-red-500">Failed to load dashboard</div>;

  const stats = [
    { label: 'Applications', value: data?.total_applications ?? 0, icon: Briefcase },
    { label: 'Active', value: data?.active_applications ?? 0, icon: TrendingUp },
    { label: 'Response Rate', value: `${((data?.response_rate ?? 0) * 100).toFixed(0)}%`, icon: CheckCircle },
    { label: 'Interviews', value: `${((data?.interview_rate ?? 0) * 100).toFixed(0)}%`, icon: BarChart3 },
  ];

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white p-4 rounded-lg shadow">
            <stat.icon className="text-indigo-600 mb-2" size={24} />
            <p className="text-2xl font-bold">{stat.value}</p>
            <p className="text-sm text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>
      {data?.most_applied_company && (
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="font-semibold mb-2">Most Applied</h2>
          <p>Company: {data.most_applied_company}</p>
          {data.most_applied_role && <p>Role: {data.most_applied_role}</p>}
        </div>
      )}
    </div>
  );
}