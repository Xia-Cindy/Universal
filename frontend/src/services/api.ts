export type PlanetStatus = 'active' | 'coming_later'

export interface PlanetSummary {
  name: string
  displayName: string
  status: PlanetStatus
  description: string
  primaryAction: string
  enterable: boolean
}

const API_BASE = '/api'

export async function fetchPlanets(): Promise<{ planets: PlanetSummary[] }> {
  const response = await fetch(`${API_BASE}/planets`)
  if (!response.ok) {
    throw new Error('Unable to load planets')
  }
  return response.json()
}

export async function fetchStudyHome() {
  const response = await fetch(`${API_BASE}/study/home`)
  if (!response.ok) {
    throw new Error('Unable to load Study Home')
  }
  return response.json()
}

