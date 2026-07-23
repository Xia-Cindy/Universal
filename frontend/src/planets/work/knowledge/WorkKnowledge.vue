<template>
  <section class="study-plan knowledge-space" aria-labelledby="work-knowledge-title">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Work Knowledge</p>
        <h2 id="work-knowledge-title">Work Knowledge Space</h2>
        <p class="surface-copy">沉淀技术栈资料、岗位 JD、面试题、项目证据和简历素材；也可以引用 Study Knowledge。</p>
      </div>
      <RouterLink class="secondary-action" to="/study/knowledge">Reference Study Knowledge</RouterLink>
    </div>

    <div class="tech-channel-tabs" aria-label="Work Knowledge views">
      <button
        v-for="view in views"
        :key="view.value"
        type="button"
        :class="{ selected: activeView === view.value }"
        @click="activeView = view.value"
      >
        {{ view.label }}
      </button>
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
        Work area
        <input v-model="form.subject" required placeholder="Backend / Frontend / AI Interview" />
      </label>
      <label>
        Topic
        <input v-model="form.topic" required placeholder="FastAPI auth / JD keywords" />
      </label>
      <label class="wide-field">
        Notes
        <textarea v-model="form.notes" rows="3" placeholder="Optional job, project, or resume context" />
      </label>
      <div class="knowledge-actions">
        <button type="submit" :disabled="!canUpload">Upload to Work Knowledge</button>
        <span>{{ uploadHint }}</span>
      </div>
    </form>

    <div v-if="isLoading" class="knowledge-state">Loading Work Knowledge...</div>

    <div v-else-if="!visibleDocuments.length" class="knowledge-state">
      <strong>{{ emptyTitle }}</strong>
      <span>{{ emptyCopy }}</span>
    </div>

    <div v-else class="knowledge-grid">
      <div class="knowledge-list" aria-label="Work Knowledge documents">
        <article
          v-for="document in visibleDocuments"
          :key="document.id"
          class="knowledge-document"
          :class="{ selected: selectedDocument?.document.id === document.id }"
        >
          <button type="button" class="document-main" @click="selectDocument(document.id)">
            <span>{{ document.fileName }}</span>
            <small>{{ document.subject }} / {{ document.topic }}</small>
            <small>{{ document.goalId ? 'Study Knowledge reference' : 'Work Knowledge' }}</small>
            <small>{{ providerLabel(document) }}</small>
          </button>
          <div class="document-meta">
            <span class="status-pill">{{ displayDocumentStatus(document) }}</span>
            <button
              v-if="canProcess(document)"
              type="button"
              :disabled="document.processingStatus === 'processed'"
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
          <p class="eyebrow">{{ selectedDocument.document.goalId ? 'Study Reference' : 'Work Knowledge' }}</p>
          <h3>{{ selectedDocument.document.fileName }}</h3>
          <p class="surface-copy">
            <span v-if="selectedDocument.document.fileType === 'pdf' && selectedDocument.document.provider === 'local'">
              Metadata saved. PDF parser is not enabled yet.
            </span>
            <span v-else>
              {{ selectedDocument.chunks.length }} chunks prepared.
            </span>
            <span v-if="selectedDocument.document.provider !== 'local'">
              Provider: {{ selectedDocument.document.provider }} · {{ selectedDocument.document.providerStatus || 'pending' }}
            </span>
          </p>
          <div v-if="selectedDocument.chunks.length" class="chunk-list">
            <article v-for="chunk in selectedDocument.chunks" :key="chunk.id" class="chunk-item">
              <strong>Chunk {{ chunk.chunkIndex + 1 }}</strong>
              <p>{{ chunk.content }}</p>
            </article>
          </div>
          <div
            v-else-if="selectedDocument.document.fileType === 'pdf' && selectedDocument.document.provider === 'local'"
            class="knowledge-state"
          >
            PDF metadata is available for organization. Text parsing will come in a later milestone.
          </div>
          <div v-else class="knowledge-state">Process this document to create provider-backed chunks.</div>
        </template>
        <template v-else>
          <div class="knowledge-state">Select a document to inspect its chunks.</div>
        </template>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  createWorkKnowledgeDocument,
  fetchWorkKnowledgeDocument,
  fetchWorkKnowledgeDocuments,
  processWorkKnowledgeDocument,
  type KnowledgeDocument,
  type KnowledgeDocumentDetail,
  type KnowledgeDocumentPayload,
} from '../../../services/api'

const views = [
  { value: 'work', label: 'Work Knowledge' },
  { value: 'study', label: 'Study References' },
  { value: 'all', label: 'All Shared Knowledge' },
]
const activeView = ref('work')
const form = ref<KnowledgeDocumentPayload>({
  fileName: '',
  fileType: 'txt',
  subject: '',
  topic: '',
  goalId: null,
  content: '',
  contentEncoding: 'text',
})
const selectedFileName = ref('')
const documents = ref<KnowledgeDocument[]>([])
const selectedDocument = ref<KnowledgeDocumentDetail | null>(null)
const statusMessage = ref('Upload txt, markdown, or PDF metadata.')
const isLoading = ref(false)
const isUploading = ref(false)

const workDocuments = computed(() => documents.value.filter((document) => !document.goalId))
const studyReferences = computed(() => documents.value.filter((document) => document.goalId))
const visibleDocuments = computed(() => {
  if (activeView.value === 'study') {
    return studyReferences.value
  }
  if (activeView.value === 'all') {
    return documents.value
  }
  return workDocuments.value
})
const canUpload = computed(
  () =>
    !isUploading.value &&
    Boolean(selectedFileName.value) &&
    Boolean(form.value.fileName) &&
    Boolean(form.value.subject.trim()) &&
    Boolean(form.value.topic.trim()),
)
const uploadHint = computed(() => {
  if (isUploading.value) {
    return 'Uploading document...'
  }
  if (canUpload.value) {
    return statusMessage.value
  }
  return 'Choose file + Work area + Topic to upload.'
})
const emptyTitle = computed(() =>
  activeView.value === 'study' ? 'No Study Knowledge references yet.' : 'No Work Knowledge yet.',
)
const emptyCopy = computed(() =>
  activeView.value === 'study'
    ? 'Study-linked documents appear here as references. Work can cite them without owning them.'
    : 'Add technical notes, JD material, interview questions, or project evidence.',
)

onMounted(loadDocuments)
watch(activeView, () => {
  if (
    selectedDocument.value &&
    !visibleDocuments.value.some((document) => document.id === selectedDocument.value?.document.id)
  ) {
    selectedDocument.value = null
  }
})

async function loadDocuments() {
  isLoading.value = true
  try {
    documents.value = await fetchWorkKnowledgeDocuments()
    if (
      selectedDocument.value &&
      !visibleDocuments.value.some((document) => document.id === selectedDocument.value?.document.id)
    ) {
      selectedDocument.value = null
    }
    if (visibleDocuments.value.length && !selectedDocument.value) {
      await selectDocument(visibleDocuments.value[0].id)
    }
  } finally {
    isLoading.value = false
  }
}

async function uploadDocument() {
  if (!canUpload.value) {
    statusMessage.value = 'Choose a supported file and fill Work area and Topic first.'
    return
  }
  isUploading.value = true
  try {
    const payload = { ...form.value, goalId: null, storagePath: selectedFileName.value }
    const document = await createWorkKnowledgeDocument(payload)
    statusMessage.value = document.fileType === 'pdf' ? 'PDF metadata uploaded.' : 'Document uploaded.'
    if (document.fileType !== 'pdf') {
      selectedDocument.value = await processWorkKnowledgeDocument(document.id)
      statusMessage.value =
        selectedDocument.value.document.processingStatus === 'processed'
          ? 'Document uploaded and processed.'
          : 'Document uploaded but processing failed.'
    }
    activeView.value = 'work'
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
  form.value.contentEncoding = fileType === 'pdf' ? 'base64' : 'text'
  form.value.content = fileType === 'pdf' ? await fileToBase64(file) : await file.text()
  if (!form.value.topic) {
    form.value.topic = file.name.replace(/\.[^.]+$/, '')
  }
  statusMessage.value =
    fileType === 'pdf'
      ? 'PDF metadata is ready to upload.'
      : 'File content is ready to upload and process.'
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const result = String(reader.result || '')
      resolve(result.includes(',') ? result.split(',')[1] : result)
    }
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
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

function displayDocumentStatus(document: KnowledgeDocument) {
  if (document.fileType === 'pdf' && document.provider === 'local') {
    return 'metadata saved'
  }
  return displayStatus(document.processingStatus)
}

function canProcess(document: KnowledgeDocument) {
  return document.provider !== 'local' || document.fileType !== 'pdf'
}

function providerLabel(document: KnowledgeDocument) {
  if (document.provider === 'local') {
    return 'Local Knowledge'
  }
  return `Provider: ${document.provider}${document.providerStatus ? ` · ${document.providerStatus}` : ''}`
}

async function selectDocument(documentId: string) {
  selectedDocument.value = await fetchWorkKnowledgeDocument(documentId)
}

async function processDocument(documentId: string) {
  isLoading.value = true
  try {
    selectedDocument.value = await processWorkKnowledgeDocument(documentId)
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
