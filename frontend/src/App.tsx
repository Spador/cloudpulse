import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Layout } from './components/layout/Layout'
import { DailyCostBarChart } from './components/charts/DailyCostBarChart'
import { CostTrendLineChart } from './components/charts/CostTrendLineChart'
import { ResourceInventoryTable } from './components/tables/ResourceInventoryTable'
import { AnomalyAlertPanel } from './components/panels/AnomalyAlertPanel'
import { DateRangePicker } from './components/controls/DateRangePicker'
import { useCosts } from './hooks/useCosts'
import { useResources } from './hooks/useResources'
import { useAnomalies } from './hooks/useAnomalies'
import { useMockMode } from './hooks/useMockMode'
import { apiFetch } from './api/client'
import type { DateRange, HealthResponse } from './types'
import { formatUSD } from './utils/formatters'

function App() {
  const [mockMode, setMockMode] = useMockMode()
  const [dateRange, setDateRange] = useState<DateRange>(30)

  const { data: costsData, isLoading: costsLoading } = useCosts(dateRange, mockMode)
  const { data: resourcesData, isLoading: resourcesLoading } = useResources(mockMode)
  const { data: anomaliesData, isLoading: anomaliesLoading } = useAnomalies(Math.min(dateRange, 30), mockMode)

  const { data: healthData } = useQuery<HealthResponse>({
    queryKey: ['health'],
    queryFn: () => apiFetch<HealthResponse>('/api/health'),
    staleTime: 30 * 1000,
    retry: false,
  })

  return (
    <Layout
      mockMode={mockMode}
      onMockChange={setMockMode}
      awsConnected={healthData?.aws?.connected}
    >
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {mockMode ? 'Viewing mock data' : 'Live AWS cost data'}
            {costsData ? ` · Total: ${formatUSD(costsData.grand_total)}` : ''}
          </p>
        </div>
        <DateRangePicker value={dateRange} onChange={setDateRange} />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
        <DailyCostBarChart data={costsData} isLoading={costsLoading} />
        <CostTrendLineChart data={costsData} isLoading={costsLoading} />
      </div>

      {/* Anomalies + Resources row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-1">
          <AnomalyAlertPanel data={anomaliesData} isLoading={anomaliesLoading} />
        </div>
        <div className="xl:col-span-2">
          <ResourceInventoryTable data={resourcesData} isLoading={resourcesLoading} />
        </div>
      </div>
    </Layout>
  )
}

export default App
