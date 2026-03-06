interface MockToggleProps {
  mockMode: boolean
  onChange: (v: boolean) => void
}

export function MockToggle({ mockMode, onChange }: MockToggleProps) {
  return (
    <button
      onClick={() => onChange(!mockMode)}
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
        mockMode
          ? 'bg-amber-100 text-amber-800 hover:bg-amber-200'
          : 'bg-green-100 text-green-800 hover:bg-green-200'
      }`}
      title={mockMode ? 'Click to use live AWS data' : 'Click to use mock data'}
    >
      <span className={`inline-block h-2 w-2 rounded-full ${mockMode ? 'bg-amber-500' : 'bg-green-500'}`} />
      {mockMode ? 'Mock Data' : 'Live Data'}
    </button>
  )
}
