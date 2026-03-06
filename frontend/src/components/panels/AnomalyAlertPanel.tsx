import type { AnomaliesResponse } from '../../types'
import { SkeletonLoader } from '../ui/SkeletonLoader'
import { EmptyState } from '../ui/EmptyState'
import { Badge } from '../ui/Badge'
import { formatUSD, formatDate, formatPct } from '../../utils/formatters'

interface AnomalyAlertPanelProps {
  data: AnomaliesResponse | undefined
  isLoading: boolean
}

export function AnomalyAlertPanel({ data, isLoading }: AnomalyAlertPanelProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="h-5 bg-gray-200 rounded w-44 mb-4 animate-pulse" />
        <div className="space-y-3">
          <SkeletonLoader height="64px" />
          <SkeletonLoader height="64px" />
          <SkeletonLoader height="64px" />
        </div>
      </div>
    )
  }

  const anomalies = data?.anomalies ?? []

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-gray-900">Cost Anomalies</h2>
        {anomalies.length > 0 && (
          <span className="bg-red-100 text-red-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">
            {anomalies.length} alert{anomalies.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {anomalies.length === 0 ? (
        <EmptyState
          message="No anomalies detected — your costs look healthy!"
          positive
        />
      ) : (
        <div className="space-y-3">
          {anomalies.map((anomaly, i) => (
            <div
              key={`${anomaly.service}-${anomaly.date}-${i}`}
              className="flex items-start justify-between rounded-lg border border-gray-100 bg-gray-50 p-3 gap-4"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-semibold text-sm text-gray-900 truncate">{anomaly.service}</span>
                  <Badge severity={anomaly.severity} />
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  {formatDate(anomaly.date)} ·{' '}
                  {formatUSD(anomaly.previous_cost)} → {formatUSD(anomaly.current_cost)}
                </p>
              </div>
              <div className="text-right shrink-0">
                <span className="text-lg font-bold text-red-600">
                  {formatPct(anomaly.pct_change)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
