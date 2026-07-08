<template>
  <section class="study-plan knowledge-space" aria-labelledby="knowledge-title">
    <p class="eyebrow">Knowledge</p>
    <h2 id="knowledge-title">Knowledge Foundation</h2>

    <form class="knowledge-form" @submit.prevent="registerDocument">
      <label>
        File name
        <input v-model="form.fileName" required placeholder="algebra-notes.md" />
      </label>
      <label>
        Type
        <select v-model="form.fileType" required>
          <option value="txt">txt</option>
          <option value="markdown">markdown</option>
          <option value="pdf">pdf</option>
        </select>
      </label>
      <label>
        Subject
        <input v-model="form.subject" required placeholder="math" />
      </label>
      <label>
        Topic
        <input v-model="form.topic" required placeholder="functions" />
      </label>
      <label class="knowledge-content">
        Content
        <textarea
          v-model="form.content"
          :disabled="form.fileType === 'pdf'"
          rows="7"
          placeholder="Paste txt or markdown content here"
        />
      </label>
      <div class="knowledge-actions">
        <button type="submit" :disabled="isLoading">Register Document</button>
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
          </button>
          <div class="document-meta">
            <span class="status-pill">{{ document.processingStatus }}</span>
            <button
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
          <p class="eyebrow">{{ selectedDocument.document.processingStatus }}</p>
          <h3>{{ selectedDocument.document.fileName }}</h3>
          <p class="surface-copy">
            {{ selectedDocument.chunks.length }} chunks prepared.
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
import { onMounted, ref } from 'vue'
import {
  createKnowledgeDocument,
  fetchKnowledgeDocument,
  fetchKnowledgeDocuments,
  processKnowledgeDocument,
  type KnowledgeDocument,
  type KnowledgeDocumentDetail,
  type KnowledgeDocumentPayload,
} from '../../../services/api'

const form = ref<KnowledgeDocumentPayload>({
  fileName: 'algebra-notes.md',
  fileType: 'markdown',
  subject: 'math',
  topic: 'functions',
  content: '# Functions\n\nA function maps each input to one output.',
})
const documents = ref<KnowledgeDocument[]>([])
const selectedDocument = ref<KnowledgeDocumentDetail | null>(null)
const statusMessage = ref('Register a document, then process it into chunks.')
const isLoading = ref(false)

onMounted(loadDocuments)

async function loadDocuments() {
  isLoading.value = true
  try {
    documents.value = await fetchKnowledgeDocuments()
    if (documents.value.length && !selectedDocument.value) {
      await selectDocument(documents.value[0].id)
    }
  } finally {
    isLoading.value = false
  }
}

async function registerDocument() {
  isLoading.value = true
  try {
    const payload = { ...form.value }
    if (payload.fileType === 'pdf') {
      payload.content = ''
    }
    const document = await createKnowledgeDocument(payload)
    statusMessage.value = 'Document registered.'
    await loadDocuments()
    await selectDocument(document.id)
  } catch (error) {
    statusMessage.value = error instanceof Error ? error.message : 'Document registration failed.'
  } finally {
    isLoading.value = false
  }
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
