import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { DailyCostBarChart } from '../components/charts/DailyCostBarChart'
import type { CostsResponse } from '../types'

// Recharts uses ResizeObserver — mock it for Jest/jsdom
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

const mockData: CostsResponse = {
  period: { start: '2024-02-27', end: '2024-03-05' },
  daily: [
    {
      date: '2024-03-04',
      services: [
        { service: 'Amazon EC2', cost: 12.34, currency: 'USD' },
        { service: 'Amazon S3', cost: 1.02, currency: 'USD' },
      ],
      total: 13.36,
    },
  ],
  monthly_summary: [
    { service: 'Amazon EC2', total_cost: 320.45, currency: 'USD' },
    { service: 'Amazon S3', total_cost: 28.10, currency: 'USD' },
  ],
  grand_total: 348.55,
  currency: 'USD',
  source: 'mock',
}

describe('DailyCostBarChart', () => {
  it('renders chart title', () => {
    render(<DailyCostBarChart data={mockData} isLoading={false} />)
    expect(screen.getByText('Daily Cost by Service')).toBeInTheDocument()
  })

  it('shows loading skeleton when loading', () => {
    const { container } = render(<DailyCostBarChart data={undefined} isLoading={true} />)
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
  })

  it('shows empty state when no daily data', () => {
    const emptyData: CostsResponse = { ...mockData, daily: [] }
    render(<DailyCostBarChart data={emptyData} isLoading={false} />)
    expect(screen.getByText(/no cost data/i)).toBeInTheDocument()
  })

  it('shows empty state when data is undefined', () => {
    render(<DailyCostBarChart data={undefined} isLoading={false} />)
    expect(screen.getByText(/no cost data/i)).toBeInTheDocument()
  })
})
