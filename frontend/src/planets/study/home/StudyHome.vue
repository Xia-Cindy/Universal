<template>
  <section class="study-home" aria-labelledby="study-home-title">
    <p class="eyebrow">Study Home</p>
    <h2 id="study-home-title">{{ pageTitle }}</h2>

    <div v-if="loadState === 'loading'" class="knowledge-state">Loading Study Workspace...</div>
    <div v-else-if="loadState === 'offline'" class="knowledge-state">Study Workspace is unavailable.</div>

    <template v-else>
      <div v-if="!workspace.currentGoal" class="knowledge-state">
        <strong>Study Planet needs a Goal.</strong>
        <span>Create a learning direction before plans, tasks, and Knowledge start to connect.</span>
        <RouterLink class="primary-action" to="/study/goals">Create Goal</RouterLink>
      </div>

      <template v-else>
        <section class="home-band" aria-label="Current goal">
          <div>
            <span class="status-pill">{{ goalTypeLabel(workspace.currentGoal.goalType) }}</span>
            <h3>{{ workspace.currentGoal.goalName }}</h3>
            <p>{{ deadlineText }}</p>
            <p v-if="workspace.currentGoal.description">{{ workspace.currentGoal.description }}</p>
          </div>
          <RouterLink class="secondary-action" to="/study/goals">Switch Goal</RouterLink>
        </section>

        <section class="home-section">
          <h3>Today’s Mission</h3>
          <div v-if="workspace.todayTasks.length" class="task-list">
            <article v-for="task in workspace.todayTasks" :key="task.id" class="task-row task-row-split">
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
            <span>No task is scheduled for today under the current Goal.</span>
          </div>
        </section>

        <section class="home-section">
          <div class="section-heading">
            <h3>Primary Action</h3>
            <RouterLink class="primary-action" :to="primaryAction.route">{{ primaryAction.label }}</RouterLink>
          </div>
          <p class="surface-copy">{{ primaryAction.description }}</p>
        </section>

        <section class="home-section">
          <h3>Recent Progress</h3>
          <div class="progress-snapshot" aria-label="Learning summary">
            <span>Today {{ learningSummary.todayStudyMinutes || 0 }} min</span>
            <span>This week {{ learningSummary.weekStudyMinutes || 0 }} min</span>
            <span>{{ learningSummary.completedTasks || 0 }}/{{ learningSummary.totalTasks || 0 }} tasks</span>
            <span>{{ workspace.knowledgeSummary.documentCount || 0 }} documents</span>
          </div>
        </section>

        <section class="home-section">
          <h3>AI Insight</h3>
          <div class="knowledge-state">
            <strong>{{ dataQualityLabel }}</strong>
            <ul v-if="workspace.analyticsSummary.learningInsights.length">
              <li v-for="insight in workspace.analyticsSummary.learningInsights" :key="insight">
                {{ insight }}
              </li>
            </ul>
            <ul v-if="workspace.analyticsSummary.recommendedActions.length">
              <li v-for="action in workspace.analyticsSummary.recommendedActions" :key="action">
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
import {
  fetchStudyWorkspace,
  type StudyGoalType,
  type StudyWorkspacePayload,
} from '../../../services/api'

const emptyWorkspace: StudyWorkspacePayload = {
  state: 'needs_goal',
  currentGoal: null,
  goals: [],
  plans: {
    longTermPlans: [],
    monthlyPlans: [],
    weeklyPlans: [],
    dailyTasks: [],
  },
  planSummary: {
    hasPlan: false,
    longTermPlanCount: 0,
    monthlyPlanCount: 0,
    weeklyPlanCount: 0,
    dailyTaskCount: 0,
    completedTaskCount: 0,
    taskCompletionRate: 0,
  },
  todayTasks: [],
  knowledgeSummary: {
    documents: [],
    statusCounts: {},
    subjects: [],
    documentCount: 0,
    goalLinkedCount: 0,
    independentCount: 0,
  },
  analyticsSummary: {
    progressSummary: {},
    learningInsights: [],
    weakAreas: [],
    recommendedActions: [],
    report: {},
    dataQuality: {
      state: 'insufficient',
      limitations: ['Complete study tasks and sessions first.'],
    },
    learningSummary: {},
  },
}

const workspace = ref<StudyWorkspacePayload>(emptyWorkspace)
const loadState = ref('loading')

const pageTitle = computed(() =>
  workspace.value.currentGoal ? workspace.value.currentGoal.goalName : 'Create your learning space',
)
const learningSummary = computed(() => workspace.value.analyticsSummary.learningSummary || {})
const primaryAction = computed(() => {
  const currentGoal = workspace.value.currentGoal
  if (!currentGoal) {
    return {
      label: 'Create Goal',
      route: '/study/goals',
      description: 'Start by choosing the learning direction for this Study Workspace.',
    }
  }
  if (!workspace.value.planSummary.hasPlan) {
    return {
      label: 'Create Plan Structure',
      route: '/study/plan',
      description: 'Turn the current Goal into a long-term, monthly, weekly, and daily structure.',
    }
  }
  const nextTask = workspace.value.todayTasks.find((task) => task.status !== 'completed')
  if (nextTask) {
    return {
      label: 'Start Learning',
      route: `/study/session/new?taskId=${nextTask.id}`,
      description: `${nextTask.subject}: ${nextTask.topic}`,
    }
  }
  if (!workspace.value.todayTasks.length) {
    return {
      label: 'Add Daily Task',
      route: '/study/plan',
      description: 'Create or adjust Daily Tasks under the current Goal.',
    }
  }
  return {
    label: 'View Analytics',
    route: '/study/analytics',
    description: 'Today’s tasks are complete. Review the latest learning signal.',
  }
})
const deadlineText = computed(() => {
  const goal = workspace.value.currentGoal
  if (!goal?.deadline) {
    return 'Open-ended learning direction'
  }
  return `${goal.deadline} · ${goal.remainingDays ?? 0} days left`
})
const dataQualityLabel = computed(() =>
  workspace.value.analyticsSummary.dataQuality?.state === 'ready' ? 'Ready' : 'More data needed',
)
const hasInsight = computed(
  () =>
    workspace.value.analyticsSummary.learningInsights.length > 0 ||
    workspace.value.analyticsSummary.recommendedActions.length > 0,
)
const firstLimitation = computed(
  () =>
    workspace.value.analyticsSummary.dataQuality?.limitations?.[0] ||
    'Study activity will unlock useful recommendations.',
)

onMounted(loadWorkspace)

function goalTypeLabel(type: StudyGoalType) {
  const labels: Record<StudyGoalType, string> = {
    exam: '考试目标',
    learning: '知识学习',
    reading: '阅读目标',
    growth: '成长目标',
  }
  return labels[type]
}

async function loadWorkspace() {
  try {
    loadState.value = 'loading'
    workspace.value = await fetchStudyWorkspace()
    loadState.value = 'ready'
  } catch {
    loadState.value = 'offline'
  }
}
</script>
