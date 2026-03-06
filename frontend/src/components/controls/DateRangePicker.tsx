import type { DateRange } from '../../types'

const OPTIONS: DateRange[] = [7, 30, 90]

interface DateRangePickerProps {
  value: DateRange
  onChange: (days: DateRange) => void
}

export function DateRangePicker({ value, onChange }: DateRangePickerProps) {
  return (
    <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1 gap-1">
      {OPTIONS.map((days) => (
        <button
          key={days}
          onClick={() => onChange(days)}
          className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
            value === days
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          {days}d
        </button>
      ))}
    </div>
  )
}
