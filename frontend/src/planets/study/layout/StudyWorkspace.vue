<template>
  <main class="study-workspace planet-workspace universe-screen">
    <UniverseBackdrop tone="study" />
    <header class="workspace-topbar">
      <RouterLink aria-label="Return to Universe Home" title="Universe Home" class="universe-return icon-return" to="/">Universe Home</RouterLink>
      <div class="workspace-crumbs" aria-label="Universe / Study Planet · Universe > Study Planet">
        <span>Study Planet</span><i>/</i><strong>{{ breadcrumbGoal }}</strong><i>/</i><span>{{ currentLocation }}</span>
      </div>
      <div class="workspace-goal-switcher" aria-label="Current Goal">
        <span class="workspace-goal-label">Current Goal</span>
        <strong>{{ currentGoalName }}</strong>
        <button
          v-if="goals.length > 1"
          class="icon-action"
          type="button"
          title="Switch Goal"
          aria-label="Switch Goal"
          @click="isGoalSwitcherOpen = !isGoalSwitcherOpen"
        >⌄</button>
        <select v-if="isGoalSwitcherOpen" v-model="selectedGoalId" @change="switchGoal">
          <option v-for="goal in goals" :key="goal.id" :value="goal.id">{{ goal.goalName }}</option>
        </select>
      </div>
    </header>

    <section class="workspace-grid study-grid">
      <nav class="study-nav" aria-label="Study workspace">
        <RouterLink v-for="item in navigation" :key="item.route" :to="item.route" :title="item.label" :aria-label="item.label">
          <span class="nav-icon" aria-hidden="true">{{ navIcons[item.label] }}</span><span class="nav-label">{{ item.label }}</span>
        </RouterLink>
      </nav>
      <RouterView />
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchStudyWorkspace, switchStudyGoal, type StudyGoal } from '../../../services/api'
import UniverseBackdrop from '../../../ui/UniverseBackdrop.vue'

const navigation = [
  { label: 'Home', route: '/study' },
  { label: 'Plan', route: '/study/plan' },
  { label: 'Knowledge', route: '/study/knowledge' },
  { label: 'Wordbook', route: '/study/wordbook' },
  { label: 'Tutor', route: '/study/tutor' },
  { label: 'Review', route: '/study/review' },
  { label: 'Analytics', route: '/study/analytics' },
]

const navIcons: Record<string, string> = {
  Home: '⌂', Plan: '▱', Knowledge: '⌬', Wordbook: '▤', Tutor: '◌', Review: '↻', Analytics: '▥',
}

const route = useRoute()
const goals = ref<StudyGoal[]>([])
const selectedGoalId = ref('')
const activeGoal = ref<StudyGoal | null>(null)
const isGoalSwitcherOpen = ref(false)

const currentLocation = computed(() => {
  const match = [...navigation]
    .sort((left, right) => right.route.length - left.route.length)
    .find((item) => route.path === item.route || route.path.startsWith(`${item.route}/`))
  if (route.path === '/study/goals/new') {
    return 'Create Goal'
  }
  if (route.path === '/study/goals') {
    return 'Manage Goals'
  }
  return match?.label || 'Home'
})
const currentGoalName = computed(() => activeGoal.value?.goalName || 'No Goal yet')
const breadcrumbGoal = computed(() => activeGoal.value?.goalName || 'Current Goal')

onMounted(loadWorkspaceContext)
watch(() => route.fullPath, loadWorkspaceContext)

async function loadWorkspaceContext() {
  const workspace = await fetchStudyWorkspace()
  goals.value = workspace.goals
  activeGoal.value = workspace.currentGoal
  selectedGoalId.value = workspace.currentGoal?.id || ''
}

async function switchGoal() {
  if (!selectedGoalId.value || selectedGoalId.value === activeGoal.value?.id) {
    return
  }
  await switchStudyGoal(selectedGoalId.value)
  isGoalSwitcherOpen.value = false
  await loadWorkspaceContext()
}
</script>
