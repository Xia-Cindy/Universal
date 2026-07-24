export type PlanetStatus = 'active' | 'coming_later'

export interface PlanetSummary {
  name: string
  displayName: string
  status: PlanetStatus
  description: string
  primaryAction: string
  enterable: boolean
}

export type StudyGoalType = 'exam' | 'learning' | 'reading' | 'growth'

export interface StudyGoalPayload {
  goalType: StudyGoalType
  goalName: string
  examName?: string | null
  targetDirection?: string
  deadline?: string | null
  description?: string
  subjects: string[]
  currentLevel: string
  dailyAvailableMinutes: number
  priority: string
}

export interface DailyTask {
  id: string
  goalId?: string
  weekPlanId?: string
  subject: string
  topic: string
  taskDate: string
  estimatedMinutes: number
  priority: 'high' | 'medium' | 'low'
  status: string
}

export interface StudyGoal {
  id: string
  userId: string
  goalType: StudyGoalType
  goalName: string
  examName?: string | null
  deadline?: string | null
  description?: string
  subjects: string[]
  currentLevel: string
  dailyAvailableMinutes: number
  priority: string
  status: string
  remainingDays?: number | null
  progress?: {
    totalTasks: number
    completedTasks: number
    taskCompletionRate: number
  }
}

export type KnowledgeDocumentStatus = 'uploaded' | 'parsing' | 'chunking' | 'processed' | 'failed'
export type KnowledgeDocumentType = 'txt' | 'markdown' | 'pdf'

export interface KnowledgeDocumentPayload {
  fileName: string
  fileType: KnowledgeDocumentType
  goalId?: string | null
  planetType?: string
  techStackId?: string | null
  tags?: string[]
  subject: string
  topic: string
  content?: string
  contentEncoding?: 'text' | 'base64'
  storagePath?: string
  notes?: string
}

export interface KnowledgeDocument {
  id: string
  userId: string
  goalId?: string | null
  fileName: string
  fileType: KnowledgeDocumentType
  subject: string
  topic: string
  planetType: string
  techStackId?: string | null
  tags: string[]
  storagePath?: string | null
  contentEncoding: string
  provider: string
  providerDatasetId?: string | null
  providerDocumentId?: string | null
  providerStatus?: string | null
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

export interface EvidenceSource {
  sourceId: string
  documentId: string
  chunkId: string
  title: string
  quote: string
  score: number
  metadata: Record<string, unknown>
  sourceUrl?: string | null
}

export interface ReviewQueueItem {
  review: {
    id: string
    wrongQuestionId: string
    stage: number
    intervalDays: number
    dueDate: string
    status: string
    result?: string | null
  }
  wrongQuestion: {
    id: string
    goalId: string
    question: string
    correctAnswer: string
    explanation: string
    subject: string
    topic: string
    status: string
  }
}

export interface StudyAnalyticsPayload {
  progressSummary: Record<string, any>
  learningInsights: string[]
  weakAreas: Array<Record<string, any>>
  recommendedActions: string[]
  report: Record<string, any>
  dataQuality: Record<string, any>
  learningSummary?: Record<string, any>
}

export interface StudyOnboardingState {
  state: 'needs_onboarding' | 'ready'
  activeGoal: Record<string, any> | null
}

export interface StudyWorkspacePayload {
  state: 'needs_goal' | 'ready'
  currentGoal: StudyGoal | null
  goals: StudyGoal[]
  plans: {
    longTermPlans: Array<Record<string, any>>
    monthlyPlans: Array<Record<string, any>>
    weeklyPlans: Array<Record<string, any>>
    dailyTasks: DailyTask[]
  }
  planSummary: {
    hasPlan: boolean
    longTermPlanCount: number
    monthlyPlanCount: number
    weeklyPlanCount: number
    dailyTaskCount: number
    completedTaskCount: number
    taskCompletionRate: number
  }
  todayTasks: DailyTask[]
  primaryAction: {
    type: string
    label: string
    route: string
    description: string
    taskId?: string
  }
  knowledgeSummary: {
    documents: KnowledgeDocument[]
    statusCounts: Record<string, number>
    subjects: Array<Record<string, any>>
    documentCount: number
    goalLinkedCount: number
    independentCount: number
  }
  analyticsSummary: StudyAnalyticsPayload
}

export interface TechStack {
  id: string
  userId: string
  name: string
  category: string
  proficiency: string
  description: string
  tags: string[]
  status: string
}

export interface WorkProject {
  id: string
  userId: string
  title: string
  description: string
  techStackIds: string[]
  evidenceRefs: string[]
  status: string
}

export interface WorkArticle {
  id: string
  userId: string
  techStackId: string
  title: string
  articleType: 'knowledge' | 'note'
  summary: string
  content: string
  tags: string[]
  status: string
  createdAt: string
  updatedAt: string
}

export interface WorkLearningRecord {
  id: string
  userId: string
  techStackId: string
  title: string
  notes: string
  minutes: number
  tags: string[]
  status: string
  createdAt: string
  updatedAt: string
}

export interface ResumeVersion {
  id: string
  userId: string
  roleTarget: string
  title: string
  content: string
  evidenceRefs: string[]
  status: string
}

export interface WorkHomePayload {
  state: string
  primaryAction: {
    type: string
    label: string
    route: string
    description: string
  }
  summary: {
    techStackCount: number
    projectCount: number
    articleCount: number
    learningRecordCount: number
    resumeCount: number
    knowledgeDocumentCount: number
  }
  techStacks: TechStack[]
  projects: WorkProject[]
  articles: WorkArticle[]
  learningRecords: WorkLearningRecord[]
  resumes: ResumeVersion[]
}

export interface CommunityArticle {
  title: string
  url: string
  source: string
  heat: string
  summary: string
  content: string
}

export interface CommunityArticlePayload {
  source: string
  topic: string
  url: string
  articles: CommunityArticle[]
  error: string
}

export interface CommunityArticleDetail {
  title: string
  url: string
  content: string
  error: string
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

export async function fetchWorkHome(): Promise<WorkHomePayload> {
  const response = await fetch(`${API_BASE}/work/home`)
  if (!response.ok) {
    throw new Error('Unable to load Work Home')
  }
  return response.json()
}

export async function fetchTechStacks(): Promise<TechStack[]> {
  const response = await fetch(`${API_BASE}/work/tech-stacks`)
  if (!response.ok) {
    throw new Error('Unable to load Tech Stacks')
  }
  return response.json()
}

export async function createTechStack(payload: Record<string, unknown>): Promise<TechStack> {
  const response = await fetch(`${API_BASE}/work/tech-stacks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create Tech Stack')
  }
  return response.json()
}

export async function updateTechStack(techStackId: string, payload: Record<string, unknown>): Promise<TechStack> {
  const response = await fetch(`${API_BASE}/work/tech-stacks/${techStackId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to update Tech Stack')
  }
  return response.json()
}

export async function deleteTechStack(techStackId: string): Promise<TechStack> {
  const response = await fetch(`${API_BASE}/work/tech-stacks/${techStackId}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Unable to delete Tech Stack')
  }
  return response.json()
}

export async function fetchTechStackDetail(techStackId: string) {
  const response = await fetch(`${API_BASE}/work/tech-stacks/${techStackId}`)
  if (!response.ok) {
    throw new Error('Unable to load Tech Stack')
  }
  return response.json()
}

export async function fetchCSDNCommunityArticles(topic = 'java'): Promise<CommunityArticlePayload> {
  const params = new URLSearchParams({ topic })
  const response = await fetch(`${API_BASE}/work/community/csdn?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Unable to load CSDN community articles')
  }
  return response.json()
}

export async function fetchCSDNCommunityArticleDetail(url: string): Promise<CommunityArticleDetail> {
  const params = new URLSearchParams({ url })
  const response = await fetch(`${API_BASE}/work/community/csdn/article?${params.toString()}`)
  if (!response.ok) {
    throw new Error('Unable to load CSDN article content')
  }
  return response.json()
}

export async function createWorkArticle(techStackId: string, payload: Record<string, unknown>): Promise<WorkArticle> {
  const response = await fetch(`${API_BASE}/work/tech-stacks/${techStackId}/articles`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create Work Article')
  }
  return response.json()
}

export async function createWorkLearningRecord(
  techStackId: string,
  payload: Record<string, unknown>,
): Promise<WorkLearningRecord> {
  const response = await fetch(`${API_BASE}/work/tech-stacks/${techStackId}/learning-records`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create Work Learning Record')
  }
  return response.json()
}

export async function fetchWorkProjects(): Promise<WorkProject[]> {
  const response = await fetch(`${API_BASE}/work/projects`)
  if (!response.ok) {
    throw new Error('Unable to load Work Projects')
  }
  return response.json()
}

export async function createWorkProject(payload: Record<string, unknown>): Promise<WorkProject> {
  const response = await fetch(`${API_BASE}/work/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create Work Project')
  }
  return response.json()
}

export async function fetchResumeVersions(): Promise<ResumeVersion[]> {
  const response = await fetch(`${API_BASE}/work/resumes`)
  if (!response.ok) {
    throw new Error('Unable to load Resume Versions')
  }
  return response.json()
}

export async function createResumeDraft(payload: Record<string, unknown>): Promise<ResumeVersion> {
  const response = await fetch(`${API_BASE}/work/resumes/draft`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create Resume Draft')
  }
  return response.json()
}

export async function fetchStudyWorkspace(): Promise<StudyWorkspacePayload> {
  const response = await fetch(`${API_BASE}/study/workspace`)
  if (!response.ok) {
    throw new Error('Unable to load Study Workspace')
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

export async function updateGoal(goalId: string, payload: Partial<StudyGoalPayload>) {
  const response = await fetch(`${API_BASE}/study/goals/${goalId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to update goal')
  }
  return response.json()
}

export async function fetchStudyGoals(): Promise<StudyGoal[]> {
  const response = await fetch(`${API_BASE}/study/goals`)
  if (!response.ok) {
    throw new Error('Unable to load goals')
  }
  return response.json()
}

export async function switchStudyGoal(goalId: string) {
  const response = await fetch(`${API_BASE}/study/goals/${goalId}/switch`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Unable to switch goal')
  }
  return response.json()
}

export async function fetchStudyOnboarding(): Promise<StudyOnboardingState> {
  const response = await fetch(`${API_BASE}/study/onboarding`)
  if (!response.ok) {
    throw new Error('Unable to load Study onboarding')
  }
  return response.json()
}

export async function createOnboardingGoal(payload: StudyGoalPayload): Promise<StudyOnboardingState> {
  const response = await fetch(`${API_BASE}/study/onboarding/goal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create Study onboarding goal')
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

export async function updateYearPlan(planId: string, payload: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/study/plans/year/${planId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to update long term plan')
  }
  return response.json()
}

export async function updateMonthPlan(planId: string, payload: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/study/plans/month/${planId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to update monthly plan')
  }
  return response.json()
}

export async function updateWeekPlan(planId: string, payload: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/study/plans/week/${planId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to update weekly plan')
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

export async function startExecutionSession(payload: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/study/execution/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to start Study session')
  }
  return response.json()
}

export async function finishExecutionSession(sessionId: string, payload: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/study/execution/sessions/${sessionId}/finish`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to finish Study session')
  }
  return response.json()
}

export async function askStudyTutor(question: string, scope = 'current_goal') {
  const response = await fetch(`${API_BASE}/study/tutor/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, scope }),
  })
  if (!response.ok) {
    throw new Error('Unable to ask Tutor')
  }
  return response.json()
}

export async function saveTutorAnswerEvent(payload: {
  question: string
  answer: string
  sources: EvidenceSource[]
}) {
  const response = await fetch(`${API_BASE}/study/tutor/events`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to save Tutor answer as a Learning Event')
  }
  return response.json()
}

export async function fetchKnowledgeEvidence(documentId: string): Promise<EvidenceSource[]> {
  const response = await fetch(`${API_BASE}/study/knowledge/documents/${documentId}/evidence`)
  if (!response.ok) {
    throw new Error('Unable to load Knowledge evidence')
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

export async function createWorkKnowledgeDocument(payload: KnowledgeDocumentPayload) {
  const response = await fetch(`${API_BASE}/work/knowledge/documents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create Work Knowledge document')
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

export async function fetchKnowledgeDocuments(
  filters: { subject?: string; topic?: string; goalId?: string; planetType?: string; techStackId?: string } = {},
): Promise<KnowledgeDocument[]> {
  const params = new URLSearchParams()
  if (filters.subject) {
    params.set('subject', filters.subject)
  }
  if (filters.topic) {
    params.set('topic', filters.topic)
  }
  if (filters.goalId) {
    params.set('goalId', filters.goalId)
  }
  if (filters.planetType) {
    params.set('planetType', filters.planetType)
  }
  if (filters.techStackId) {
    params.set('techStackId', filters.techStackId)
  }
  const query = params.toString()
  const response = await fetch(`${API_BASE}/study/knowledge/documents${query ? `?${query}` : ''}`)
  if (!response.ok) {
    throw new Error('Unable to load Knowledge documents')
  }
  return response.json()
}

export async function fetchWorkKnowledgeDocuments(
  filters: { subject?: string; topic?: string; goalId?: string; planetType?: string; techStackId?: string } = {},
): Promise<KnowledgeDocument[]> {
  const params = new URLSearchParams()
  if (filters.subject) {
    params.set('subject', filters.subject)
  }
  if (filters.topic) {
    params.set('topic', filters.topic)
  }
  if (filters.goalId) {
    params.set('goalId', filters.goalId)
  }
  if (filters.planetType) {
    params.set('planetType', filters.planetType)
  }
  if (filters.techStackId) {
    params.set('techStackId', filters.techStackId)
  }
  const query = params.toString()
  const response = await fetch(`${API_BASE}/work/knowledge/documents${query ? `?${query}` : ''}`)
  if (!response.ok) {
    throw new Error('Unable to load Work Knowledge documents')
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

export async function fetchWorkKnowledgeDocument(documentId: string): Promise<KnowledgeDocumentDetail> {
  const response = await fetch(`${API_BASE}/work/knowledge/documents/${documentId}`)
  if (!response.ok) {
    throw new Error('Unable to load Work Knowledge document')
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

export async function refreshKnowledgeDocument(documentId: string): Promise<KnowledgeDocumentDetail> {
  const response = await fetch(`${API_BASE}/study/knowledge/documents/${documentId}/status`)
  if (!response.ok) {
    throw new Error('Unable to refresh Knowledge document status')
  }
  return response.json()
}

export async function retryKnowledgeDocument(documentId: string): Promise<KnowledgeDocumentDetail> {
  const response = await fetch(`${API_BASE}/study/knowledge/documents/${documentId}/retry`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Unable to retry Knowledge document')
  }
  return response.json()
}

export async function processWorkKnowledgeDocument(documentId: string): Promise<KnowledgeDocumentDetail> {
  const response = await fetch(`${API_BASE}/work/knowledge/documents/${documentId}/process`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Unable to process Work Knowledge document')
  }
  return response.json()
}

export async function updateKnowledgeDocument(
  documentId: string,
  payload: Partial<Pick<KnowledgeDocumentPayload, 'subject' | 'topic' | 'goalId'>>,
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

export async function fetchStudyAnalytics(): Promise<StudyAnalyticsPayload> {
  const response = await fetch(`${API_BASE}/study/analytics`)
  if (!response.ok) {
    throw new Error('Unable to load Study Analytics')
  }
  return response.json()
}

export async function createStudyAnalyticsReport(): Promise<StudyAnalyticsPayload> {
  const response = await fetch(`${API_BASE}/study/analytics/report`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Unable to create Study Analytics report')
  }
  return response.json()
}

export async function fetchReviewQueue(includeFuture = true): Promise<ReviewQueueItem[]> {
  const response = await fetch(`${API_BASE}/study/review/queue?includeFuture=${includeFuture}`)
  if (!response.ok) {
    throw new Error('Unable to load Review queue')
  }
  return response.json()
}

export async function createWrongQuestion(payload: {
  question: string
  correctAnswer?: string
  explanation?: string
  subject?: string
  topic?: string
  goalId?: string
}) {
  const response = await fetch(`${API_BASE}/study/review/wrong-questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Unable to create Wrong Question')
  }
  return response.json()
}

export async function completeReviewItem(reviewId: string, result = 'remembered') {
  const response = await fetch(`${API_BASE}/study/review/items/${reviewId}/complete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ result }),
  })
  if (!response.ok) {
    throw new Error('Unable to complete Review item')
  }
  return response.json()
}
