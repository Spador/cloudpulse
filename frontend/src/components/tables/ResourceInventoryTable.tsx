import type { ResourcesResponse } from '../../types'
import { SkeletonLoader } from '../ui/SkeletonLoader'
import { EmptyState } from '../ui/EmptyState'
import { StatusIndicator } from '../ui/StatusIndicator'

interface ResourceInventoryTableProps {
  data: ResourcesResponse | undefined
  isLoading: boolean
}

export function ResourceInventoryTable({ data, isLoading }: ResourceInventoryTableProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="h-5 bg-gray-200 rounded w-48 mb-4 animate-pulse" />
        <SkeletonLoader rows={6} />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-base font-semibold text-gray-900 mb-4">Resource Inventory</h2>
        <EmptyState message="No resource data available" />
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-8">
      <h2 className="text-base font-semibold text-gray-900">Resource Inventory</h2>

      {/* EC2 Section */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-700">
            EC2 Instances
            <span className="ml-2 text-gray-400 font-normal">({data.ec2.total} total)</span>
          </h3>
          <div className="flex gap-3 text-xs text-gray-500">
            {Object.entries(data.ec2.by_state).map(([state, count]) => (
              <span key={state}>{state}: {count}</span>
            ))}
          </div>
        </div>
        {data.ec2.instances.length === 0 ? (
          <EmptyState message="No EC2 instances found" />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Name</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Instance ID</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Type</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">State</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Region</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.ec2.instances.map((inst) => (
                  <tr key={inst.id} className="hover:bg-gray-50">
                    <td className="py-2.5 px-3 font-medium text-gray-900">{inst.name}</td>
                    <td className="py-2.5 px-3 font-mono text-gray-500 text-xs">{inst.id}</td>
                    <td className="py-2.5 px-3 text-gray-600">{inst.type}</td>
                    <td className="py-2.5 px-3"><StatusIndicator status={inst.state} /></td>
                    <td className="py-2.5 px-3 text-gray-500">{inst.region}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* S3 Section */}
      <section>
        <h3 className="text-sm font-semibold text-gray-700 mb-3">
          S3 Buckets
          <span className="ml-2 text-gray-400 font-normal">({data.s3.total_buckets} total)</span>
        </h3>
        {data.s3.buckets.length === 0 ? (
          <EmptyState message="No S3 buckets found" />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Bucket Name</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Region</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.s3.buckets.map((bucket) => (
                  <tr key={bucket.name} className="hover:bg-gray-50">
                    <td className="py-2.5 px-3 font-medium text-gray-900">{bucket.name}</td>
                    <td className="py-2.5 px-3 text-gray-500">{bucket.region}</td>
                    <td className="py-2.5 px-3 text-gray-500">{new Date(bucket.creation_date).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Lambda Section */}
      <section>
        <h3 className="text-sm font-semibold text-gray-700 mb-3">
          Lambda Functions
          <span className="ml-2 text-gray-400 font-normal">({data.lambda.total_functions} total)</span>
        </h3>
        {data.lambda.functions.length === 0 ? (
          <EmptyState message="No Lambda functions found" />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Function Name</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Runtime</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Region</th>
                  <th className="text-left py-2 px-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Last Modified</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.lambda.functions.map((fn) => (
                  <tr key={fn.name} className="hover:bg-gray-50">
                    <td className="py-2.5 px-3 font-medium text-gray-900">{fn.name}</td>
                    <td className="py-2.5 px-3 font-mono text-gray-500 text-xs">{fn.runtime}</td>
                    <td className="py-2.5 px-3 text-gray-500">{fn.region}</td>
                    <td className="py-2.5 px-3 text-gray-500">{new Date(fn.last_modified).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
