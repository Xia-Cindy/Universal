<template>
  <main class="study-workspace">
    <header class="study-header">
      <div>
        <RouterLink class="universe-return" to="/">Universe Home</RouterLink>
        <p class="eyebrow">Study Planet</p>
        <h1>Study Workspace</h1>
        <p class="workspace-location">Universe / Study Planet / {{ currentLocation }}</p>
      </div>
      <div class="signals">
        <span>AI Core: ready</span>
        <span>Memory: scoped</span>
      </div>
    </header>

    <section class="workspace-grid">
      <nav class="study-nav" aria-label="Study workspace">
        <RouterLink v-for="item in navigation" :key="item.route" :to="item.route">
          {{ item.label }}
        </RouterLink>
      </nav>
      <RouterView />
      <aside class="ai-panel">
        <p class="eyebrow">AI Recommendation</p>
        <p>
          AI Core can guide learning from your workflow data. Knowledge keeps source material close
          to the Study path.
        </p>
      </aside>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const navigation = [
  { label: 'Home', route: '/study' },
  { label: 'Plan', route: '/study/plan' },
  { label: 'Knowledge', route: '/study/knowledge' },
  { label: 'Tutor', route: '/study/tutor' },
  { label: 'Review', route: '/study/review' },
  { label: 'Analytics', route: '/study/analytics' },
]

const route = useRoute()
const currentLocation = computed(() => {
  const match = [...navigation]
    .sort((left, right) => right.route.length - left.route.length)
    .find((item) => route.path === item.route || route.path.startsWith(`${item.route}/`))
  return match?.label || 'Home'
})
</script>
