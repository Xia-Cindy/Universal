<template>
  <section class="study-home" aria-labelledby="study-home-title">
    <p class="eyebrow">Study Home</p>
    <h2 id="study-home-title">{{ title }}</h2>

    <div v-if="loadState === 'loading'" class="knowledge-state">Loading Study Planet...</div>
    <div v-else-if="loadState === 'offline'" class="knowledge-state">Study Home is unavailable.</div>

    <template v-else>
      <div v-if="!home.currentGoal" class="knowledge-state">
        <strong>Study Planet needs a Goal.</strong>
        <span>Create one Goal to open today’s learning loop.</span>
        <RouterLink class="primary-action" to="/study/onboarding">Start Onboarding</RouterLink>
      </div>

      <template v-else>
        <section class="home-band" aria-label="Current goal">
          <div>
            <span class="status-pill">{{ goalTypeLabel }}</span>
            <h3>{{ home.currentGoal.goalName }}</h3>
            <p>{{ deadlineText }}</p>
            <p v-if="home.currentGoal.description">{{ home.currentGoal.description }}</p>
          </div>
          <RouterLink class="primary-action" :to="primaryRoute">{{ primaryLabel }}</RouterLink>
        </section>

        <div class="progress-snapshot" aria-label="Progress snapshot">
          <span>Today {{ home.progressSnapshot.todayStudyMinutes }} min</span>
          <span>This week {{ home.progressSnapshot.weekStudyMinutes }} min</span>
          <span>{{ home.progressSummary.completedTasks }}/{{ home.progressSummary.totalTasks }} tasks</span>
          <span>Streak {{ home.progressSnapshot.studyStreakDays }} days</span>
        </div>

        <section class="home-section">
          <h3>Today’s Mission</h3>
          <div v-if="home.todayTasks.length" class="task-list">
            <article v-for="task in home.todayTasks" :key="task.id" class="task-row task-row-split">
              <div>
                <strong>{{ task.subject }}</strong>
                <span>{{ task.topic }}</span>
                <small>{{ task.estimatedMinutes }} min · {{ task.status }}</small>
              </div>
              <RouterLink
                v-if="task.status !== 'completed'"
                class="primary-action"
                :to="`/study/session/new?taskId=${task.id}`"
              >
                Start
              </RouterLink>
            </article>
          </div>
          <div v-else class="knowledge-state">
            <span>No tasks are scheduled for today.</span>
            <RouterLink class="primary-action" to="/study/plan">Open Plan</RouterLink>
          </div>
        </section>

        <section class="home-section">
          <h3>AI Insight</h3>
          <div class="knowledge-state">
            <strong>{{ dataQualityLabel }}</strong>
            <ul v-if="home.aiInsight.learningInsights.length">
              <li v-for="insight in home.aiInsight.learningInsights" :key="insight">
                {{ insight }}
              </li>
            </ul>
            <ul v-if="home.aiInsight.recommendedActions.length">
              <li v-for="action in home.aiInsight.recommendedActions" :key="action">
                {{ action }}
              </li>
            </ul>
            <span v-if="!hasInsight">{{ firstLimitation }}</span>
          </div>
        </section>
      </template>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchStudyHome } from '../../../services/api'

const home = ref({
  state: 'empty',
  currentGoal: null as null | {
    goalType: string
    goalName: string
    examName?: string | null
    deadline?: string | null
    description?: string
    remainingDays: number | null
  },
  todayTasks: [] as Array<{
    id: string
    subject: string
    topic: string
    estimatedMinutes: number
    status: string
  }>,
  primaryNextAction: {
    label: 'Create Goal',
    route: '/study/onboarding',
  },
  aiInsight: {
    learningInsights: [] as string[],
    recommendedActions: [] as string[],
    dataQuality: {
      state: 'insufficient',
      limitations: ['No Study workflow data is available.'] as string[],
    },
  },
  progressSummary: {
    totalTasks: 0,
    completedTasks: 0,
    taskCompletionRate: 0,
  },
  progressSnapshot: {
    todayStudyMinutes: 0,
    weekStudyMinutes: 0,
    studyStreakDays: 0,
  },
})
const loadState = ref('ready')

const title = computed(() =>
  home.value.currentGoal ? home.value.currentGoal.goalName : 'Create your first learning Goal',
)
const primaryLabel = computed(() => home.value.primaryNextAction.label)
const primaryRoute = computed(() => home.value.primaryNextAction.route)
const goalTypeLabel = computed(() => {
  const labels: Record<string, string> = {
    exam: '考试目标',
    learning: '知识学习',
    growth: '成长目标',
  }
  return home.value.currentGoal ? labels[home.value.currentGoal.goalType] || '学习目标' : '学习目标'
})
const deadlineText = computed(() => {
  if (!home.value.currentGoal?.deadline) {
    return 'Long-term goal'
  }
  return `${home.value.currentGoal.deadline} · ${home.value.currentGoal.remainingDays} days left`
})
const dataQualityLabel = computed(() =>
  home.value.aiInsight.dataQuality.state === 'ready' ? 'Ready' : 'More data needed',
)
const hasInsight = computed(
  () =>
    home.value.aiInsight.learningInsights.length > 0 ||
    home.value.aiInsight.recommendedActions.length > 0,
)
const firstLimitation = computed(
  () => home.value.aiInsight.dataQuality.limitations[0] || 'Complete tasks and sessions first.',
)

onMounted(async () => {
  try {
    loadState.value = 'loading'
    home.value = await fetchStudyHome()
    loadState.value = 'ready'
  } catch {
    loadState.value = 'offline'
  }
})
</script>
