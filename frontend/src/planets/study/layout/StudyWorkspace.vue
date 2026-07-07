<template>
  <main class="study-workspace">
    <header class="study-header">
      <div>
        <p class="eyebrow">Study Planet</p>
        <h1>Study Workspace</h1>
      </div>
      <div class="signals">
        <span>AI Core: ready</span>
        <span>Memory: scoped</span>
      </div>
    </header>

    <nav class="study-nav" aria-label="Study workspace">
      <RouterLink v-for="item in navigation" :key="item.route" :to="item.route">
        {{ item.label }}
      </RouterLink>
    </nav>

    <section class="workspace-grid">
      <RouterView />
      <aside class="ai-panel">
        <p class="eyebrow">AI Recommendation</p>
        <p>AI Core starts in Milestone 3. Milestone 2 uses your learning workflow data.</p>
      </aside>
    </section>
  </main>
</template>

<script setup lang="ts">
const navigation = [
  { label: 'Home', route: '/study' },
  { label: 'Plan', route: '/study/plan' },
  { label: 'Knowledge', route: '/study/knowledge' },
  { label: 'Tutor', route: '/study/tutor' },
  { label: 'Review', route: '/study/review' },
  { label: 'Analytics', route: '/study/analytics' },
]
</script>
