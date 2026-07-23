<template>
  <section class="study-plan" aria-labelledby="tech-stack-detail-title">
    <RouterLink class="secondary-action" to="/work/tech-stack">Back to Tech Stack</RouterLink>

    <div v-if="detail" class="home-section">
      <div class="section-heading">
        <div>
          <p class="eyebrow">Tech Stack Detail</p>
          <h2 id="tech-stack-detail-title">{{ detail.techStack.name }}</h2>
          <p class="surface-copy">{{ detail.techStack.description || detail.techStack.category }}</p>
        </div>
        <div class="knowledge-actions">
          <button class="secondary-action" type="button" @click="showStackEditor = !showStackEditor">
            {{ showStackEditor ? 'Close Edit' : 'Edit Stack' }}
          </button>
          <button class="danger-action" type="button" @click="archiveStack">Archive Stack</button>
        </div>
      </div>

      <section v-if="showStackEditor" class="home-section stack-editor-panel">
        <div class="section-heading">
          <h3>管理技术栈</h3>
          <span>{{ stackStatus }}</span>
        </div>
        <form class="study-form" @submit.prevent="submitStackUpdate">
          <label>
            技术名称
            <input v-model="stackForm.name" required />
          </label>
          <label>
            分类
            <input v-model="stackForm.category" required />
          </label>
          <label>
            熟练度
            <select v-model="stackForm.proficiency">
              <option value="learning">Learning</option>
              <option value="practicing">Practicing</option>
              <option value="project-ready">Project ready</option>
            </select>
          </label>
          <label>
            标签
            <input v-model="stackTagsText" placeholder="java, spring, backend" />
          </label>
          <label class="wide-field">
            描述
            <textarea v-model="stackForm.description" rows="3" />
          </label>
          <div class="knowledge-actions">
            <button type="submit">Save Stack</button>
          </div>
        </form>
      </section>

      <form class="article-writing-room" @submit.prevent="submitArticle">
        <aside class="article-outline-panel" aria-label="文章目录">
          <div class="section-heading">
            <h3>目录</h3>
            <button class="secondary-action compact-tool-button" type="button" @click="appendChapter">新增章节</button>
          </div>
          <button
            v-for="item in articleOutline"
            :key="item.id"
            type="button"
            :class="{ selected: selectedHeading === item.id }"
            @click="selectedHeading = item.id"
          >
            <span :style="{ paddingLeft: `${(item.level - 1) * 10}px` }">{{ item.title }}</span>
          </button>
          <p v-if="!articleOutline.length">在正文里输入 `#` 或 `##` 标题后，这里会自动生成目录。</p>
        </aside>

        <main class="article-editor-canvas">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Writer</p>
              <h3>写文章</h3>
            </div>
            <div class="knowledge-actions">
              <span>{{ articleStatus }}</span>
              <button type="submit">Save Article</button>
            </div>
          </div>

          <input v-model="articleForm.title" class="article-title-input" required placeholder="输入文章标题" />

          <div class="article-inline-toolbar" aria-label="写作工具栏">
            <button class="icon-tool-button" title="正文段落" type="button" @mousedown.prevent="insertParagraph">P</button>
            <button class="icon-tool-button" title="二级标题" type="button" @mousedown.prevent="insertHeading">H2</button>
            <button class="icon-tool-button" title="图片" type="button" @mousedown.prevent="openImagePicker">Img</button>
            <button class="icon-tool-button" title="表格" type="button" @mousedown.prevent="insertTable()">Grid</button>
            <button class="icon-tool-button" title="代码块" type="button" @mousedown.prevent="insertCodeBlock">Code</button>
            <span class="toolbar-divider" aria-hidden="true"></span>
            <button class="icon-tool-button" title="左对齐" type="button" @mousedown.prevent="alignSelection('left')">L</button>
            <button class="icon-tool-button" title="居中" type="button" @mousedown.prevent="alignSelection('center')">C</button>
            <button class="icon-tool-button" title="右对齐" type="button" @mousedown.prevent="alignSelection('right')">R</button>
            <button class="icon-tool-button wide-icon-tool" title="向右合并表格单元格" type="button" @mousedown.prevent="mergeTableCellRight">Merge</button>
          </div>
          <input ref="imageInputRef" class="visually-hidden" type="file" accept="image/*" @change="insertSelectedImage" />

          <div
            ref="editorRef"
            class="article-rich-editor"
            contenteditable="true"
            data-placeholder="像写文档一样写正文。代码块、图片、表格会插入到光标所在位置。"
            @blur="syncArticleContent"
            @input="syncArticleContent"
            @keyup="rememberSelection"
            @mouseup="rememberSelection"
            @paste="handleEditorPaste"
          >
          </div>
        </main>
      </form>
    </div>

    <div v-else class="knowledge-state">Loading Tech Stack detail...</div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createWorkArticle, deleteTechStack, fetchTechStackDetail, updateTechStack } from '../../../services/api'

const route = useRoute()
const router = useRouter()
const detail = ref<any | null>(null)
const articleStatus = ref('Draft is local until saved.')
const stackStatus = ref('Update name, category, proficiency, tags or description.')
const stackTagsText = ref('')
const showStackEditor = ref(false)
const selectedHeading = ref('')
const editorRef = ref<HTMLElement | null>(null)
const imageInputRef = ref<HTMLInputElement | null>(null)
const savedRange = ref<Range | null>(null)
const articleForm = ref({
  title: '',
  contentHtml: '',
})
const stackForm = ref({
  name: '',
  category: '',
  proficiency: 'learning',
  description: '',
})
const stackTags = computed(() => splitTags(stackTagsText.value))
const articleOutline = computed(() =>
  Array.from(editorRef.value?.querySelectorAll('h1, h2, h3') || []).map((heading, index) => ({
    id: `heading-${index}`,
    level: Number(heading.tagName.slice(1)),
    title: heading.textContent?.trim() || '未命名章节',
  })),
)

onMounted(async () => {
  await loadDetail()
})

async function loadDetail() {
  const rawDetail = await fetchTechStackDetail(String(route.params.techStackId))
  detail.value = {
    ...rawDetail,
    relatedKnowledge: Array.isArray(rawDetail.relatedKnowledge) ? rawDetail.relatedKnowledge : [],
    projects: Array.isArray(rawDetail.projects) ? rawDetail.projects : [],
    articles: Array.isArray(rawDetail.articles) ? rawDetail.articles : [],
    learningRecords: Array.isArray(rawDetail.learningRecords) ? rawDetail.learningRecords : [],
    resumeSnippets: Array.isArray(rawDetail.resumeSnippets) ? rawDetail.resumeSnippets : [],
  }
  stackForm.value = {
    name: detail.value.techStack.name,
    category: detail.value.techStack.category,
    proficiency: detail.value.techStack.proficiency,
    description: detail.value.techStack.description,
  }
  stackTagsText.value = (detail.value.techStack.tags || []).join(', ')
}

async function submitStackUpdate() {
  detail.value.techStack = await updateTechStack(String(route.params.techStackId), {
    ...stackForm.value,
    tags: stackTags.value,
  })
  stackStatus.value = 'Tech Stack updated.'
  await loadDetail()
}

async function archiveStack() {
  if (!window.confirm('Archive this Tech Stack? Articles remain as history, but the stack will leave the active directory.')) {
    return
  }
  await deleteTechStack(String(route.params.techStackId))
  await router.push('/work/tech-stack')
}

async function submitArticle() {
  syncArticleContent()
  const content = composeArticleContent()
  await createWorkArticle(String(route.params.techStackId), {
    title: articleForm.value.title,
    articleType: 'knowledge',
    summary: firstParagraph(editorRef.value?.innerText || ''),
    content: `<h1>${escapeHtml(articleForm.value.title)}</h1>\n${content}`.trim(),
    tags: stackTags.value,
  })
  articleStatus.value = 'Article saved.'
  articleForm.value = { title: '', contentHtml: '' }
  if (editorRef.value) {
    editorRef.value.innerHTML = ''
  }
  selectedHeading.value = ''
  await loadDetail()
}

function appendChapter() {
  insertHeading(`第 ${articleOutline.value.length + 1} 章`)
}

function insertParagraph() {
  insertHtmlAtCursor('<p><br></p>')
}

function insertHeading(title = '新章节') {
  insertHtmlAtCursor(`<h2>${escapeHtml(title)}</h2><p><br></p>`)
}

function openImagePicker() {
  rememberSelection()
  imageInputRef.value?.click()
}

async function insertSelectedImage(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) {
    return
  }
  insertImage(await readImageAsDataUrl(file), file.name || '图片说明')
  input.value = ''
}

function insertImage(url: string, alt = '图片说明') {
  insertHtmlAtCursor(
    `<figure class="article-image-fragment"><img src="${escapeAttribute(url)}" alt="${escapeAttribute(
      alt,
    )}"><figcaption>${escapeHtml(alt)}</figcaption></figure><p><br></p>`,
  )
  articleStatus.value = 'Image inserted into article body.'
}

function insertTable(rows?: string[][]) {
  const sourceRows = rows || [
    ['', '', ''],
    ['', '', ''],
    ['', '', ''],
  ]
  const body = sourceRows
    .map(
      (row) =>
        `<tr>${row
          .map((cell) => `<td contenteditable="true">${escapeHtml(cell || '')}</td>`)
          .join('')}</tr>`,
    )
    .join('')
  insertHtmlAtCursor(`<table class="article-table-fragment"><tbody>${body}</tbody></table><p><br></p>`)
  articleStatus.value = 'Table inserted into article body.'
}

function insertCodeBlock() {
  insertHtmlAtCursor(
    '<pre class="article-code-fragment"><code contenteditable="true">plain text</code></pre><p><br></p>',
  )
  articleStatus.value = 'Code block inserted into article body.'
}

function alignSelection(align: 'left' | 'center' | 'right') {
  restoreSelection()
  const cell = closestSelectedElement('td')
  if (cell) {
    ;(cell as HTMLElement).style.textAlign = align
    syncArticleContent()
    return
  }
  const command = align === 'left' ? 'justifyLeft' : align === 'center' ? 'justifyCenter' : 'justifyRight'
  document.execCommand(command)
  syncArticleContent()
}

function mergeTableCellRight() {
  restoreSelection()
  const cell = closestSelectedElement('td') as HTMLTableCellElement | null
  if (!cell) {
    articleStatus.value = 'Place cursor inside a table cell before merging.'
    return
  }
  const next = cell.nextElementSibling as HTMLTableCellElement | null
  if (!next || next.tagName.toLowerCase() !== 'td') {
    articleStatus.value = 'No right-side cell to merge.'
    return
  }
  cell.colSpan += next.colSpan || 1
  next.remove()
  syncArticleContent()
  articleStatus.value = 'Table cell merged.'
}

async function handleEditorPaste(event: ClipboardEvent) {
  rememberSelection()
  const items = Array.from(event.clipboardData?.items || [])
  const imageItems = items.filter((item) => item.type.startsWith('image/'))
  if (imageItems.length) {
    event.preventDefault()
    for (const item of imageItems) {
      const file = item.getAsFile()
      if (file) {
        insertImage(await readImageAsDataUrl(file), file.name || 'pasted-image')
      }
    }
    return
  }

  const text = event.clipboardData?.getData('text/plain') || ''
  if (looksLikeTable(text)) {
    event.preventDefault()
    insertTable(parsePastedTable(text))
    return
  }

  window.setTimeout(syncArticleContent)
}

function rememberSelection() {
  const selection = window.getSelection()
  if (!selection || !selection.rangeCount || !editorRef.value) {
    return
  }
  const range = selection.getRangeAt(0)
  if (editorRef.value.contains(range.commonAncestorContainer)) {
    savedRange.value = range.cloneRange()
  }
}

function restoreSelection() {
  if (!editorRef.value) {
    return
  }
  editorRef.value.focus()
  const selection = window.getSelection()
  if (!selection) {
    return
  }
  selection.removeAllRanges()
  if (savedRange.value) {
    selection.addRange(savedRange.value)
    return
  }
  const range = document.createRange()
  range.selectNodeContents(editorRef.value)
  range.collapse(false)
  selection.addRange(range)
}

function insertHtmlAtCursor(html: string) {
  restoreSelection()
  const selection = window.getSelection()
  if (!selection || !selection.rangeCount || !editorRef.value) {
    return
  }
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
  syncArticleContent()
}

function closestSelectedElement(selector: string) {
  const selection = window.getSelection()
  if (!selection || !selection.rangeCount || !editorRef.value) {
    return null
  }
  let node: Node | null = selection.getRangeAt(0).startContainer
  if (node.nodeType === Node.TEXT_NODE) {
    node = node.parentElement
  }
  const element = node as Element | null
  const found = element?.closest(selector) || null
  return found && editorRef.value.contains(found) ? found : null
}

function readImageAsDataUrl(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

function looksLikeTable(text: string) {
  const lines = text.trim().split(/\r?\n/).filter(Boolean)
  return lines.length >= 2 && lines.every((line) => line.includes('\t'))
}

function parsePastedTable(text: string) {
  const rows = text
    .trim()
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => line.split('\t').map((cell) => cell.trim()))
  const columnCount = Math.max(...rows.map((row) => row.length))
  return rows.map((row) => [...row, ...Array(columnCount - row.length).fill('')])
}

function composeArticleContent() {
  syncArticleContent()
  return articleForm.value.contentHtml
}

function syncArticleContent() {
  articleForm.value.contentHtml = editorRef.value?.innerHTML || ''
}

function firstParagraph(value: string) {
  return (
    value
      .split('\n')
      .map((line) => line.replace(/^#{1,6}\s+/, '').trim())
      .find(Boolean) || ''
  )
}

function splitTags(value: string) {
  return value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

function escapeHtml(value: string) {
  const container = document.createElement('div')
  container.textContent = value
  return container.innerHTML
}

function escapeAttribute(value: string) {
  return escapeHtml(value).replace(/"/g, '&quot;')
}
</script>
