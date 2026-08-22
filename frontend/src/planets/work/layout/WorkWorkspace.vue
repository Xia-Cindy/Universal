<template>
  <main class="work-workspace planet-workspace universe-screen">
    <UniverseBackdrop tone="work" />
    <header class="workspace-topbar work-topbar">
      <RouterLink aria-label="Return to Universe Home" title="Universe Home" class="universe-return icon-return" to="/">Universe Home</RouterLink>
      <div class="workspace-crumbs" aria-label="Universe / Work Planet">
        <span>Work Planet</span><i>/</i><strong>{{ currentLocation }}</strong>
      </div>
      <div class="workspace-goal-switcher work-focus"><span class="workspace-goal-label">Practice loop</span><strong>Case · Evidence · Review</strong></div>
    </header>

    <section class="workspace-grid work-grid">
      <nav class="study-nav" aria-label="Work workspace">
        <RouterLink v-for="item in navigation" :key="item.route" :to="item.route" :title="item.label" :aria-label="item.label">
          <span class="nav-icon" aria-hidden="true">{{ navIcons[item.label] }}</span><span class="nav-label">{{ item.label }}</span>
        </RouterLink>
      </nav>
      <RouterView />
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import UniverseBackdrop from '../../../ui/UniverseBackdrop.vue'

const navigation = [
  { label: 'Home', route: '/work' },
  { label: 'Tech Stack', route: '/work/tech-stack' },
  { label: 'Projects', route: '/work/projects' },
  { label: 'Resume', route: '/work/resume' },
]

const navIcons: Record<string, string> = {
  Home: '⌂', 'Tech Stack': '▱', Projects: '◇', Resume: '▤',
}

const route = useRoute()
const currentLocation = computed(() => {
  const match = [...navigation]
    .sort((left, right) => right.route.length - left.route.length)
    .find((item) => route.path === item.route || route.path.startsWith(`${item.route}/`))
  return match?.label || 'Home'
})
</script>
