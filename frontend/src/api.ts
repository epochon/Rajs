/**
 * API client for profiles and watchlist (backend must be running).
 */

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface Profile {
  id: string
  name: string
  tickers: string[]
}

export interface WatchlistCheckResult {
  ticker: string
  verdict: 'BUY' | 'HOLD' | 'SELL'
  confidence_score: number
  justification: string[]
  quant_data: Record<string, unknown>
}

export interface CheckWatchlistResponse {
  profile_id: string
  profile_name: string
  results: WatchlistCheckResult[]
  good_to_invest: string[]
}

async function request<T>(
  path: string,
  options?: RequestInit & { method?: string; body?: unknown }
): Promise<T> {
  const { method = 'GET', body, ...rest } = options ?? {}
  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    method,
    headers: {
      'Content-Type': 'application/json',
      ...rest.headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
  }
  return res.json() as Promise<T>
}

export async function fetchProfiles(): Promise<Profile[]> {
  return request<Profile[]>('/api/profiles')
}

export async function createProfile(name: string): Promise<Profile> {
  return request<Profile>('/api/profiles', { method: 'POST', body: { name } })
}

export async function getProfile(profileId: string): Promise<Profile> {
  return request<Profile>(`/api/profiles/${profileId}`)
}

export async function updateProfileTickers(
  profileId: string,
  addTickers?: string[],
  removeTickers?: string[]
): Promise<Profile> {
  return request<Profile>(`/api/profiles/${profileId}`, {
    method: 'PATCH',
    body: { add_tickers: addTickers, remove_tickers: removeTickers },
  })
}

export async function deleteProfile(profileId: string): Promise<void> {
  await request(`/api/profiles/${profileId}`, { method: 'DELETE' })
}

export async function checkWatchlist(profileId: string): Promise<CheckWatchlistResponse> {
  return request<CheckWatchlistResponse>(`/api/profiles/${profileId}/check-watchlist`, {
    method: 'POST',
  })
}
