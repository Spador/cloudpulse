import { useState, useCallback } from 'react'

const STORAGE_KEY = 'cloudpulse_mock_mode'

export function useMockMode(): [boolean, (v: boolean) => void] {
  const [mockMode, setMockModeState] = useState<boolean>(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) === 'true'
    } catch {
      return false
    }
  })

  const setMockMode = useCallback((value: boolean) => {
    try {
      localStorage.setItem(STORAGE_KEY, String(value))
    } catch {
      // ignore storage errors
    }
    setMockModeState(value)
  }, [])

  return [mockMode, setMockMode]
}
