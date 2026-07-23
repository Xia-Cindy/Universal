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
          <strong>{{ detail.resumeSnippets.length }}</strong>
          <span>Resume Snippets</span>
        </article>
      </div>

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
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { fetchTechStackDetail } from '../../../services/api'

const route = useRoute()
const detail = ref<any | null>(null)

onMounted(async () => {
  detail.value = await fetchTechStackDetail(String(route.params.techStackId))
})
</script>
