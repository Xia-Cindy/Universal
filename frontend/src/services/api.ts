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

export type KnowledgeDocumentStatus = 'uploaded' | 'parsing' | 'chunking' | 'processed' | 'failed'
export type KnowledgeDocumentType = 'txt' | 'markdown' | 'pdf'

export interface KnowledgeDocumentPayload {
  fileName: string
  fileType: KnowledgeDocumentType
  subject: string
  topic: string
  content?: string
  storagePath?: string
}

export interface KnowledgeDocument {
  id: string
  userId: string
  fileName: string
  fileType: KnowledgeDocumentType
  subject: string
  topic: string
  storagePath?: string | null
  processingStatus: KnowledgeDocumentStatus
  errorMessage?: string | null
  createdAt: string
  updatedAt: string
}

export interface KnowledgeChunk {
  id: string
  userId: string
  documentId: string
  chunkIndex: number
  content: string
  metadata: Record<string, unknown>
  createdAt: string
}

export interface KnowledgeDocumentDetail {
  document: KnowledgeDocument
  chunks: KnowledgeChunk[]
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

export async function createKnowledgeDocument(payload: KnowledgeDocumentPayload) {
  const response = await fetch(`${API_BASE}/study/knowledge/documents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create Knowledge document')
  }
  return response.json()
}

export async function fetchKnowledgeOverview() {
  const response = await fetch(`${API_BASE}/study/knowledge`)
  if (!response.ok) {
    throw new Error('Unable to load Knowledge overview')
  }
  return response.json()
}

export async function fetchKnowledgeDocuments(filters: { subject?: string; topic?: string } = {}) {
  const params = new URLSearchParams()
  if (filters.subject) {
    params.set('subject', filters.subject)
  }
  if (filters.topic) {
    params.set('topic', filters.topic)
  }
  const query = params.toString()
  const response = await fetch(`${API_BASE}/study/knowledge/documents${query ? `?${query}` : ''}`)
  if (!response.ok) {
    throw new Error('Unable to load Knowledge documents')
  }
  return response.json()
}

export async function fetchKnowledgeDocument(documentId: string): Promise<KnowledgeDocumentDetail> {
  const response = await fetch(`${API_BASE}/study/knowledge/documents/${documentId}`)
  if (!response.ok) {
    throw new Error('Unable to load Knowledge document')
  }
  return response.json()
}

export async function processKnowledgeDocument(documentId: string): Promise<KnowledgeDocumentDetail> {
  const response = await fetch(`${API_BASE}/study/knowledge/documents/${documentId}/process`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Unable to process Knowledge document')
  }
  return response.json()
}

export async function updateKnowledgeDocument(
  documentId: string,
  payload: Partial<Pick<KnowledgeDocumentPayload, 'subject' | 'topic'>>,
) {
  const response = await fetch(`${API_BASE}/study/knowledge/documents/${documentId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to update Knowledge document')
  }
  return response.json()
}
