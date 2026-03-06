import type { EC2State } from '../../types'

const STATE_CLASSES: Record<string, string> = {
  running:       'bg-green-500',
  stopped:       'bg-yellow-400',
  terminated:    'bg-gray-400',
  pending:       'bg-blue-400',
  'shutting-down': 'bg-orange-400',
}

const STATE_LABELS: Record<string, string> = {
  running:       'Running',
  stopped:       'Stopped',
  terminated:    'Terminated',
  pending:       'Pending',
  'shutting-down': 'Shutting down',
}

interface StatusIndicatorProps {
  status: EC2State | string
}

export function StatusIndicator({ status }: StatusIndicatorProps) {
  const colorClass = STATE_CLASSES[status] ?? 'bg-gray-300'
  const label = STATE_LABELS[status] ?? status

  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`inline-block h-2 w-2 rounded-full ${colorClass}`} />
      <span className="text-sm text-gray-700">{label}</span>
    </span>
  )
}
