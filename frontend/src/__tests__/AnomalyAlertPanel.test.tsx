import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { AnomalyAlertPanel } from '../components/panels/AnomalyAlertPanel'
import type { AnomaliesResponse } from '../types'

const mockData: AnomaliesResponse = {
  anomalies: [
    { service: 'Amazon EC2', date: '2024-03-04', previous_cost: 10, current_cost: 23, pct_change: 130, severity: 'critical', currency: 'USD' },
    { service: 'Amazon RDS', date: '2024-03-03', previous_cost: 8, current_cost: 13.2, pct_change: 65, severity: 'high', currency: 'USD' },
    { service: 'Amazon S3', date: '2024-03-02', previous_cost: 1, current_cost: 1.3, pct_change: 30, severity: 'medium', currency: 'USD' },
  ],
  threshold_used: 0.20,
  period_scanned: { start: '2024-02-27', end: '2024-03-05' },
  total_anomalies: 3,
  source: 'mock',
}

const emptyData: AnomaliesResponse = {
  anomalies: [],
  threshold_used: 0.20,
  period_scanned: { start: '2024-02-27', end: '2024-03-05' },
  total_anomalies: 0,
  source: 'mock',
}

describe('AnomalyAlertPanel', () => {
  it('renders anomaly cards', () => {
    render(<AnomalyAlertPanel data={mockData} isLoading={false} />)
    expect(screen.getByText('Amazon EC2')).toBeInTheDocument()
    expect(screen.getByText('Amazon RDS')).toBeInTheDocument()
    expect(screen.getByText('Amazon S3')).toBeInTheDocument()
  })

  it('shows correct severity badges', () => {
    render(<AnomalyAlertPanel data={mockData} isLoading={false} />)
    expect(screen.getByText('critical')).toBeInTheDocument()
    expect(screen.getByText('high')).toBeInTheDocument()
    expect(screen.getByText('medium')).toBeInTheDocument()
  })

  it('shows healthy empty state when no anomalies', () => {
    render(<AnomalyAlertPanel data={emptyData} isLoading={false} />)
    expect(screen.getByText(/no anomalies detected/i)).toBeInTheDocument()
  })

  it('shows loading skeleton when loading', () => {
    const { container } = render(<AnomalyAlertPanel data={undefined} isLoading={true} />)
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
  })

  it('shows alert count badge when anomalies present', () => {
    render(<AnomalyAlertPanel data={mockData} isLoading={false} />)
    expect(screen.getByText('3 alerts')).toBeInTheDocument()
  })

  it('shows pct_change values', () => {
    render(<AnomalyAlertPanel data={mockData} isLoading={false} />)
    expect(screen.getByText('+130.0%')).toBeInTheDocument()
  })
})
