import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { CostsResponse } from '../../types'
import { SkeletonLoader } from '../ui/SkeletonLoader'
import { EmptyState } from '../ui/EmptyState'
import { formatDate, formatUSD } from '../../utils/formatters'

const SERVICE_COLORS: Record<string, string> = {
  'Amazon EC2':        '#3B82F6',
  'Amazon S3':         '#10B981',
  'AWS Lambda':        '#F59E0B',
  'Amazon RDS':        '#8B5CF6',
  'Amazon CloudFront': '#EF4444',
}

interface CostTrendLineChartProps {
  data: CostsResponse | undefined
  isLoading: boolean
}

export function CostTrendLineChart({ data, isLoading }: CostTrendLineChartProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="h-5 bg-gray-200 rounded w-40 mb-4 animate-pulse" />
        <SkeletonLoader height="260px" />
      </div>
    )
  }

  if (!data || data.daily.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-base font-semibold text-gray-900 mb-4">7-Day Cost Trend</h2>
        <EmptyState message="No trend data available" />
      </div>
    )
  }

  // Top 5 services by monthly total
  const top5 = data.monthly_summary.slice(0, 5).map((s) => s.service)

  // Last 7 days of data
  const last7 = data.daily.slice(-7)

  const chartData = last7.map((day) => {
    const row: Record<string, string | number> = { date: formatDate(day.date) }
    for (const svc of day.services) {
      if (top5.includes(svc.service)) {
        row[svc.service] = svc.cost
      }
    }
    return row
  })

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-base font-semibold text-gray-900 mb-4">7-Day Cost Trend (Top Services)</h2>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={chartData} margin={{ top: 4, right: 8, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis
            tickFormatter={(v) => `$${v}`}
            tick={{ fontSize: 11 }}
            width={55}
          />
          <Tooltip
            formatter={(value: number) => formatUSD(value)}
            labelStyle={{ fontWeight: 600 }}
          />
          <Legend wrapperStyle={{ fontSize: 12, paddingTop: 12 }} />
          {top5.map((svc) => (
            <Line
              key={svc}
              type="monotone"
              dataKey={svc}
              stroke={SERVICE_COLORS[svc] ?? '#6B7280'}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
