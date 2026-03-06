// ─── Cost Types ───────────────────────────────────────────────────────────────

export interface ServiceCost {
  service: string
  cost: number
  currency: string
}

export interface DailyCost {
  date: string
  services: ServiceCost[]
  total: number
}

export interface MonthlySummary {
  service: string
  total_cost: number
  currency: string
}

export interface CostsResponse {
  period: { start: string; end: string }
  daily: DailyCost[]
  monthly_summary: MonthlySummary[]
  grand_total: number
  currency: string
  source: 'live' | 'mock' | 'mock_fallback'
}

// ─── Resource Types ───────────────────────────────────────────────────────────

export type EC2State = 'running' | 'stopped' | 'terminated' | 'pending' | 'shutting-down'

export interface EC2Instance {
  id: string
  type: string
  state: EC2State
  region: string
  name: string
}

export interface S3Bucket {
  name: string
  region: string
  creation_date: string
}

export interface LambdaFunction {
  name: string
  runtime: string
  region: string
  last_modified: string
}

export interface ResourcesResponse {
  ec2: {
    total: number
    by_state: Record<string, number>
    instances: EC2Instance[]
  }
  s3: {
    total_buckets: number
    buckets: S3Bucket[]
  }
  lambda: {
    total_functions: number
    functions: LambdaFunction[]
  }
  source: 'live' | 'mock' | 'mock_fallback'
  fetched_at: string
}

// ─── Anomaly Types ────────────────────────────────────────────────────────────

export type AnomalySeverity = 'critical' | 'high' | 'medium'

export interface Anomaly {
  service: string
  date: string
  previous_cost: number
  current_cost: number
  pct_change: number
  severity: AnomalySeverity
  currency: string
}

export interface AnomaliesResponse {
  anomalies: Anomaly[]
  threshold_used: number
  period_scanned: { start: string; end: string }
  total_anomalies: number
  source: 'live' | 'mock' | 'mock_fallback'
}

// ─── Health Types ─────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: 'ok' | 'degraded'
  version: string
  uptime_seconds: number
  mock_mode: boolean
  aws: {
    connected: boolean
    region: string
    account_id: string | null
  }
  dynamodb: {
    connected: boolean
    table: string
  }
  timestamp: string
}

// ─── UI Types ─────────────────────────────────────────────────────────────────

export type DateRange = 7 | 30 | 90
