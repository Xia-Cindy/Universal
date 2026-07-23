<template>
  <section class="study-plan" aria-labelledby="tech-stack-detail-title">
    <RouterLink class="secondary-action" to="/work/tech-stack">Back to Tech Stack</RouterLink>
    <div v-if="detail" class="home-section">
      <p class="eyebrow">Tech Stack Detail</p>
      <h2 id="tech-stack-detail-title">{{ detail.techStack.name }}</h2>
      <p class="surface-copy">{{ detail.techStack.description || detail.techStack.category }}</p>

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
          <h3>写文章</h3>
          <span>输出技术理解，沉淀为作品证据</span>
        </div>
        <form class="study-form" @submit.prevent="submitArticle">
          <label>
            标题
            <input v-model="articleForm.title" required placeholder="FastAPI 权限系统实践" />
          </label>
          <label>
            标签
            <input v-model="articleTagsText" placeholder="backend, auth, project" />
          </label>
          <label class="wide-field">
            摘要
            <input v-model="articleForm.summary" placeholder="这篇文章解决什么问题" />
          </label>
          <label class="wide-field">
            正文
            <textarea v-model="articleForm.content" rows="6" placeholder="写下技术背景、方案、踩坑、结论" />
          </label>
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
              <span class="status-pill">Article</span>
              <h3>{{ article.title }}</h3>
              <p>{{ article.summary || article.content }}</p>
              <div class="tech-tag-row">
                <span v-for="tag in article.tags" :key="tag">{{ tag }}</span>
                <span v-if="!article.tags.length">No tags yet</span>
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
                <span v-for="tag in record.tags" :key="tag">{{ tag }}</span>
                <span v-if="!record.tags.length">No tags yet</span>
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
import { useRoute } from 'vue-router'
import { createWorkArticle, createWorkLearningRecord, fetchTechStackDetail } from '../../../services/api'

const route = useRoute()
const detail = ref<any | null>(null)
const articleStatus = ref('Draft an article under this Tech Stack.')
const recordStatus = ref('Record learning progress under this Tech Stack.')
const articleTagsText = ref('')
const recordTagsText = ref('')
const articleForm = ref({
  title: '',
  summary: '',
  content: '',
})
const recordForm = ref({
  title: '',
  minutes: 30,
  notes: '',
})
const articleTags = computed(() => splitTags(articleTagsText.value))
const recordTags = computed(() => splitTags(recordTagsText.value))

onMounted(async () => {
  await loadDetail()
})

async function loadDetail() {
  detail.value = await fetchTechStackDetail(String(route.params.techStackId))
}

async function submitArticle() {
  await createWorkArticle(String(route.params.techStackId), {
    ...articleForm.value,
    tags: articleTags.value,
  })
  articleStatus.value = 'Article saved.'
  articleForm.value = { title: '', summary: '', content: '' }
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
</script>
