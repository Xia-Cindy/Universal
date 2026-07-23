<template>
  <section class="study-plan" aria-labelledby="tech-stack-title">
    <p class="eyebrow">Tech Stack</p>
    <h2 id="tech-stack-title">技术栈目录</h2>
    <p class="surface-copy">每个技术栈都可以下钻到知识、项目证据和简历表达。</p>

    <form class="study-form" @submit.prevent="submitTechStack">
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

    <div v-if="techStacks.length" class="knowledge-grid tech-stack-grid">
      <article v-for="stack in techStacks" :key="stack.id" class="knowledge-document">
        <span class="status-pill">{{ stack.proficiency }}</span>
        <h3>{{ stack.name }}</h3>
        <p class="surface-copy">{{ stack.description || stack.category }}</p>
        <small>{{ stack.tags.join(' / ') || 'No tags yet' }}</small>
        <RouterLink class="primary-action" :to="`/work/tech-stack/${stack.id}`">Open Stack</RouterLink>
      </article>
    </div>
    <div v-else class="knowledge-state">
      <strong>No Tech Stack yet.</strong>
      <span>Create one capability you want to turn into career evidence.</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { createTechStack, fetchTechStacks, type TechStack } from '../../../services/api'

const techStacks = ref<TechStack[]>([])
const status = ref('Create a capability directory first.')
const tagsText = ref('')
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

onMounted(loadTechStacks)

async function loadTechStacks() {
  techStacks.value = await fetchTechStacks()
}

async function submitTechStack() {
  await createTechStack({ ...form.value, tags: tags.value })
  status.value = 'Tech Stack created.'
  form.value = {
    name: '',
    category: 'Engineering',
    proficiency: 'learning',
    description: '',
  }
  tagsText.value = ''
  await loadTechStacks()
}
</script>
