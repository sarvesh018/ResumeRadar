import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Briefcase, MessageCircle, Award } from 'lucide-react'
import { analytics } from '../api/analytics'

export default function Dashboard() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: analytics.dashboard,
  })

  const { data: funnel } = useQuery({
    queryKey: ['funnel'],
    queryFn: analytics.funnel,
  })

  if (isLoading) {
    return <div className="p-8 text-gray-500">Loading dashboard...</div>
  }

  const stats = [
    { label: 'Total Applications', value: summary?.total_applications || 0, icon: Briefcase, color: 'bg-blue-50 text-blue-700' },
    { label: 'Active', value: summary?.active_applications || 0, icon: TrendingUp, color: 'bg-green-50 text-green-700' },
    { label: 'Response Rate', value: `${((summary?.response_rate || 0) * 100).toFixed(0)}%`, icon: MessageCircle, color: 'bg-purple-50 text-purple-700' },
    { label: 'Offer Rate', value: `${((summary?.offer_rate || 0) * 100).toFixed(0)}%`, icon: Award, color: 'bg-amber-50 text-amber-700' },
  ]

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="card">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${stat.color}`}>
              <stat.icon className="w-5 h-5" />
            </div>
            <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </div>
        ))}
      </div>

      {funnel && funnel.total_applications > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Application Funnel</h2>
          <div className="space-y-2">
            {funnel.stages
              .filter((s) => s.count > 0)
              .map((stage) => (
                <div key={stage.status}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="capitalize text-gray-700">{stage.status}</span>
                    <span className="text-gray-600">{stage.count} ({stage.percentage}%)</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-brand-500"
                      style={{ width: `${stage.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {summary?.most_applied_company && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div className="card">
            <div className="text-sm text-gray-600 mb-1">Most applied company</div>
            <div className="text-xl font-semibold">{summary.most_applied_company}</div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-600 mb-1">Most applied role</div>
            <div className="text-xl font-semibold">{summary.most_applied_role}</div>
          </div>
        </div>
      )}
    </div>
  )
}