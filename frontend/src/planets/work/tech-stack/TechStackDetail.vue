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
            <button class="secondary-action" type="button" @click="appendChapter">新增章节</button>
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
          <textarea
            v-model="articleForm.content"
            class="article-body-editor"
            rows="28"
            placeholder="# 第一章&#10;&#10;像写小说一样写文章。用 # / ## 标题自然形成左侧目录。"
          />
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
const articleForm = ref({
  title: '',
  content: '',
})
const stackForm = ref({
  name: '',
  category: '',
  proficiency: 'learning',
  description: '',
})
const stackTags = computed(() => splitTags(stackTagsText.value))
const articleOutline = computed(() =>
  articleForm.value.content
    .split('\n')
    .map((line, index) => {
      const match = line.match(/^(#{1,3})\s+(.+)$/)
      if (!match) {
        return null
      }
      return {
        id: `heading-${index}`,
        level: match[1].length,
        title: match[2].trim(),
      }
    })
    .filter(Boolean) as Array<{ id: string; level: number; title: string }>,
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
    summary: firstParagraph(articleForm.value.content),
    content: `# ${articleForm.value.title}\n\n${articleForm.value.content}`.trim(),
    tags: stackTags.value,
  })
  articleStatus.value = 'Article saved.'
  articleForm.value = { title: '', content: '' }
  selectedHeading.value = ''
  await loadDetail()
}

function appendChapter() {
  const chapterNumber = articleOutline.value.length + 1
  articleForm.value.content = `${articleForm.value.content.trim()}\n\n## 第 ${chapterNumber} 章\n\n`.trimStart()
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
</script>
