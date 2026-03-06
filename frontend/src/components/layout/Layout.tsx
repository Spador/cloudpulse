import { Header } from './Header'

interface LayoutProps {
  children: React.ReactNode
  mockMode: boolean
  onMockChange: (v: boolean) => void
  awsConnected?: boolean
}

export function Layout({ children, mockMode, onMockChange, awsConnected }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header mockMode={mockMode} onMockChange={onMockChange} awsConnected={awsConnected} />
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        {children}
      </main>
    </div>
  )
}
