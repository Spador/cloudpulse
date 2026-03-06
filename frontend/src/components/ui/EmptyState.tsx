interface EmptyStateProps {
  message: string
  positive?: boolean
}

export function EmptyState({ message, positive = false }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className={`text-4xl mb-3 ${positive ? 'text-green-500' : 'text-gray-400'}`}>
        {positive ? '✓' : '○'}
      </div>
      <p className={`text-sm font-medium ${positive ? 'text-green-600' : 'text-gray-500'}`}>
        {message}
      </p>
    </div>
  )
}
