<template>
  <section class="study-plan knowledge-space" aria-labelledby="knowledge-title">
    <p class="eyebrow">Knowledge</p>
    <h2 id="knowledge-title">Knowledge Space</h2>

    <div class="knowledge-filter">
      <label>
        Goal filter
        <select v-model="goalFilter" @change="loadDocuments">
          <option value="all">All Knowledge</option>
          <option value="independent">Independent Knowledge</option>
          <option v-for="goal in goals" :key="goal.id" :value="goal.id">
            {{ goal.goalName }}
          </option>
        </select>
      </label>
    </div>

    <form class="knowledge-form" @submit.prevent="uploadDocument">
      <label class="wide-field">
        File
        <input accept=".txt,.md,.markdown,.pdf" required type="file" @change="selectFile" />
      </label>
      <label>
        File type
        <input :value="form.fileType || 'Select a file'" disabled />
      </label>
      <label>
        Subject
        <input v-model="form.subject" required placeholder="systems" />
      </label>
      <label>
        Topic
        <input v-model="form.topic" required placeholder="chapter 1" />
      </label>
      <label>
        Goal link
        <select v-model="form.goalId">
          <option :value="null">Independent Knowledge</option>
          <option v-for="goal in goals" :key="goal.id" :value="goal.id">
            {{ goal.goalName }}
          </option>
        </select>
      </label>
      <label class="wide-field">
        Notes
        <textarea v-model="form.notes" rows="3" placeholder="Optional reading note or context" />
      </label>
      <div class="knowledge-actions">
        <button type="submit" :disabled="!canUpload">Upload</button>
        <span>{{ statusMessage }}</span>
      </div>
    </form>

    <div v-if="isLoading" class="knowledge-state">Loading Knowledge space...</div>

    <div v-else-if="!documents.length" class="knowledge-state">
      <strong>No documents yet.</strong>
      <span>Add a txt or markdown document to start building your knowledge space.</span>
    </div>

    <div v-else class="knowledge-grid">
      <div class="knowledge-list" aria-label="Knowledge documents">
        <article
          v-for="document in documents"
          :key="document.id"
          class="knowledge-document"
          :class="{ selected: selectedDocument?.document.id === document.id }"
        >
          <button type="button" class="document-main" @click="selectDocument(document.id)">
            <span>{{ document.fileName }}</span>
            <small>{{ document.subject }} / {{ document.topic }}</small>
            <small>{{ documentGoalLabel(document.goalId) }}</small>
          </button>
          <div class="document-meta">
            <span class="status-pill">{{ displayStatus(document.processingStatus) }}</span>
            <button
              type="button"
              :disabled="document.processingStatus === 'processed' || document.fileType === 'pdf'"
              @click="processDocument(document.id)"
            >
              Process
            </button>
          </div>
          <p v-if="document.errorMessage" class="error-text">{{ document.errorMessage }}</p>
        </article>
      </div>

      <aside class="chunk-panel">
        <template v-if="selectedDocument">
          <p class="eyebrow">{{ selectedDocument.document.processingStatus }}</p>
          <h3>{{ selectedDocument.document.fileName }}</h3>
          <p class="surface-copy">
            {{ selectedDocument.chunks.length }} chunks prepared.
            <span v-if="selectedDocument.document.fileType === 'pdf'">
              PDF metadata is saved; parser support is not enabled yet.
            </span>
          </p>
          <div v-if="selectedDocument.chunks.length" class="chunk-list">
            <article v-for="chunk in selectedDocument.chunks" :key="chunk.id" class="chunk-item">
              <strong>Chunk {{ chunk.chunkIndex + 1 }}</strong>
              <p>{{ chunk.content }}</p>
            </article>
          </div>
          <div v-else class="knowledge-state">Process this document to create plain text chunks.</div>
        </template>
        <template v-else>
          <div class="knowledge-state">Select a document to inspect its chunks.</div>
        </template>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  createKnowledgeDocument,
  fetchKnowledgeDocument,
  fetchKnowledgeDocuments,
  fetchStudyWorkspace,
  processKnowledgeDocument,
  type KnowledgeDocument,
  type KnowledgeDocumentDetail,
  type KnowledgeDocumentPayload,
  type StudyGoal,
} from '../../../services/api'

const form = ref<KnowledgeDocumentPayload>({
  fileName: '',
  fileType: 'txt',
  subject: '',
  topic: '',
  goalId: null,
  content: '',
})
const goals = ref<StudyGoal[]>([])
const goalFilter = ref('all')
const selectedFileName = ref('')
const documents = ref<KnowledgeDocument[]>([])
const selectedDocument = ref<KnowledgeDocumentDetail | null>(null)
const statusMessage = ref('Upload txt, markdown, or PDF metadata.')
const isLoading = ref(false)
const isUploading = ref(false)
const canUpload = computed(
  () =>
    !isUploading.value &&
    Boolean(selectedFileName.value) &&
    Boolean(form.value.fileName) &&
    Boolean(form.value.subject.trim()) &&
    Boolean(form.value.topic.trim()),
)

onMounted(loadDocuments)
onMounted(loadGoalContext)

async function loadDocuments() {
  isLoading.value = true
  try {
    const remoteDocuments = await fetchKnowledgeDocuments(
      goalFilter.value !== 'all' && goalFilter.value !== 'independent'
        ? { goalId: goalFilter.value }
        : {},
    )
    documents.value =
      goalFilter.value === 'independent'
        ? remoteDocuments.filter((document: KnowledgeDocument) => !document.goalId)
        : remoteDocuments
    if (
      selectedDocument.value &&
      !documents.value.some((document) => document.id === selectedDocument.value?.document.id)
    ) {
      selectedDocument.value = null
    }
    if (documents.value.length && !selectedDocument.value) {
      await selectDocument(documents.value[0].id)
    }
  } finally {
    isLoading.value = false
  }
}

async function loadGoalContext() {
  const workspace = await fetchStudyWorkspace()
  goals.value = workspace.goals
  if (workspace.currentGoal && !form.value.goalId) {
    form.value.goalId = workspace.currentGoal.id
    goalFilter.value = workspace.currentGoal.id
    await loadDocuments()
  }
}

async function uploadDocument() {
  if (!canUpload.value) {
    statusMessage.value = 'Choose a supported file and fill Subject and Topic first.'
    return
  }
  isUploading.value = true
  try {
    const payload = { ...form.value, storagePath: selectedFileName.value }
    if (payload.fileType === 'pdf') {
      payload.content = ''
    }
    const document = await createKnowledgeDocument(payload)
    statusMessage.value = document.fileType === 'pdf' ? 'PDF metadata uploaded.' : 'Document uploaded.'
    if (document.fileType !== 'pdf') {
      selectedDocument.value = await processKnowledgeDocument(document.id)
      statusMessage.value =
        selectedDocument.value.document.processingStatus === 'processed'
          ? 'Document uploaded and processed.'
          : 'Document uploaded but processing failed.'
    }
    await loadDocuments()
    await selectDocument(document.id)
  } catch (error) {
    statusMessage.value = error instanceof Error ? error.message : 'Document upload failed.'
  } finally {
    isUploading.value = false
  }
}

async function selectFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) {
    selectedFileName.value = ''
    return
  }
  const fileType = detectFileType(file.name)
  if (!fileType) {
    statusMessage.value = 'Supported file types: txt, markdown, pdf.'
    input.value = ''
    selectedFileName.value = ''
    return
  }
  selectedFileName.value = file.name
  form.value.fileName = file.name
  form.value.fileType = fileType
  form.value.content = fileType === 'pdf' ? '' : await file.text()
  if (!form.value.topic) {
    form.value.topic = file.name.replace(/\.[^.]+$/, '')
  }
  statusMessage.value =
    fileType === 'pdf'
      ? 'PDF metadata is ready to upload.'
      : 'File content is ready to upload and process.'
}

function detectFileType(fileName: string): KnowledgeDocumentPayload['fileType'] | null {
  const lower = fileName.toLowerCase()
  if (lower.endsWith('.txt')) {
    return 'txt'
  }
  if (lower.endsWith('.md') || lower.endsWith('.markdown')) {
    return 'markdown'
  }
  if (lower.endsWith('.pdf')) {
    return 'pdf'
  }
  return null
}

function displayStatus(status: KnowledgeDocument['processingStatus']) {
  return status === 'parsing' || status === 'chunking' ? 'processing' : status
}

function documentGoalLabel(goalId?: string | null) {
  if (!goalId) {
    return 'Independent Knowledge'
  }
  return goals.value.find((goal) => goal.id === goalId)?.goalName || 'Linked Goal'
}

async function selectDocument(documentId: string) {
  selectedDocument.value = await fetchKnowledgeDocument(documentId)
}

async function processDocument(documentId: string) {
  isLoading.value = true
  try {
    selectedDocument.value = await processKnowledgeDocument(documentId)
    statusMessage.value =
      selectedDocument.value.document.processingStatus === 'processed'
        ? 'Document processed into chunks.'
        : 'Document processing failed.'
    await loadDocuments()
    await selectDocument(documentId)
  } finally {
    isLoading.value = false
  }
}
</script>
