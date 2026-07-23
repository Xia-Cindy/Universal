<template>
  <section class="study-home work-home" aria-labelledby="work-home-title">
    <div class="study-home-intro">
      <div>
        <p class="eyebrow">Work Home</p>
        <h2 id="work-home-title">职业能力工作空间</h2>
        <p>把学习过的知识、技术栈和项目证据组织成可表达的岗位竞争力。</p>
      </div>
      <RouterLink class="primary-action" :to="home.primaryAction.route">
        {{ home.primaryAction.label }}
      </RouterLink>
    </div>

    <div class="progress-snapshot">
      <article>
        <strong>{{ home.summary.techStackCount }}</strong>
        <span>Tech Stacks</span>
      </article>
      <article>
        <strong>{{ home.summary.projectCount }}</strong>
        <span>Projects</span>
      </article>
      <article>
        <strong>{{ home.summary.resumeCount }}</strong>
        <span>Resume versions</span>
      </article>
      <article>
        <strong>{{ home.summary.knowledgeDocumentCount }}</strong>
        <span>Work Knowledge docs</span>
      </article>
    </div>

    <section class="home-section">
      <div class="section-heading">
        <h3>重点技术栈</h3>
        <RouterLink class="secondary-action" to="/work/tech-stack">Open Tech Stack</RouterLink>
      </div>
      <div v-if="home.techStacks.length" class="goal-list">
        <article v-for="stack in home.techStacks.slice(0, 3)" :key="stack.id" class="knowledge-document">
          <span class="status-pill">{{ stack.proficiency }}</span>
          <h3>{{ stack.name }}</h3>
          <p class="surface-copy">{{ stack.description || stack.category }}</p>
        </article>
      </div>
      <div v-else class="knowledge-state">Create your first Tech Stack to start building evidence.</div>
    </section>

    <section class="home-section">
      <div class="section-heading">
        <h3>Work Knowledge</h3>
        <RouterLink class="secondary-action" to="/work/knowledge">Open Knowledge</RouterLink>
      </div>
      <p class="surface-copy">
        Work has its own Knowledge Space for tech notes, JD material, interview questions, project evidence, and resume material.
        Study Knowledge can still be referenced when it supports a capability.
      </p>
    </section>

    <section class="home-section">
      <div class="section-heading">
        <h3>动态简历</h3>
        <RouterLink class="secondary-action" to="/work/resume">Open Resume</RouterLink>
      </div>
      <p class="surface-copy">
        Resume drafts stay evidence-based. The system can draft wording, but it cannot invent experience.
      </p>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchWorkHome, type WorkHomePayload } from '../../../services/api'

const home = ref<WorkHomePayload>({
  state: 'loading',
  primaryAction: {
    type: 'create_tech_stack',
    label: 'Create Tech Stack',
    route: '/work/tech-stack',
    description: '',
  },
  summary: {
    techStackCount: 0,
    projectCount: 0,
    resumeCount: 0,
    knowledgeDocumentCount: 0,
  },
  techStacks: [],
  projects: [],
  resumes: [],
})

onMounted(async () => {
  home.value = await fetchWorkHome()
})
</script>
