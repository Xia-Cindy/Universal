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
      <a v-for="item in navigation" :key="item.route" :href="item.route">{{ item.label }}</a>
    </nav>

    <section class="workspace-grid">
      <StudyHome />
      <aside class="ai-panel">
        <p class="eyebrow">AI Recommendation</p>
        <p>Create your first Goal to unlock personalized study guidance.</p>
      </aside>
    </section>
  </main>
</template>

<script setup lang="ts">
import StudyHome from '../home/StudyHome.vue'

const navigation = [
  { label: 'Home', route: '/study' },
  { label: 'Plan', route: '/study/plan' },
  { label: 'Knowledge', route: '/study/knowledge' },
  { label: 'Tutor', route: '/study/tutor' },
  { label: 'Review', route: '/study/review' },
  { label: 'Analytics', route: '/study/analytics' },
]
</script>

