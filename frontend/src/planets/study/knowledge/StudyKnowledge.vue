<template>
  <section class="study-plan knowledge-space" aria-labelledby="knowledge-title">
    <p class="eyebrow">Knowledge</p>
    <h2 id="knowledge-title">Knowledge Space</h2>

    <div class="knowledge-mode-tabs" aria-label="Knowledge input mode">
      <button type="button" :class="{ selected: inputMode === 'upload' }" @click="inputMode = 'upload'">Upload File</button>
      <button type="button" :class="{ selected: inputMode === 'article' }" @click="inputMode = 'article'">Write Article</button>
    </div>

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

    <form v-if="inputMode === 'upload'" class="knowledge-form" @submit.prevent="uploadDocument">
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
        <span>{{ uploadHint }}</span>
      </div>
    </form>

    <form v-else class="knowledge-form study-article-writer" @submit.prevent="saveArticle">
      <label class="wide-field">
        Article title
        <input v-model="articleForm.title" required placeholder="写一篇学习文章" />
      </label>
      <label>
        Subject
        <input v-model="articleForm.subject" required placeholder="computer systems" />
      </label>
      <label>
        Topic
        <input v-model="articleForm.topic" required placeholder="memory hierarchy" />
      </label>
      <label>
        Goal link
        <select v-model="articleForm.goalId">
          <option :value="null">Independent Knowledge</option>
          <option v-for="goal in goals" :key="goal.id" :value="goal.id">
            {{ goal.goalName }}
          </option>
        </select>
      </label>
      <label>
        Tags
        <input v-model="articleTagsText" placeholder="chapter, note, csapp" />
      </label>
      <label class="wide-field">
        Body
        <input ref="imageInputRef" class="visually-hidden" type="file" accept="image/*" @change="insertSelectedImage" />
        <input ref="colorInputRef" v-model="textColor" class="visually-hidden" type="color" @input="applyTextColor" />
        <div class="article-inline-toolbar" aria-label="学习文章工具栏">
          <div class="toolbar-group" aria-label="段落">
            <button class="icon-tool-button" type="button" title="正文段落" @mousedown.prevent="insertParagraph">¶</button>
            <button class="icon-tool-button" type="button" title="二级标题" @mousedown.prevent="insertHeading">H2</button>
          </div>
          <div class="toolbar-group" aria-label="文字格式">
            <button class="icon-tool-button strong-tool" type="button" title="加粗" @mousedown.prevent="formatBold">B</button>
            <button class="icon-tool-button color-tool" type="button" title="文字颜色" @mousedown.prevent="openTextColorPicker">
              <span class="color-tool-dot" :style="{ background: textColor }"></span>A
            </button>
          </div>
          <div class="toolbar-group" aria-label="插入正文内容">
            <button class="icon-tool-button" type="button" title="插入图片" @mousedown.prevent="openImagePicker">▧</button>
            <button class="icon-tool-button" type="button" title="插入表格" @mousedown.prevent="insertTable">▦</button>
            <button class="icon-tool-button" type="button" title="插入代码块" @mousedown.prevent="insertCodeBlock">&lt;/&gt;</button>
          </div>
          <div class="toolbar-group" aria-label="对齐">
            <button class="icon-tool-button" type="button" title="左对齐" @mousedown.prevent="alignSelection('left')">☰</button>
            <button class="icon-tool-button" type="button" title="居中" @mousedown.prevent="alignSelection('center')">≡</button>
            <button class="icon-tool-button" type="button" title="右对齐" @mousedown.prevent="alignSelection('right')">☷</button>
          </div>
          <div class="toolbar-group" aria-label="表格操作">
            <button class="icon-tool-button" type="button" title="增加行" @mousedown.prevent="addTableRowAfter">R+</button>
            <button class="icon-tool-button" type="button" title="删除行" @mousedown.prevent="deleteTableRow">R-</button>
            <button class="icon-tool-button" type="button" title="增加列" @mousedown.prevent="addTableColumnAfter">C+</button>
            <button class="icon-tool-button" type="button" title="删除列" @mousedown.prevent="deleteTableColumn">C-</button>
            <button class="icon-tool-button" type="button" title="合并单元格" @mousedown.prevent="mergeTableCellRight">⇥</button>
            <button class="icon-tool-button" type="button" title="拆分单元格" @mousedown.prevent="splitTableCell">⇤</button>
          </div>
        </div>
        <div
          ref="editorRef"
          class="article-rich-editor"
          contenteditable="true"
          data-placeholder="像写文档一样写学习内容。图片、表格、代码块会插入到正文光标所在位置。"
          @input="syncArticleBody"
          @keyup="rememberSelection"
          @mouseup="rememberSelection"
          @paste="handleEditorPaste"
        ></div>
      </label>
      <div class="knowledge-actions">
        <button type="submit" :disabled="!canSaveArticle">Save Article</button>
        <span>{{ articleStatus }}</span>
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
            <button
              v-if="document.processingStatus === 'failed' && document.provider !== 'local'"
              type="button"
              @click="retryDocument(document.id)"
            >
              Retry
            </button>
          </div>
          <p v-if="document.errorMessage" class="error-text">{{ document.errorMessage }}</p>
          <small v-if="document.providerErrorCode" class="error-code">{{ document.providerErrorCode }}</small>
        </article>
      </div>

      <aside class="chunk-panel">
        <template v-if="selectedDocument">
          <p class="eyebrow">{{ selectedDocument.document.processingStatus }}</p>
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
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  createKnowledgeDocument,
  fetchKnowledgeDocument,
  fetchKnowledgeDocuments,
  fetchStudyWorkspace,
  processKnowledgeDocument,
  refreshKnowledgeDocument,
  retryKnowledgeDocument,
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
  contentEncoding: 'text',
})
const route = useRoute()
const goals = ref<StudyGoal[]>([])
const goalFilter = ref('all')
const selectedFileName = ref('')
const documents = ref<KnowledgeDocument[]>([])
const selectedDocument = ref<KnowledgeDocumentDetail | null>(null)
const inputMode = ref<'upload' | 'article'>('upload')
const statusMessage = ref('Upload txt, markdown, or PDF metadata.')
const articleStatus = ref('Write an article and save it into Study Knowledge.')
const articleTagsText = ref('')
const isLoading = ref(false)
const isUploading = ref(false)
const isSavingArticle = ref(false)
const editorRef = ref<HTMLElement | null>(null)
const imageInputRef = ref<HTMLInputElement | null>(null)
const colorInputRef = ref<HTMLInputElement | null>(null)
const savedRange = ref<Range | null>(null)
const textColor = ref('#1f2937')
let statusPollTimer: ReturnType<typeof setInterval> | null = null
const articleForm = ref({
  title: '',
  subject: '',
  topic: '',
  goalId: null as string | null,
  body: '',
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
  return 'Choose file + Subject + Topic to upload.'
})
const canSaveArticle = computed(
  () =>
    !isSavingArticle.value &&
    Boolean(articleForm.value.title.trim()) &&
    Boolean(articleForm.value.subject.trim()) &&
    Boolean(articleForm.value.topic.trim()) &&
    Boolean(articleForm.value.body.trim()),
)

onMounted(loadDocuments)
onMounted(loadGoalContext)
onUnmounted(() => stopStatusPolling())

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
    const requestedDocumentId = typeof route.query.documentId === 'string' ? route.query.documentId : ''
    const requestedDocument = documents.value.find((document) => document.id === requestedDocumentId)
    if (requestedDocument) {
      await selectDocument(requestedDocument.id)
    } else if (documents.value.length && !selectedDocument.value) {
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
    articleForm.value.goalId = workspace.currentGoal.id
    goalFilter.value = workspace.currentGoal.id
    await loadDocuments()
  }
}

async function saveArticle() {
  syncArticleBody()
  if (!canSaveArticle.value) {
    articleStatus.value = 'Fill title, subject, topic and body before saving.'
    return
  }
  isSavingArticle.value = true
  try {
    const title = articleForm.value.title.trim()
    const document = await createKnowledgeDocument({
      fileName: `${slugify(title)}.md`,
      fileType: 'markdown',
      subject: articleForm.value.subject.trim(),
      topic: articleForm.value.topic.trim(),
      goalId: articleForm.value.goalId,
      planetType: 'study',
      tags: splitTags(articleTagsText.value),
      content: `# ${title}\n\n${articleForm.value.body.trim()}`,
      contentEncoding: 'text',
      storagePath: `study-article:${title}`,
    })
    selectedDocument.value = await processKnowledgeDocument(document.id)
    articleStatus.value =
      selectedDocument.value.document.processingStatus === 'processed'
        ? 'Article saved into Knowledge and processed.'
        : 'Article saved, but processing needs attention.'
    articleForm.value = {
      title: '',
      subject: '',
      topic: '',
      goalId: articleForm.value.goalId,
      body: '',
    }
    if (editorRef.value) {
      editorRef.value.innerHTML = ''
    }
    articleTagsText.value = ''
    await loadDocuments()
    await selectDocument(document.id)
  } catch (error) {
    articleStatus.value = error instanceof Error ? error.message : 'Article save failed.'
  } finally {
    isSavingArticle.value = false
  }
}

function insertParagraph() {
  insertHtmlAtCursor('<p><br></p>')
}

function insertHeading() {
  insertHtmlAtCursor('<h2>新章节</h2><p><br></p>')
}

function formatBold() {
  restoreSelection()
  document.execCommand('bold')
  syncArticleBody()
}

function openImagePicker() {
  rememberSelection()
  imageInputRef.value?.click()
}

function openTextColorPicker() {
  rememberSelection()
  colorInputRef.value?.click()
}

function applyTextColor() {
  restoreSelection()
  document.execCommand('foreColor', false, textColor.value)
  syncArticleBody()
}

async function insertSelectedImage(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    insertHtmlAtCursor(`<figure class="article-image-fragment"><img src="${escapeAttribute(await readImageAsDataUrl(file))}" alt="${escapeAttribute(file.name)}"><figcaption>${escapeHtml(file.name)}</figcaption></figure><p><br></p>`)
  }
  input.value = ''
}

function insertTable(rows = 3, columns = 3) {
  const body = Array.from({ length: rows }, () =>
    `<tr>${Array.from({ length: columns }, () => '<td contenteditable="true"><br></td>').join('')}</tr>`,
  ).join('')
  insertHtmlAtCursor(`<table class="article-table-fragment"><tbody>${body}</tbody></table><p><br></p>`)
}

function insertCodeBlock() {
  insertHtmlAtCursor('<pre class="article-code-fragment"><code contenteditable="true">plain text</code></pre><p><br></p>')
}

function alignSelection(align: 'left' | 'center' | 'right') {
  restoreSelection()
  const cell = closestSelectedElement('td') as HTMLElement | null
  if (cell) {
    cell.style.textAlign = align
  } else {
    document.execCommand(align === 'left' ? 'justifyLeft' : align === 'center' ? 'justifyCenter' : 'justifyRight')
  }
  syncArticleBody()
}

function addTableRowAfter() {
  const cell = currentTableCell()
  const row = cell?.parentElement as HTMLTableRowElement | null
  if (!cell || !row) return
  const newRow = document.createElement('tr')
  const count = Array.from(row.children).reduce((sum, item) => sum + ((item as HTMLTableCellElement).colSpan || 1), 0)
  for (let index = 0; index < count; index += 1) newRow.appendChild(createEditableCell())
  row.after(newRow)
  syncArticleBody()
}

function deleteTableRow() {
  const cell = currentTableCell()
  const row = cell?.parentElement as HTMLTableRowElement | null
  const table = row?.closest('table')
  if (!row || !table) return
  if (table.querySelectorAll('tr').length <= 1) table.remove()
  else row.remove()
  syncArticleBody()
}

function addTableColumnAfter() {
  const cell = currentTableCell()
  const row = cell?.parentElement as HTMLTableRowElement | null
  const table = row?.closest('table')
  if (!cell || !row || !table) return
  const index = Array.from(row.children).indexOf(cell)
  table.querySelectorAll('tr').forEach((tableRow) => tableRow.children[index]?.after(createEditableCell()))
  syncArticleBody()
}

function deleteTableColumn() {
  const cell = currentTableCell()
  const row = cell?.parentElement as HTMLTableRowElement | null
  const table = row?.closest('table')
  if (!cell || !row || !table) return
  const index = Array.from(row.children).indexOf(cell)
  table.querySelectorAll('tr').forEach((tableRow) => tableRow.children[index]?.remove())
  syncArticleBody()
}

function mergeTableCellRight() {
  const cell = currentTableCell()
  const next = cell?.nextElementSibling as HTMLTableCellElement | null
  if (!cell || !next) return
  cell.colSpan = (cell.colSpan || 1) + (next.colSpan || 1)
  next.remove()
  syncArticleBody()
}

function splitTableCell() {
  const cell = currentTableCell()
  const span = cell?.colSpan || 1
  if (!cell || span <= 1) return
  cell.colSpan = 1
  for (let index = 1; index < span; index += 1) cell.after(createEditableCell())
  syncArticleBody()
}

function currentTableCell() {
  return closestSelectedElement('td') as HTMLTableCellElement | null
}

function closestSelectedElement(selector: string) {
  const selection = window.getSelection()
  if (!selection || !selection.rangeCount || !editorRef.value) return null
  let node: Node | null = selection.getRangeAt(0).startContainer
  if (node.nodeType === Node.TEXT_NODE) node = node.parentElement
  const found = (node as Element | null)?.closest(selector) || null
  return found && editorRef.value.contains(found) ? found : null
}

function createEditableCell() {
  const cell = document.createElement('td')
  cell.contentEditable = 'true'
  cell.innerHTML = '<br>'
  return cell
}

function rememberSelection() {
  const selection = window.getSelection()
  if (!selection || !selection.rangeCount || !editorRef.value) return
  const range = selection.getRangeAt(0)
  if (editorRef.value.contains(range.commonAncestorContainer)) savedRange.value = range.cloneRange()
}

function restoreSelection() {
  if (!editorRef.value) return
  editorRef.value.focus()
  const selection = window.getSelection()
  if (!selection) return
  selection.removeAllRanges()
  const range = savedRange.value || document.createRange()
  if (!savedRange.value) {
    range.selectNodeContents(editorRef.value)
    range.collapse(false)
  }
  selection.addRange(range)
}

function insertHtmlAtCursor(html: string) {
  restoreSelection()
  const selection = window.getSelection()
  if (!selection || !selection.rangeCount || !editorRef.value) return
  const range = selection.getRangeAt(0)
  const fragment = range.createContextualFragment(html)
  const lastNode = fragment.lastChild
  range.deleteContents()
  range.insertNode(fragment)
  if (lastNode) {
    const nextRange = document.createRange()
    nextRange.setStartAfter(lastNode)
    nextRange.collapse(true)
    selection.removeAllRanges()
    selection.addRange(nextRange)
    savedRange.value = nextRange.cloneRange()
  }
  syncArticleBody()
}

function handleEditorPaste(event: ClipboardEvent) {
  const image = Array.from(event.clipboardData?.items || []).find((item) => item.type.startsWith('image/'))
  if (!image) return
  event.preventDefault()
  const file = image.getAsFile()
  if (file) readImageAsDataUrl(file).then((data) => insertHtmlAtCursor(`<figure class="article-image-fragment"><img src="${escapeAttribute(data)}" alt="pasted image"></figure><p><br></p>`))
}

function syncArticleBody() {
  articleForm.value.body = editorRef.value?.innerHTML || ''
}

function readImageAsDataUrl(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

function escapeHtml(value: string) {
  const container = document.createElement('div')
  container.textContent = value
  return container.innerHTML
}

function escapeAttribute(value: string) {
  return escapeHtml(value).replace(/"/g, '&quot;')
}

async function uploadDocument() {
  if (!canUpload.value) {
    statusMessage.value = 'Choose a supported file and fill Subject and Topic first.'
    return
  }
  isUploading.value = true
  try {
    const payload = { ...form.value, storagePath: selectedFileName.value }
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

function splitTags(value: string) {
  return value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

function slugify(value: string) {
  const slug = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return slug || `study-article-${Date.now()}`
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

function documentGoalLabel(goalId?: string | null) {
  if (!goalId) {
    return 'Independent Knowledge'
  }
  return goals.value.find((goal) => goal.id === goalId)?.goalName || 'Linked Goal'
}

async function selectDocument(documentId: string) {
  selectedDocument.value = await fetchKnowledgeDocument(documentId)
  if (isProviderProcessing(selectedDocument.value.document)) {
    startStatusPolling(documentId)
  } else {
    stopStatusPolling()
  }
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

async function retryDocument(documentId: string) {
  isLoading.value = true
  try {
    selectedDocument.value = await retryKnowledgeDocument(documentId)
    await loadDocuments()
    await selectDocument(documentId)
  } finally {
    isLoading.value = false
  }
}

function isProviderProcessing(document: KnowledgeDocument) {
  return document.provider !== 'local' && ['parsing', 'chunking'].includes(document.processingStatus)
}

function startStatusPolling(documentId: string) {
  stopStatusPolling()
  statusPollTimer = setInterval(async () => {
    try {
      const detail = await refreshKnowledgeDocument(documentId)
      selectedDocument.value = detail
      const item = documents.value.find((document) => document.id === documentId)
      if (item) {
        Object.assign(item, detail.document)
      }
      if (!isProviderProcessing(detail.document)) {
        stopStatusPolling()
      }
    } catch (error) {
      statusMessage.value = error instanceof Error ? error.message : 'Unable to refresh provider status.'
    }
  }, 2500)
}

function stopStatusPolling() {
  if (statusPollTimer) {
    clearInterval(statusPollTimer)
    statusPollTimer = null
  }
}
</script>
