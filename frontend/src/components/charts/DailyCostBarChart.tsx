import {
  BarChart,
  Bar,
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
  'Other':             '#6B7280',
}

function getColor(service: string): string {
  return SERVICE_COLORS[service] ?? SERVICE_COLORS['Other']
}

interface DailyCostBarChartProps {
  data: CostsResponse | undefined
  isLoading: boolean
}

export function DailyCostBarChart({ data, isLoading }: DailyCostBarChartProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="h-5 bg-gray-200 rounded w-40 mb-4 animate-pulse" />
        <SkeletonLoader height="300px" />
      </div>
    )
  }

  if (!data || data.daily.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-base font-semibold text-gray-900 mb-4">Daily Cost by Service</h2>
        <EmptyState message="No cost data for this period" />
      </div>
    )
  }

  // Get top 10 services by total cost
  const topServices = data.monthly_summary
    .slice(0, 10)
    .map((s) => s.service)

  // Build chart data
  const chartData = data.daily.map((day) => {
    const row: Record<string, string | number> = { date: formatDate(day.date) }
    let otherCost = 0
    for (const svc of day.services) {
      if (topServices.includes(svc.service)) {
        row[svc.service] = svc.cost
      } else {
        otherCost += svc.cost
      }
    }
    if (otherCost > 0) row['Other'] = parseFloat(otherCost.toFixed(4))
    return row
  })

  const services = [...topServices, ...(chartData.some((d) => d['Other']) ? ['Other'] : [])]

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-base font-semibold text-gray-900 mb-4">Daily Cost by Service</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 4, right: 8, left: 8, bottom: 0 }}>
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
          {services.map((svc) => (
            <Bar key={svc} dataKey={svc} stackId="a" fill={getColor(svc)} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
