<template>
  <section class="study-plan" aria-labelledby="work-projects-title">
    <p class="eyebrow">Projects</p>
    <h2 id="work-projects-title">项目与证据</h2>
    <p class="surface-copy">项目是动态简历的证据来源。先记录真实做过的事，再生成岗位表达。</p>

    <form class="study-form" @submit.prevent="submitProject">
      <label>
        项目名称
        <input v-model="form.title" required placeholder="RAGFlow Knowledge Migration" />
      </label>
      <label>
        关联技术栈
        <select v-model="selectedTechStackId">
          <option value="">No stack</option>
          <option v-for="stack in techStacks" :key="stack.id" :value="stack.id">
            {{ stack.name }}
          </option>
        </select>
      </label>
      <label class="wide-field">
        项目描述
        <textarea v-model="form.description" rows="3" />
      </label>
      <div class="knowledge-actions">
        <button type="submit">Create Project Evidence</button>
        <span>{{ status }}</span>
      </div>
    </form>

    <div v-if="projects.length" class="goal-list">
      <article v-for="project in projects" :key="project.id" class="knowledge-document">
        <span class="status-pill">{{ project.status }}</span>
        <h3>{{ project.title }}</h3>
        <p class="surface-copy">{{ project.description }}</p>
        <small>{{ project.techStackIds.length }} linked tech stacks</small>
      </article>
    </div>
    <div v-else class="knowledge-state">No project evidence yet.</div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  createWorkProject,
  fetchTechStacks,
  fetchWorkProjects,
  type TechStack,
  type WorkProject,
} from '../../../services/api'

const projects = ref<WorkProject[]>([])
const techStacks = ref<TechStack[]>([])
const selectedTechStackId = ref('')
const status = ref('Create evidence only from real work or confirmed practice.')
const form = ref({
  title: '',
  description: '',
})

onMounted(load)

async function load() {
  projects.value = await fetchWorkProjects()
  techStacks.value = await fetchTechStacks()
}

async function submitProject() {
  await createWorkProject({
    ...form.value,
    techStackIds: selectedTechStackId.value ? [selectedTechStackId.value] : [],
  })
  status.value = 'Project evidence created.'
  form.value = { title: '', description: '' }
  selectedTechStackId.value = ''
  await load()
}
</script>
