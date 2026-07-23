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

      <div class="progress-snapshot">
        <article>
          <strong>{{ detail.relatedKnowledge.length }}</strong>
          <span>Work Knowledge</span>
        </article>
        <article>
          <strong>{{ detail.projects.length }}</strong>
          <span>Projects</span>
        </article>
        <article>
          <strong>{{ detail.articles.length }}</strong>
          <span>Articles</span>
        </article>
        <article>
          <strong>{{ detail.learningRecords.length }}</strong>
          <span>Learning Records</span>
        </article>
      </div>

      <section class="home-section">
        <div class="section-heading">
          <div>
            <h3>写文章</h3>
            <span>按大纲和章节沉淀知识、笔记、代码与图表</span>
          </div>
          <button class="secondary-action" type="button" @click="showArticleEditor = !showArticleEditor">
            {{ showArticleEditor ? 'Close Writer' : 'Create Article' }}
          </button>
        </div>
        <form v-if="showArticleEditor" class="study-form article-editor-form" @submit.prevent="submitArticle">
          <label>
            标题
            <input v-model="articleForm.title" required placeholder="FastAPI 权限系统实践" />
          </label>
          <label>
            标签
            <input v-model="articleTagsText" placeholder="backend, auth, project" />
          </label>
          <label>
            类型
            <select v-model="articleForm.articleType">
              <option value="knowledge">知识</option>
              <option value="note">笔记</option>
            </select>
          </label>
          <label class="wide-field">
            摘要
            <input v-model="articleForm.summary" placeholder="这篇文章解决什么问题" />
          </label>
          <label class="wide-field">
            大纲
            <textarea v-model="articleForm.outline" rows="4" placeholder="- 背景&#10;- 核心概念&#10;- 实战步骤&#10;- 常见问题" />
          </label>
          <div class="wide-field article-builder">
            <div class="section-heading">
              <h4>章节</h4>
              <button class="secondary-action" type="button" @click="addChapter">Add Chapter</button>
            </div>
            <div class="markdown-toolbar" aria-label="Markdown insert toolbar">
              <button type="button" @click="insertBlock('table')">插入表格</button>
              <button type="button" @click="insertBlock('image')">插入图片</button>
              <button type="button" @click="insertBlock('code')">插入代码块</button>
              <button type="button" @click="insertBlock('section')">插入小节</button>
            </div>
            <article v-for="(chapter, index) in articleForm.chapters" :key="chapter.id" class="chapter-editor">
              <div class="section-heading">
                <label>
                  章节标题
                  <input v-model="chapter.title" @focus="selectedChapterIndex = index" />
                </label>
                <button class="secondary-action" type="button" @click="removeChapter(index)">Remove</button>
              </div>
              <textarea
                v-model="chapter.body"
                rows="8"
                placeholder="写正文。可以用 Markdown 表格、图片、代码块。"
                @focus="selectedChapterIndex = index"
              />
            </article>
          </div>
          <label class="wide-field">
            附加内容
            <textarea v-model="articleForm.content" rows="5" placeholder="补充结论、参考链接或临时片段" />
          </label>
          <div class="wide-field article-preview">
            <div class="section-heading">
              <h4>文章预览</h4>
              <span>Markdown source</span>
            </div>
            <pre>{{ composedArticle }}</pre>
          </div>
          <div class="knowledge-actions">
            <button type="submit">Save Article</button>
            <span>{{ articleStatus }}</span>
          </div>
        </form>
      </section>

      <section class="home-section">
        <div class="section-heading">
          <h3>学习记录</h3>
          <span>记录今天推进了什么</span>
        </div>
        <form class="study-form" @submit.prevent="submitLearningRecord">
          <label>
            记录标题
            <input v-model="recordForm.title" required placeholder="阅读 FastAPI dependency 文档" />
          </label>
          <label>
            分钟
            <input v-model.number="recordForm.minutes" min="0" type="number" />
          </label>
          <label>
            标签
            <input v-model="recordTagsText" placeholder="reading, source-code, bugfix" />
          </label>
          <label class="wide-field">
            笔记
            <textarea v-model="recordForm.notes" rows="4" placeholder="记录学习过程、问题和下一步" />
          </label>
          <div class="knowledge-actions">
            <button type="submit">Save Record</button>
            <span>{{ recordStatus }}</span>
          </div>
        </form>
      </section>

      <section class="home-section">
        <h3>文章与学习记录</h3>
        <div v-if="detail.articles.length || detail.learningRecords.length" class="tech-feed">
          <article v-for="article in detail.articles" :key="article.id" class="tech-feed-item content-feed-item">
            <div>
              <span class="status-pill">{{ article.articleType === 'note' ? '笔记' : '知识' }}</span>
              <h3>{{ article.title }}</h3>
              <p>{{ article.summary || article.content }}</p>
              <pre class="article-content-preview">{{ article.content }}</pre>
              <div class="tech-tag-row">
                <span v-for="tag in article.tags || []" :key="tag">{{ tag }}</span>
                <span v-if="!(article.tags || []).length">No tags yet</span>
              </div>
            </div>
          </article>
          <article v-for="record in detail.learningRecords" :key="record.id" class="tech-feed-item content-feed-item">
            <div>
              <span class="status-pill">Learning Record</span>
              <h3>{{ record.title }}</h3>
              <p>{{ record.notes }}</p>
              <div class="tech-meta-row">
                <span>{{ record.minutes }} min</span>
                <span>{{ record.status }}</span>
              </div>
              <div class="tech-tag-row">
                <span v-for="tag in record.tags || []" :key="tag">{{ tag }}</span>
                <span v-if="!(record.tags || []).length">No tags yet</span>
              </div>
            </div>
          </article>
        </div>
        <div v-else class="knowledge-state">还没有文章或学习记录。先写一篇短文章，或记录今天的一次推进。</div>
      </section>

      <section class="home-section">
        <h3>Work Knowledge</h3>
        <div v-if="detail.relatedKnowledge.length" class="goal-list">
          <article v-for="document in detail.relatedKnowledge" :key="document.id" class="knowledge-document">
            <span class="status-pill">{{ document.goalId ? 'Study reference' : 'Work Knowledge' }}</span>
            <h3>{{ document.fileName }}</h3>
            <p class="surface-copy">{{ document.subject }} / {{ document.topic }}</p>
          </article>
        </div>
        <div v-else class="knowledge-state">
          No related Work Knowledge yet. Add Work Knowledge or reference matching Study Knowledge by subject, topic, or tags.
        </div>
        <RouterLink class="secondary-action" to="/work/knowledge">Open Work Knowledge</RouterLink>
      </section>
    </div>
    <div v-else class="knowledge-state">Loading Tech Stack detail...</div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  createWorkArticle,
  createWorkLearningRecord,
  deleteTechStack,
  fetchTechStackDetail,
  updateTechStack,
} from '../../../services/api'

const route = useRoute()
const router = useRouter()
const detail = ref<any | null>(null)
const articleStatus = ref('Draft an article under this Tech Stack.')
const recordStatus = ref('Record learning progress under this Tech Stack.')
const stackStatus = ref('Update name, category, proficiency, tags or description.')
const articleTagsText = ref('')
const recordTagsText = ref('')
const stackTagsText = ref('')
const showArticleEditor = ref(true)
const showStackEditor = ref(false)
const selectedChapterIndex = ref(0)
const articleForm = ref({
  title: '',
  articleType: 'knowledge',
  summary: '',
  outline: '',
  chapters: [{ id: 'chapter-1', title: '第一章', body: '' }],
  content: '',
})
const recordForm = ref({
  title: '',
  minutes: 30,
  notes: '',
})
const stackForm = ref({
  name: '',
  category: '',
  proficiency: 'learning',
  description: '',
})
const articleTags = computed(() => splitTags(articleTagsText.value))
const recordTags = computed(() => splitTags(recordTagsText.value))
const stackTags = computed(() => splitTags(stackTagsText.value))
const composedArticle = computed(() => composeArticleContent())

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
  if (!window.confirm('Archive this Tech Stack? Articles and records remain as history, but the stack will leave the active directory.')) {
    return
  }
  await deleteTechStack(String(route.params.techStackId))
  await router.push('/work/tech-stack')
}

async function submitArticle() {
  await createWorkArticle(String(route.params.techStackId), {
    ...articleForm.value,
    tags: articleTags.value,
    content: composedArticle.value,
  })
  articleStatus.value = 'Article saved.'
  articleForm.value = {
    title: '',
    articleType: 'knowledge',
    summary: '',
    outline: '',
    chapters: [{ id: `chapter-${Date.now()}`, title: '第一章', body: '' }],
    content: '',
  }
  articleTagsText.value = ''
  await loadDetail()
}

async function submitLearningRecord() {
  await createWorkLearningRecord(String(route.params.techStackId), {
    ...recordForm.value,
    tags: recordTags.value,
  })
  recordStatus.value = 'Learning record saved.'
  recordForm.value = { title: '', minutes: 30, notes: '' }
  recordTagsText.value = ''
  await loadDetail()
}

function splitTags(value: string) {
  return value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

function addChapter() {
  articleForm.value.chapters.push({
    id: `chapter-${Date.now()}`,
    title: `第 ${articleForm.value.chapters.length + 1} 章`,
    body: '',
  })
  selectedChapterIndex.value = articleForm.value.chapters.length - 1
}

function removeChapter(index: number) {
  if (articleForm.value.chapters.length === 1) {
    articleForm.value.chapters[0].body = ''
    articleForm.value.chapters[0].title = '第一章'
    return
  }
  articleForm.value.chapters.splice(index, 1)
  selectedChapterIndex.value = Math.max(0, selectedChapterIndex.value - 1)
}

function insertBlock(kind: 'table' | 'image' | 'code' | 'section') {
  const snippets = {
    table: '\n\n| 字段 | 说明 | 示例 |\n| --- | --- | --- |\n| name | 技术点 | Java Stream |\n',
    image: '\n\n![图片说明](https://example.com/image.png)\n',
    code: '\n\n```ts\n// 在这里写代码\nfunction example() {\n  return true\n}\n```\n',
    section: '\n\n### 小节标题\n\n这里写这个小节的核心内容。\n',
  }
  const chapter = articleForm.value.chapters[selectedChapterIndex.value] || articleForm.value.chapters[0]
  chapter.body = `${chapter.body}${snippets[kind]}`
}

function composeArticleContent() {
  const blocks = []
  if (articleForm.value.outline.trim()) {
    blocks.push(`## 大纲\n\n${articleForm.value.outline.trim()}`)
  }
  articleForm.value.chapters.forEach((chapter, index) => {
    const title = chapter.title.trim() || `章节 ${index + 1}`
    blocks.push(`## ${title}\n\n${chapter.body.trim()}`)
  })
  if (articleForm.value.content.trim()) {
    blocks.push(articleForm.value.content.trim())
  }
  return blocks.filter(Boolean).join('\n\n')
}
</script>
