<template>
  <main class="work-workspace">
    <header class="study-header work-header">
      <div class="workspace-title">
        <RouterLink class="universe-return" to="/">Universe Home</RouterLink>
        <p class="eyebrow">Work Planet</p>
        <h1>Work Workspace</h1>
        <p class="workspace-location">Universe > Work Planet > {{ currentLocation }}</p>
      </div>
      <div class="goal-context">
        <div>
          <span class="eyebrow">Career Focus</span>
          <strong>Tech Stack → Evidence → Resume</strong>
        </div>
        <RouterLink class="secondary-action" to="/work/knowledge">Open Work Knowledge</RouterLink>
      </div>
    </header>

    <section class="workspace-grid work-grid">
      <nav class="study-nav" aria-label="Work workspace">
        <RouterLink v-for="item in navigation" :key="item.route" :to="item.route">
          {{ item.label }}
        </RouterLink>
      </nav>
      <RouterView />
      <aside class="ai-panel">
        <p class="eyebrow">Work Context</p>
        <strong>Evidence first</strong>
        <p>Dynamic Resume only uses user-confirmed tech stacks, projects, and Knowledge evidence.</p>
        <div class="context-stack">
          <span>Work Knowledge first</span>
          <span>Study Knowledge can be referenced</span>
          <span>No fake experience</span>
        </div>
      </aside>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const navigation = [
  { label: 'Home', route: '/work' },
  { label: 'Tech Stack', route: '/work/tech-stack' },
  { label: 'Knowledge', route: '/work/knowledge' },
  { label: 'Projects', route: '/work/projects' },
  { label: 'Resume', route: '/work/resume' },
]

const route = useRoute()
const currentLocation = computed(() => {
  const match = [...navigation]
    .sort((left, right) => right.route.length - left.route.length)
    .find((item) => route.path === item.route || route.path.startsWith(`${item.route}/`))
  return match?.label || 'Home'
})
</script>
