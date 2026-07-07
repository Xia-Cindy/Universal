export type PlanetStatus = 'active' | 'coming_later'

export interface PlanetSummary {
  name: string
  displayName: string
  status: PlanetStatus
  description: string
  primaryAction: string
  enterable: boolean
}

export interface StudyGoalPayload {
  goalName: string
  examName: string
  deadline: string
  subjects: string[]
  currentLevel: string
  dailyAvailableMinutes: number
  priority: string
}

export interface DailyTask {
  id: string
  subject: string
  topic: string
  taskDate: string
  estimatedMinutes: number
  status: string
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

export async function createGoal(payload: StudyGoalPayload) {
  const response = await fetch(`${API_BASE}/study/goals`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create goal')
  }
  return response.json()
}

export async function createPlan(payload: Record<string, unknown> = {}) {
  const response = await fetch(`${API_BASE}/study/plans`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create plan')
  }
  return response.json()
}

export async function fetchCurrentPlan() {
  const response = await fetch(`${API_BASE}/study/plans/current`)
  if (!response.ok) {
    throw new Error('Unable to load current plan')
  }
  return response.json()
}

export async function updateTask(taskId: string, payload: Partial<DailyTask>) {
  const response = await fetch(`${API_BASE}/study/tasks/${taskId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to update task')
  }
  return response.json()
}

export async function completeTask(taskId: string) {
  const response = await fetch(`${API_BASE}/study/tasks/${taskId}/complete`, {
    method: 'PATCH',
  })
  if (!response.ok) {
    throw new Error('Unable to complete task')
  }
  return response.json()
}

export async function startSession(payload: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/study/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to start session')
  }
  return response.json()
}

export async function finishSession(sessionId: string, payload: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/study/sessions/${sessionId}/finish`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to finish session')
  }
  return response.json()
}

export async function askStudyTutor(question: string) {
  const response = await fetch(`${API_BASE}/study/tutor/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  if (!response.ok) {
    throw new Error('Unable to ask Tutor')
  }
  return response.json()
}

export async function fetchTutorHistory() {
  const response = await fetch(`${API_BASE}/study/tutor/history`)
  if (!response.ok) {
    throw new Error('Unable to load Tutor history')
  }
  return response.json()
}
