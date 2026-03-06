import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ResourceInventoryTable } from '../components/tables/ResourceInventoryTable'
import type { ResourcesResponse } from '../types'

const mockData: ResourcesResponse = {
  ec2: {
    total: 2,
    by_state: { running: 1, stopped: 1 },
    instances: [
      { id: 'i-001', type: 't3.medium', state: 'running', region: 'us-east-1', name: 'web-01' },
      { id: 'i-002', type: 't2.micro', state: 'stopped', region: 'us-west-2', name: 'dev-box' },
    ],
  },
  s3: {
    total_buckets: 1,
    buckets: [{ name: 'my-bucket', region: 'us-east-1', creation_date: '2024-01-01T00:00:00Z' }],
  },
  lambda: {
    total_functions: 1,
    functions: [{ name: 'my-function', runtime: 'python3.11', region: 'us-east-1', last_modified: '2024-03-01T00:00:00Z' }],
  },
  source: 'mock',
  fetched_at: '2024-03-05T12:00:00Z',
}

describe('ResourceInventoryTable', () => {
  it('renders all three sections', () => {
    render(<ResourceInventoryTable data={mockData} isLoading={false} />)
    expect(screen.getByText(/EC2 Instances/)).toBeInTheDocument()
    expect(screen.getByText(/S3 Buckets/)).toBeInTheDocument()
    expect(screen.getByText(/Lambda Functions/)).toBeInTheDocument()
  })

  it('renders EC2 instance names', () => {
    render(<ResourceInventoryTable data={mockData} isLoading={false} />)
    expect(screen.getByText('web-01')).toBeInTheDocument()
    expect(screen.getByText('dev-box')).toBeInTheDocument()
  })

  it('renders S3 bucket name', () => {
    render(<ResourceInventoryTable data={mockData} isLoading={false} />)
    expect(screen.getByText('my-bucket')).toBeInTheDocument()
  })

  it('renders Lambda function name', () => {
    render(<ResourceInventoryTable data={mockData} isLoading={false} />)
    expect(screen.getByText('my-function')).toBeInTheDocument()
  })

  it('shows Running status for running instance', () => {
    render(<ResourceInventoryTable data={mockData} isLoading={false} />)
    expect(screen.getByText('Running')).toBeInTheDocument()
  })

  it('shows Stopped status for stopped instance', () => {
    render(<ResourceInventoryTable data={mockData} isLoading={false} />)
    expect(screen.getByText('Stopped')).toBeInTheDocument()
  })

  it('shows loading skeleton when loading', () => {
    const { container } = render(<ResourceInventoryTable data={undefined} isLoading={true} />)
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument()
  })

  it('shows empty state when no data', () => {
    render(<ResourceInventoryTable data={undefined} isLoading={false} />)
    expect(screen.getByText(/no resource data/i)).toBeInTheDocument()
  })
})
