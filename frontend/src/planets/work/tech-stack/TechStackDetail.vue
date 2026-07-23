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

          <div class="article-block-stack">
            <section v-for="block in articleForm.blocks" :key="block.id" class="article-block">
              <textarea
                v-if="block.kind === 'text'"
                v-model="block.content"
                class="article-body-editor"
                rows="10"
                placeholder="# 第一章&#10;&#10;像写小说一样写文章。用 # / ## 标题自然形成左侧目录。"
                @focus="activeBlockId = block.id"
                @paste="handleEditorPaste($event, block.id)"
              />

              <div v-else-if="block.kind === 'table'" class="article-table-block">
                <div class="article-block-toolbar">
                  <strong>表格</strong>
                  <button class="compact-tool-button" type="button" @click="addTableRow(block)">加行</button>
                  <button class="compact-tool-button" type="button" @click="addTableColumn(block)">加列</button>
                  <button class="compact-tool-button" type="button" @click="removeBlock(block.id)">删除</button>
                </div>
                <table>
                  <tbody>
                    <tr v-for="(row, rowIndex) in block.rows" :key="rowIndex">
                      <td v-for="(cell, columnIndex) in row" :key="columnIndex">
                        <input v-model="row[columnIndex]" />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div v-else-if="block.kind === 'code'" class="article-code-block">
                <div class="article-block-toolbar">
                  <strong>代码块</strong>
                  <input v-model="block.language" placeholder="plain text" />
                  <button class="compact-tool-button" type="button" @click="removeBlock(block.id)">删除</button>
                </div>
                <textarea v-model="block.content" rows="8" placeholder="在这里写代码或 plain text。" />
              </div>

              <div v-else class="article-image-block">
                <div class="article-block-toolbar">
                  <strong>图片</strong>
                  <button class="compact-tool-button" type="button" @click="removeBlock(block.id)">删除</button>
                </div>
                <input v-model="block.alt" placeholder="图片说明" />
                <input v-model="block.url" placeholder="图片地址，或直接粘贴图片到正文" />
                <img v-if="block.url" :alt="block.alt" :src="block.url" />
              </div>
            </section>
          </div>
        </main>

        <aside class="article-tool-panel" aria-label="写作工具">
          <p class="eyebrow">Tools</p>
          <h3>写作工具</h3>
          <button class="compact-tool-button" type="button" @click="addTextBlock">文本</button>
          <button class="compact-tool-button" type="button" @click="addImageBlock()">图片</button>
          <button class="compact-tool-button" type="button" @click="addTableBlock()">表格</button>
          <button class="compact-tool-button" type="button" @click="addCodeBlock">代码块</button>
          <p>粘贴图片会生成图片块；粘贴 Excel 单元格会生成表格块。</p>
        </aside>
      </form>
    </div>

    <div v-else class="knowledge-state">Loading Tech Stack detail...</div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createWorkArticle, deleteTechStack, fetchTechStackDetail, updateTechStack } from '../../../services/api'

type TextBlock = {
  id: string
  kind: 'text'
  content: string
}

type TableBlock = {
  id: string
  kind: 'table'
  rows: string[][]
}

type CodeBlock = {
  id: string
  kind: 'code'
  language: string
  content: string
}

type ImageBlock = {
  id: string
  kind: 'image'
  alt: string
  url: string
}

type ArticleBlock = TextBlock | TableBlock | CodeBlock | ImageBlock

const route = useRoute()
const router = useRouter()
const detail = ref<any | null>(null)
const articleStatus = ref('Draft is local until saved.')
const stackStatus = ref('Update name, category, proficiency, tags or description.')
const stackTagsText = ref('')
const showStackEditor = ref(false)
const selectedHeading = ref('')
const activeBlockId = ref('')
const articleForm = ref({
  title: '',
  blocks: [createTextBlock('')],
})
const stackForm = ref({
  name: '',
  category: '',
  proficiency: 'learning',
  description: '',
})
const stackTags = computed(() => splitTags(stackTagsText.value))
const articleOutline = computed(() =>
  articleForm.value.blocks.flatMap((block, blockIndex) => {
    if (block.kind !== 'text') {
      return []
    }
    return block.content
      .split('\n')
      .map((line, lineIndex) => {
        const match = line.match(/^(#{1,3})\s+(.+)$/)
        if (!match) {
          return null
        }
        return {
          id: `heading-${blockIndex}-${lineIndex}`,
          level: match[1].length,
          title: match[2].trim(),
        }
      })
      .filter(Boolean) as Array<{ id: string; level: number; title: string }>
  }),
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
  await createWorkArticle(String(route.params.techStackId), {
    title: articleForm.value.title,
    articleType: 'knowledge',
    summary: firstParagraph(composeArticleContent()),
    content: `# ${articleForm.value.title}\n\n${composeArticleContent()}`.trim(),
    tags: stackTags.value,
  })
  articleStatus.value = 'Article saved.'
  articleForm.value = { title: '', blocks: [createTextBlock('')] }
  selectedHeading.value = ''
  await loadDetail()
}

function appendChapter() {
  const block = activeTextBlock()
  block.content = `${block.content.trim()}\n\n## 第 ${articleOutline.value.length + 1} 章\n\n`.trimStart()
}

function addTextBlock(content = '') {
  const block = createTextBlock(content)
  articleForm.value.blocks.push(block)
  activeBlockId.value = block.id
}

function addTableBlock(rows?: string[][]) {
  articleForm.value.blocks.push({
    id: createId('table'),
    kind: 'table',
    rows: rows || [
      ['', '', ''],
      ['', '', ''],
      ['', '', ''],
    ],
  })
}

function addCodeBlock() {
  articleForm.value.blocks.push({
    id: createId('code'),
    kind: 'code',
    language: '',
    content: '',
  })
}

function addImageBlock(url = '', alt = '图片说明') {
  articleForm.value.blocks.push({
    id: createId('image'),
    kind: 'image',
    alt,
    url,
  })
}

function removeBlock(blockId: string) {
  if (articleForm.value.blocks.length === 1) {
    articleForm.value.blocks = [createTextBlock('')]
    return
  }
  articleForm.value.blocks = articleForm.value.blocks.filter((block) => block.id !== blockId)
}

function addTableRow(block: TableBlock) {
  const columnCount = block.rows[0]?.length || 3
  block.rows.push(Array(columnCount).fill(''))
}

function addTableColumn(block: TableBlock) {
  block.rows.forEach((row) => row.push(''))
}

async function handleEditorPaste(event: ClipboardEvent, blockId: string) {
  activeBlockId.value = blockId
  const items = Array.from(event.clipboardData?.items || [])
  const imageItems = items.filter((item) => item.type.startsWith('image/'))
  if (imageItems.length) {
    event.preventDefault()
    for (const item of imageItems) {
      const file = item.getAsFile()
      if (file) {
        addImageBlock(await readImageAsDataUrl(file), file.name || 'pasted-image')
      }
    }
    articleStatus.value = 'Image pasted into article.'
    return
  }

  const text = event.clipboardData?.getData('text/plain') || ''
  if (looksLikeTable(text)) {
    event.preventDefault()
    addTableBlock(parsePastedTable(text))
    articleStatus.value = 'Table pasted into article.'
  }
}

function activeTextBlock() {
  const found = articleForm.value.blocks.find(
    (block): block is TextBlock => block.id === activeBlockId.value && block.kind === 'text',
  )
  if (found) {
    return found
  }
  const existing = articleForm.value.blocks.find((block): block is TextBlock => block.kind === 'text')
  if (existing) {
    activeBlockId.value = existing.id
    return existing
  }
  const created = createTextBlock('')
  articleForm.value.blocks.unshift(created)
  activeBlockId.value = created.id
  return created
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
  return articleForm.value.blocks
    .map((block) => {
      if (block.kind === 'text') {
        return block.content.trim()
      }
      if (block.kind === 'table') {
        return block.rows.map((row) => row.join('\t')).join('\n')
      }
      if (block.kind === 'code') {
        return `Code block${block.language ? ` (${block.language})` : ''}:\n${block.content}`
      }
      return `Image: ${block.alt}\n${block.url}`
    })
    .filter(Boolean)
    .join('\n\n')
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

function createTextBlock(content: string): TextBlock {
  return {
    id: createId('text'),
    kind: 'text',
    content,
  }
}

function createId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`
}
</script>
