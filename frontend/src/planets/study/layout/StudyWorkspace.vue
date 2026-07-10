<template>
  <main class="study-workspace">
    <header class="study-header">
      <div>
        <RouterLink class="universe-return" to="/">Universe Home</RouterLink>
        <p class="eyebrow">Study Planet</p>
        <h1>Study Workspace</h1>
        <p class="workspace-location" aria-label="Universe / Study Planet">
          Universe > Study Planet > {{ breadcrumbGoal }} > {{ currentLocation }}
        </p>
      </div>
      <div class="goal-context" aria-label="Current Goal">
        <span class="eyebrow">Current Goal</span>
        <strong>{{ currentGoalName }}</strong>
        <select v-if="goals.length" v-model="selectedGoalId" @change="switchGoal">
          <option v-for="goal in goals" :key="goal.id" :value="goal.id">
            {{ goal.goalName }}
          </option>
        </select>
        <RouterLink class="secondary-action" to="/study/goals">Manage Goals</RouterLink>
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
          Study guidance comes from Analytics and your current learning workflow. Knowledge stays
          linked to the Goal when you choose one.
        </p>
      </aside>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchStudyWorkspace, switchStudyGoal, type StudyGoal } from '../../../services/api'

const navigation = [
  { label: 'Home', route: '/study' },
  { label: 'Plan', route: '/study/plan' },
  { label: 'Knowledge', route: '/study/knowledge' },
  { label: 'Tutor', route: '/study/tutor' },
  { label: 'Review', route: '/study/review' },
  { label: 'Analytics', route: '/study/analytics' },
]

const route = useRoute()
const goals = ref<StudyGoal[]>([])
const selectedGoalId = ref('')
const activeGoal = ref<StudyGoal | null>(null)

const currentLocation = computed(() => {
  const match = [...navigation]
    .sort((left, right) => right.route.length - left.route.length)
    .find((item) => route.path === item.route || route.path.startsWith(`${item.route}/`))
  if (route.path === '/study/goals') {
    return 'Goals'
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
  await loadWorkspaceContext()
}
</script>
