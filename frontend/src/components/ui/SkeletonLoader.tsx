interface SkeletonLoaderProps {
  height?: string
  rows?: number
  className?: string
}

export function SkeletonLoader({ height = '200px', rows = 1, className = '' }: SkeletonLoaderProps) {
  if (rows > 1) {
    return (
      <div className={`space-y-3 ${className}`}>
        {Array.from({ length: rows }).map((_, i) => (
          <div
            key={i}
            className="animate-pulse bg-gray-200 rounded"
            style={{ height: '1.25rem', width: i % 3 === 0 ? '60%' : i % 3 === 1 ? '85%' : '75%' }}
          />
        ))}
      </div>
    )
  }

  return (
    <div
      className={`animate-pulse bg-gray-200 rounded-lg ${className}`}
      style={{ height }}
    />
  )
}
