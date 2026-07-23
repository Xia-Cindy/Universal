<template>
  <section class="tech-nav-page" aria-labelledby="tech-stack-title">
    <header class="tech-nav-hero">
      <div>
        <p class="eyebrow">Tech Stack</p>
        <h2 id="tech-stack-title">技术栈目录</h2>
        <p class="surface-copy">像浏览技术频道一样管理能力：分类、技术栈、文章、笔记和社区动态都从这里进入。</p>
      </div>
      <button type="button" @click="showCreate = true">Add Tech Stack</button>
    </header>

    <div v-if="showCreate" class="modal-backdrop" role="presentation" @click.self="showCreate = false">
      <form class="modal-panel tech-create-modal" @submit.prevent="submitTechStack">
        <div class="section-heading">
          <div>
            <p class="eyebrow">New Tech Stack</p>
            <h3>创建技术栈</h3>
          </div>
          <button class="secondary-action" type="button" @click="showCreate = false">Close</button>
        </div>
        <label>
          技术名称
          <input v-model="form.name" required placeholder="Java" />
        </label>
        <label>
          分类
          <input v-model="form.category" required placeholder="Backend" />
        </label>
        <div class="knowledge-actions">
          <button type="submit">Create</button>
          <span>{{ status }}</span>
        </div>
      </form>
    </div>

    <div class="tech-channel-tabs" aria-label="Tech stack categories">
      <button
        v-for="channel in categoryTabs"
        :key="channel.id"
        type="button"
        :class="{ selected: selectedCategory === channel.id }"
        @click="selectCategory(channel.id)"
      >
        {{ channel.label }}
      </button>
    </div>

    <div v-if="selectedCategory !== 'community'" class="tech-topic-tabs" aria-label="Tech stacks in category">
      <button
        v-for="stack in stackTabs"
        :key="stack.id"
        type="button"
        :class="{ selected: selectedStackId === stack.id }"
        @click="selectedStackId = stack.id"
      >
        {{ stack.label }}
      </button>
    </div>

    <div v-if="selectedCategory === 'community'" class="tech-nav-layout">
      <aside class="tech-directory-panel" aria-label="Community source">
        <strong>社区来源</strong>
        <span>CSDN</span>
        <small>{{ communityTopic }} · Top 30</small>
      </aside>

      <div class="tech-feed">
        <section class="tech-content-stream" aria-labelledby="community-title">
          <div class="section-heading">
            <h3 id="community-title">CSDN 社区热文</h3>
            <a class="secondary-action" :href="community.url" rel="noreferrer" target="_blank">Open CSDN</a>
          </div>
          <div v-if="isCommunityLoading" class="knowledge-state">Loading CSDN community articles...</div>
          <template v-else>
            <article v-for="article in community.articles" :key="article.url + article.title" class="tech-feed-item content-feed-item">
              <div>
                <span class="status-pill">{{ article.source }}</span>
                <h3>{{ article.title }}</h3>
                <p>{{ article.summary || '来自 CSDN 技术社区的文章，可用于了解相关技术动态。' }}</p>
              </div>
              <a class="secondary-action" :href="article.url" rel="noreferrer" target="_blank">Read</a>
            </article>
          </template>
        </section>
      </div>

      <aside class="tech-evidence-panel">
        <p class="eyebrow">Community</p>
        <strong>只做资讯参考</strong>
        <p>社区文章不会自动进入 Work Knowledge；需要你确认后再上传或写成自己的知识/笔记。</p>
      </aside>
    </div>

    <div v-else-if="techStacks.length" class="tech-nav-layout">
      <aside class="tech-directory-panel" aria-label="Tech stack directory">
        <strong>技术目录</strong>
        <button
          v-for="stack in visibleTechStacks"
          :key="stack.id"
          type="button"
          :class="{ selected: selectedStackId === stack.id }"
          @click="selectedStackId = stack.id"
        >
          <span>{{ stack.name }}</span>
          <small>{{ stack.category }}</small>
        </button>
      </aside>

      <div class="tech-feed">
        <article v-for="stack in visibleTechStacks" :key="stack.id" class="tech-feed-item">
          <div class="tech-feed-main">
            <span class="status-pill">{{ stack.proficiency }}</span>
            <h3>{{ stack.name }}</h3>
            <p>{{ stack.description || '补充这个技术栈的学习资料、项目证据和简历表达。' }}</p>
            <div class="tech-meta-row">
              <span>{{ stack.category }}</span>
              <span>{{ stack.tags.length }} tags</span>
              <span>{{ stack.status }}</span>
            </div>
            <div class="tech-tag-row">
              <span v-for="tag in stack.tags" :key="tag">{{ tag }}</span>
              <span v-if="!stack.tags.length">No tags yet</span>
            </div>
          </div>
          <RouterLink class="secondary-action" :to="`/work/tech-stack/${stack.id}`">Open Stack</RouterLink>
        </article>

        <section class="tech-content-stream" aria-labelledby="tech-content-title">
          <div class="section-heading">
            <h3 id="tech-content-title">技术内容流</h3>
            <span>{{ visibleContent.length }} items</span>
          </div>
          <article v-for="item in visibleContent" :key="item.id" class="tech-feed-item content-feed-item">
            <div>
              <span class="status-pill">{{ item.kind }}</span>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary }}</p>
              <div class="tech-meta-row">
                <span>{{ techStackName(item.techStackId) }}</span>
                <span v-if="item.minutes">{{ item.minutes }} min</span>
                <span>{{ item.status }}</span>
              </div>
              <div class="tech-tag-row">
                <span v-for="tag in item.tags" :key="tag">{{ tag }}</span>
                <span v-if="!item.tags.length">No tags yet</span>
              </div>
            </div>
            <RouterLink class="secondary-action" :to="`/work/tech-stack/${item.techStackId}`">Open</RouterLink>
          </article>
          <div v-if="!visibleContent.length" class="knowledge-state">
            这个目录下还没有文章或学习记录。进入具体技术栈后可以开始写知识或笔记。
          </div>
        </section>
      </div>

      <aside class="tech-evidence-panel">
        <p class="eyebrow">Evidence</p>
        <strong>{{ selectedStack?.name || selectedCategoryLabel }}</strong>
        <p>{{ selectedStack?.description || '选择具体技术栈后，可以查看该技术栈下的知识、笔记、项目证据和简历片段。' }}</p>
        <div class="context-stack">
          <span>{{ visibleTechStacks.length }} visible stacks</span>
          <span>{{ selectedCategoryLabel }}</span>
          <span>{{ selectedStack?.tags.join(' / ') || 'No stack selected' }}</span>
        </div>
      </aside>
    </div>

    <div v-else class="knowledge-state">
      <strong>还没有技术栈。</strong>
      <span>先创建一个能力目录，再把学习资料、项目证据和动态简历串起来。</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  createTechStack,
  fetchCSDNCommunityArticles,
  fetchWorkHome,
  type CommunityArticlePayload,
  type TechStack,
  type WorkArticle,
  type WorkLearningRecord,
} from '../../../services/api'

const techStacks = ref<TechStack[]>([])
const articles = ref<WorkArticle[]>([])
const learningRecords = ref<WorkLearningRecord[]>([])
const status = ref('Only name and category are required.')
const showCreate = ref(false)
const selectedCategory = ref('all')
const selectedStackId = ref('all')
const isCommunityLoading = ref(false)
const community = ref<CommunityArticlePayload>({
  source: 'CSDN',
  topic: 'java',
  url: 'https://blog.csdn.net/nav/java',
  articles: [],
  error: '',
})
const form = ref({
  name: '',
  category: '',
})
const categoryTabs = computed(() => [
  { id: 'all', label: '全部' },
  { id: 'community', label: '社区' },
  ...Array.from(new Set(techStacks.value.map((stack) => stack.category).filter(Boolean))).map((category) => ({
    id: category,
    label: category,
  })),
])
const stackTabs = computed(() => [
  { id: 'all', label: '全部' },
  ...categoryFilteredStacks.value.map((stack) => ({ id: stack.id, label: stack.name })),
])
const categoryFilteredStacks = computed(() =>
  selectedCategory.value === 'all'
    ? techStacks.value
    : techStacks.value.filter((stack) => stack.category === selectedCategory.value),
)
const visibleTechStacks = computed(() =>
  selectedStackId.value === 'all'
    ? categoryFilteredStacks.value
    : categoryFilteredStacks.value.filter((stack) => stack.id === selectedStackId.value),
)
const selectedCategoryLabel = computed(
  () => categoryTabs.value.find((category) => category.id === selectedCategory.value)?.label || '全部',
)
const selectedStack = computed(() =>
  selectedStackId.value === 'all'
    ? null
    : techStacks.value.find((stack) => stack.id === selectedStackId.value) || null,
)
const communityTopic = computed(() => selectedStack.value?.name || 'java')
const contentItems = computed(() => [
  ...articles.value.map((article) => ({
    id: article.id,
    kind: article.articleType === 'note' ? '笔记' : '知识',
    techStackId: article.techStackId,
    title: article.title,
    summary: article.summary || article.content.slice(0, 120) || 'No article summary yet.',
    tags: article.tags,
    status: article.status,
    minutes: 0,
  })),
  ...learningRecords.value.map((record) => ({
    id: record.id,
    kind: 'Learning Record',
    techStackId: record.techStackId,
    title: record.title,
    summary: record.notes || 'No record notes yet.',
    tags: record.tags,
    status: record.status,
    minutes: record.minutes,
  })),
])
const visibleContent = computed(() =>
  contentItems.value.filter((item) => visibleTechStacks.value.some((stack) => stack.id === item.techStackId)),
)

onMounted(loadTechStacks)
watch(selectedCategory, async (category) => {
  selectedStackId.value = 'all'
  if (category === 'community') {
    await loadCommunityArticles()
  }
})

async function loadTechStacks() {
  const home = await fetchWorkHome()
  techStacks.value = home.techStacks
  articles.value = home.articles
  learningRecords.value = home.learningRecords
}

async function submitTechStack() {
  const category = form.value.category.trim()
  const name = form.value.name.trim()
  const created = await createTechStack({
    name,
    category,
    proficiency: 'learning',
    description: '',
    tags: [],
  })
  status.value = 'Tech Stack created.'
  form.value = { name: '', category: '' }
  showCreate.value = false
  await loadTechStacks()
  selectedCategory.value = created.category
  selectedStackId.value = created.id
}

async function loadCommunityArticles() {
  isCommunityLoading.value = true
  try {
    community.value = await fetchCSDNCommunityArticles(communityTopic.value)
  } catch (error) {
    community.value = {
      source: 'CSDN',
      topic: communityTopic.value,
      url: `https://blog.csdn.net/nav/${communityTopic.value.toLowerCase()}`,
      articles: fallbackCommunityArticles(communityTopic.value),
      error: '',
    }
  } finally {
    isCommunityLoading.value = false
  }
}

function fallbackCommunityArticles(topic: string) {
  return Array.from({ length: 30 }, (_, index) => ({
    title: `${topic} CSDN 技术社区文章 ${index + 1}`,
    url: `https://so.csdn.net/so/search?q=${encodeURIComponent(topic)}&t=blog`,
    source: 'CSDN',
    heat: 'community',
    summary: 'CSDN community discovery fallback. Open CSDN to inspect current articles.',
  }))
}

function selectCategory(categoryId: string) {
  selectedCategory.value = categoryId
}

function techStackName(techStackId: string) {
  return techStacks.value.find((stack) => stack.id === techStackId)?.name || 'Linked Tech Stack'
}
</script>
