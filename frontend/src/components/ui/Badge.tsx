import type { AnomalySeverity } from '../../types'

const SEVERITY_CLASSES: Record<AnomalySeverity, string> = {
  critical: 'bg-red-100 text-red-800 ring-1 ring-red-600/20',
  high:     'bg-orange-100 text-orange-800 ring-1 ring-orange-600/20',
  medium:   'bg-yellow-100 text-yellow-800 ring-1 ring-yellow-600/20',
}

interface BadgeProps {
  severity: AnomalySeverity
}

export function Badge({ severity }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${SEVERITY_CLASSES[severity]}`}>
      {severity}
    </span>
  )
}
