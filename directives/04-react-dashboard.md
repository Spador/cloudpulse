# Directive 04 — React Dashboard

## Objective
Build a fully functional single-page application (SPA) using React 18, TypeScript 5, Tailwind CSS, and Recharts. The dashboard must work in mock mode without any backend connection, and in live mode when the Flask API is running.

---

## Inputs
- Flask API running at `VITE_API_BASE_URL` (default: `http://localhost:5000`)
- Mock JSON files in `frontend/src/mock/`
- Brand guidelines (see `brand-guidelines.md` if present)

---

## Tech Stack
- **Vite 5** — build tool and dev server
- **React 18** — UI framework
- **TypeScript 5** — type safety
- **Tailwind CSS 3** — utility-first styling (no component library)
- **Recharts 2** — charts
- **React Query (TanStack Query)** — data fetching, caching, and loading states

---

## Bootstrap Command
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install recharts @tanstack/react-query tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

---

## Component Specifications

### `Layout.tsx`
- Full-height layout with sidebar + main area
- Passes `mockMode` boolean via React Context

### `Header.tsx`
- App name "CloudPulse" with cloud icon
- AWS connection status badge (green "Live" / yellow "Mock")
- Links to GitHub repo

### `MockToggle.tsx`
- Toggle switch: "Mock Data" / "Live Data"
- Persists state in `localStorage` key `cloudpulse_mock_mode`
- Emits event via `useMockMode` hook

### `DateRangePicker.tsx`
- Three buttons: **7d** / **30d** / **90d**
- Active state highlighted
- Passes `days` value up via callback prop

### `DailyCostBarChart.tsx`
- **Recharts `<BarChart>`**
- X-axis: date (formatted as `MMM DD`)
- Y-axis: cost in USD (formatted as `$0.00`)
- Stacked bars per service
- Legend below chart
- Tooltip: shows date + per-service breakdown
- Loading: `<SkeletonLoader height="300px" />`
- Empty: `<EmptyState message="No cost data for this period" />`

### `CostTrendLineChart.tsx`
- **Recharts `<LineChart>`**
- Shows 7-day trend for top-5 services by total cost
- Each service is a colored line
- X-axis: date, Y-axis: daily cost USD
- Tooltip: shows all service costs for hovered date

### `ResourceInventoryTable.tsx`
- Three sections: EC2, S3, Lambda
- EC2: table with columns: Name, Instance ID, Type, State, Region
- S3: table with columns: Bucket Name, Region, Created
- Lambda: table with columns: Function Name, Runtime, Region, Last Modified
- `<StatusIndicator>` for EC2 state: green=running, yellow=stopped, gray=terminated

### `AnomalyAlertPanel.tsx`
- List of anomaly cards, ranked by severity
- Each card: service name, date, `<Badge severity={...}>`, `+{pct}%`, old cost → new cost
- Severity badge colors: red=critical, orange=high, yellow=medium
- Empty state: green checkmark, "No anomalies detected — your costs look healthy!"

### `SkeletonLoader.tsx`
- Gray animated pulse blocks
- Props: `height`, `width`, `rows` (for multi-row skeletons)

### `EmptyState.tsx`
- Props: `message`, `icon` (optional), `positive` (boolean — switches to green for "healthy" state)

### `Badge.tsx`
- Props: `severity: 'critical' | 'high' | 'medium'`
- Pill-shaped, colored by severity

### `StatusIndicator.tsx`
- Small colored dot
- Props: `status: 'running' | 'stopped' | 'terminated' | 'unknown'`

---

## Custom Hooks

### `useCosts(days: number, mock: boolean)`
- Calls `GET /api/costs?days={days}` or returns `mock/costs.json`
- Returns `{ data, isLoading, error }`

### `useResources(mock: boolean)`
- Calls `GET /api/resources` or returns `mock/resources.json`

### `useAnomalies(days: number, mock: boolean)`
- Calls `GET /api/anomalies?days={days}` or returns `mock/anomalies.json`

### `useMockMode()`
- Returns `[mockMode: boolean, setMockMode: (v: boolean) => void]`
- Persists in `localStorage`

---

## TypeScript Types (`src/types/index.ts`)

```typescript
export interface ServiceCost {
  service: string;
  cost: number;
  currency: string;
}

export interface DailyCost {
  date: string;
  services: ServiceCost[];
  total: number;
}

export interface CostsResponse {
  period: { start: string; end: string };
  daily: DailyCost[];
  monthly_summary: ServiceCost[];
  grand_total: number;
  currency: string;
  source: 'live' | 'mock';
}

export interface EC2Instance {
  id: string;
  type: string;
  state: 'running' | 'stopped' | 'terminated';
  region: string;
  name: string;
}

export interface ResourcesResponse {
  ec2: { total: number; by_state: Record<string, number>; instances: EC2Instance[] };
  s3: { total_buckets: number; buckets: { name: string; region: string; creation_date: string }[] };
  lambda: { total_functions: number; functions: { name: string; runtime: string; region: string; last_modified: string }[] };
  source: 'live' | 'mock';
  fetched_at: string;
}

export interface Anomaly {
  service: string;
  date: string;
  previous_cost: number;
  current_cost: number;
  pct_change: number;
  severity: 'critical' | 'high' | 'medium';
  currency: string;
}

export interface AnomaliesResponse {
  anomalies: Anomaly[];
  threshold_used: number;
  period_scanned: { start: string; end: string };
  total_anomalies: number;
  source: 'live' | 'mock';
}
```

---

## Environment Variables
```
VITE_API_BASE_URL=http://localhost:5000
```

---

## Test Requirements
- Jest + React Testing Library
- Test files in `src/__tests__/`
- Run: `npm test -- --watchAll=false`

### Required tests:
| Test file | Tests |
|-----------|-------|
| `DailyCostBarChart.test.tsx` | Renders chart with mock data; shows skeleton when loading; shows empty state |
| `AnomalyAlertPanel.test.tsx` | Renders anomaly cards; shows correct severity badges; shows healthy empty state |
| `ResourceInventoryTable.test.tsx` | Renders all three resource sections; StatusIndicator correct color per state |

---

## Color Palette (Recharts lines + bars)
```
EC2:          #3B82F6  (blue-500)
S3:           #10B981  (emerald-500)
Lambda:       #F59E0B  (amber-500)
RDS:          #8B5CF6  (violet-500)
CloudFront:   #EF4444  (red-500)
Other:        #6B7280  (gray-500)
```

---

## Edge Cases and Known Constraints

- **CORS**: Backend must allow `http://localhost:5173` in development. Add `VITE_API_BASE_URL` to Vite proxy config as alternative.
- **Recharts and SSR**: Recharts has no SSR issues since this is a pure SPA (no Next.js here). No special handling needed.
- **Stacked bar chart with many services**: Limit displayed services to top 10 by cost; aggregate rest as "Other".
- **Date formatting**: Use `Intl.DateTimeFormat` (no date-fns dependency to keep bundle lean). Format dates as `MMM DD`.
- **Currency formatting**: Always display as `$0.00` using `Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })`.
- **React Query cache**: Set `staleTime: 5 * 60 * 1000` (5 minutes) to avoid hammering API on tab focus.
- **Mobile responsiveness**: Dashboard must be usable on 1024px+ wide screens. Charts may scroll horizontally on smaller screens.

---

## Updates Log
_Update this section as you learn new constraints during implementation._

- (Add entries here as they're discovered)
