const usdFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const dateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: '2-digit',
  timeZone: 'UTC',
})

export function formatUSD(amount: number): string {
  return usdFormatter.format(amount)
}

export function formatDate(dateStr: string): string {
  return dateFormatter.format(new Date(dateStr + 'T00:00:00Z'))
}

export function formatPct(pct: number): string {
  return `+${pct.toFixed(1)}%`
}

export function formatDatetime(isoString: string): string {
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(isoString))
}
