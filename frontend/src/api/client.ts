const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export async function apiFetch<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(BASE_URL + path, window.location.origin)
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  }

  const response = await fetch(url.toString())
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }))
    throw new Error(error.message || `API error: ${response.status}`)
  }
  return response.json() as Promise<T>
}
