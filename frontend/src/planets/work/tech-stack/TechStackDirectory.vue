<template>
  <section class="tech-nav-page" aria-labelledby="tech-stack-title">
    <header class="tech-nav-hero">
      <div>
        <p class="eyebrow">Tech Stack</p>
        <h2 id="tech-stack-title">技术栈目录</h2>
        <p class="surface-copy">像浏览技术频道一样管理能力：分类、标签、证据、项目和简历表达都从这里进入。</p>
      </div>
      <button type="button" @click="showCreate = !showCreate">
        {{ showCreate ? 'Close Create' : 'Add Tech Stack' }}
      </button>
    </header>

    <form v-if="showCreate" class="study-form tech-create-form" @submit.prevent="submitTechStack">
      <label>
        技术名称
        <input v-model="form.name" required placeholder="FastAPI / Vue / RAG" />
      </label>
      <label>
        分类
        <input v-model="form.category" required placeholder="Backend / Frontend / AI" />
      </label>
      <label>
        熟练度
        <select v-model="form.proficiency">
          <option value="learning">Learning</option>
          <option value="practicing">Practicing</option>
          <option value="project-ready">Project ready</option>
        </select>
      </label>
      <label class="wide-field">
        标签
        <input v-model="tagsText" placeholder="API, Python, retrieval" />
      </label>
      <label class="wide-field">
        描述
        <textarea v-model="form.description" rows="3" />
      </label>
      <div class="knowledge-actions">
        <button type="submit">Create Tech Stack</button>
        <span>{{ status }}</span>
      </div>
    </form>

    <div class="tech-channel-tabs" aria-label="Tech stack channels">
      <button
        v-for="channel in channelTabs"
        :key="channel.id"
        type="button"
        :class="{ selected: selectedChannel === channel.id }"
        @click="selectChannel(channel.id)"
      >
        {{ channel.label }}
      </button>
    </div>

    <div v-if="selectedChannel !== 'community'" class="tech-topic-tabs" aria-label="Tech tags">
      <button
        v-for="tag in tagTabs"
        :key="tag"
        type="button"
        :class="{ selected: selectedTag === tag }"
        @click="selectedTag = tag"
      >
        {{ tag }}
      </button>
    </div>

    <div v-if="selectedChannel === 'community'" class="tech-nav-layout">
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
          <div v-else-if="community.error" class="knowledge-state">
            <strong>CSDN articles unavailable.</strong>
            <span>{{ community.error }}</span>
          </div>
          <article v-for="article in community.articles" :key="article.url" class="tech-feed-item content-feed-item">
            <div>
              <span class="status-pill">{{ article.source }}</span>
              <h3>{{ article.title }}</h3>
              <p>{{ article.summary || '来自 CSDN 技术社区的文章，可用于了解相关技术动态。' }}</p>
            </div>
            <a class="secondary-action" :href="article.url" rel="noreferrer" target="_blank">Read</a>
          </article>
        </section>
      </div>

      <aside class="tech-evidence-panel">
        <p class="eyebrow">Community</p>
        <strong>只做资讯参考</strong>
        <p>社区文章不会自动进入你的 Work Knowledge；需要你确认后再上传或写成自己的文章/笔记。</p>
      </aside>
    </div>

    <div v-else-if="techStacks.length" class="tech-nav-layout">
      <aside class="tech-directory-panel" aria-label="Tech stack directory">
        <strong>技术目录</strong>
        <button
          v-for="stack in filteredTechStacks"
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
        <article v-for="stack in filteredTechStacks" :key="stack.id" class="tech-feed-item">
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
            技术栈目录下还没有文章或学习记录。进入一个技术栈后可以开始写。
          </div>
        </section>
      </div>

      <aside class="tech-evidence-panel">
        <p class="eyebrow">Evidence</p>
        <strong>{{ selectedStack?.name || '选择一个技术栈' }}</strong>
        <p>{{ selectedStack?.description || '下钻后可以查看关联知识、项目证据和简历片段。' }}</p>
        <div class="context-stack">
          <span>{{ filteredTechStacks.length }} visible stacks</span>
          <span>{{ selectedStack?.category || 'No category selected' }}</span>
          <span>{{ selectedStack?.tags.join(' / ') || 'No tags yet' }}</span>
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
const status = ref('Create a capability directory first.')
const tagsText = ref('')
const showCreate = ref(false)
const selectedChannel = ref('all')
const selectedTag = ref('全部')
const selectedStackId = ref('')
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
  category: 'Engineering',
  proficiency: 'learning',
  description: '',
})
const tags = computed(() =>
  tagsText.value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean),
)
const channelTabs = computed(() => [
  { id: 'all', label: '全部' },
  { id: 'community', label: '社区' },
  ...techStacks.value.map((stack) => ({ id: stack.id, label: stack.name })),
])
const tagTabs = computed(() => [
  '全部',
  ...Array.from(new Set(techStacks.value.flatMap((stack) => stack.tags).filter(Boolean))),
])
const filteredTechStacks = computed(() =>
  techStacks.value.filter((stack) => {
    const channelMatches = selectedChannel.value === 'all' || stack.id === selectedChannel.value
    const tagMatches = selectedTag.value === '全部' || stack.tags.includes(selectedTag.value)
    return channelMatches && tagMatches
  }),
)
const communityTopic = computed(() => selectedStack.value?.name || 'java')
const selectedStack = computed(
  () =>
    filteredTechStacks.value.find((stack) => stack.id === selectedStackId.value) ||
    filteredTechStacks.value[0] ||
    null,
)
const contentItems = computed(() => [
  ...articles.value.map((article) => ({
    id: article.id,
    kind: 'Article',
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
  contentItems.value.filter((item) => filteredTechStacks.value.some((stack) => stack.id === item.techStackId)),
)

onMounted(loadTechStacks)
watch(selectedChannel, async (channel) => {
  if (channel === 'community') {
    await loadCommunityArticles()
  }
})
watch(filteredTechStacks, (stacks) => {
  if (!stacks.some((stack) => stack.id === selectedStackId.value)) {
    selectedStackId.value = stacks[0]?.id || ''
  }
})

async function loadTechStacks() {
  const home = await fetchWorkHome()
  techStacks.value = home.techStacks
  articles.value = home.articles
  learningRecords.value = home.learningRecords
  selectedStackId.value = techStacks.value[0]?.id || ''
}

async function submitTechStack() {
  const created = await createTechStack({ ...form.value, tags: tags.value })
  status.value = 'Tech Stack created.'
  form.value = {
    name: '',
    category: 'Engineering',
    proficiency: 'learning',
    description: '',
  }
  tagsText.value = ''
  showCreate.value = false
  await loadTechStacks()
  selectedChannel.value = created.id
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
      articles: [],
      error: error instanceof Error ? error.message : 'Unable to load CSDN community articles.',
    }
  } finally {
    isCommunityLoading.value = false
  }
}

function selectChannel(channelId: string) {
  selectedChannel.value = channelId
  selectedTag.value = '全部'
  if (channelId !== 'all' && channelId !== 'community') {
    selectedStackId.value = channelId
  }
}

function techStackName(techStackId: string) {
  return techStacks.value.find((stack) => stack.id === techStackId)?.name || 'Linked Tech Stack'
}
</script>
