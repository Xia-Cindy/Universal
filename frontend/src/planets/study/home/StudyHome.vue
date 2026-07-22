<template>
  <section class="study-home" aria-labelledby="study-home-title">
    <div class="study-home-intro">
      <div>
        <p class="eyebrow">Study Home</p>
        <h2 id="study-home-title">{{ pageTitle }}</h2>
      </div>
      <span class="status-pill">Next Action First</span>
    </div>

    <div v-if="loadState === 'loading'" class="knowledge-state ambient-state">
      Loading Goal, Plan, Memory, and Analytics...
    </div>
    <div v-else-if="loadState === 'offline'" class="knowledge-state ambient-state">
      <strong>Study Workspace is unavailable.</strong>
      <span>Goal and task data could not be loaded. Retry when the backend is reachable.</span>
    </div>

    <template v-else>
      <div v-if="!workspace.currentGoal" class="knowledge-state">
        <strong>Study Planet needs a Goal.</strong>
        <span>Create a learning direction before plans, tasks, and Knowledge start to connect.</span>
        <RouterLink class="primary-action" to="/study/goals">Create Goal</RouterLink>
      </div>

      <template v-else>
        <section class="next-action-room" aria-label="Primary next action">
          <div class="next-action-copy">
            <span class="status-pill">{{ primaryActionTag }}</span>
            <h3>{{ primaryAction.label }}</h3>
            <p>{{ primaryAction.description }}</p>
            <RouterLink class="primary-action" :to="primaryAction.route">{{ primaryAction.label }}</RouterLink>
          </div>
          <aside class="recommendation-card">
            <p class="eyebrow">AI Insight</p>
            <strong>{{ dataQualityLabel }}</strong>
            <p>{{ recommendationText }}</p>
          </aside>
        </section>

        <section class="home-band" aria-label="Current goal">
          <div>
            <span class="status-pill">{{ goalTypeLabel(workspace.currentGoal.goalType) }}</span>
            <h3>{{ workspace.currentGoal.goalName }}</h3>
            <p>{{ deadlineText }}</p>
            <p v-if="workspace.currentGoal.description">{{ workspace.currentGoal.description }}</p>
          </div>
          <RouterLink class="secondary-action" to="/study/goals">Switch Goal</RouterLink>
        </section>

        <section class="home-layout">
          <div class="home-section today-panel">
            <div class="section-heading">
              <h3>Today’s Mission</h3>
              <span>{{ workspace.todayTasks.length }} tasks</span>
            </div>
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
                <RouterLink v-else class="secondary-action" to="/study/analytics">
                  View Record / Review
                </RouterLink>
              </article>
            </div>
            <div v-else class="knowledge-state">
              <span>No task is scheduled for today under the current Goal.</span>
            </div>
          </div>

          <div class="home-section progress-panel">
            <h3>Progress Snapshot</h3>
            <div class="progress-snapshot" aria-label="Learning summary">
              <span><strong>{{ learningSummary.todayStudyMinutes || 0 }}</strong>Today min</span>
              <span><strong>{{ learningSummary.weekStudyMinutes || 0 }}</strong>This week min</span>
              <span><strong>{{ learningSummary.completedTasks || 0 }}/{{ learningSummary.totalTasks || 0 }}</strong>Tasks</span>
              <span><strong>{{ workspace.knowledgeSummary.documentCount || 0 }}</strong>Documents</span>
            </div>
          </div>
        </section>

        <section class="home-section insight-panel">
          <div>
            <h3>Recommendation Evidence</h3>
            <p class="surface-copy">AI advice should explain what it used, not appear as a generic prompt.</p>
          </div>
          <div class="knowledge-state">
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
  primaryAction: {
    type: 'create_goal',
    label: 'Create Goal',
    route: '/study/goals',
    description: 'Start by choosing the learning direction for this Study Workspace.',
  },
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
  workspace.value.currentGoal ? 'What should I do next today?' : 'Create your learning space',
)
const learningSummary = computed(() => workspace.value.analyticsSummary.learningSummary || {})
const primaryAction = computed(() => workspace.value.primaryAction)
const primaryActionTag = computed(() => {
  const labels: Record<string, string> = {
    create_goal: 'CREATE GOAL',
    generate_plan: 'GENERATE PLAN',
    start_learning: 'PRIMARY NEXT ACTION',
    start_review: 'REVIEW DUE',
    view_record: 'TODAY COMPLETE',
  }
  return labels[primaryAction.value.type] || 'PRIMARY NEXT ACTION'
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
const recommendationText = computed(
  () =>
    workspace.value.analyticsSummary.recommendedActions[0] ||
    workspace.value.analyticsSummary.learningInsights[0] ||
    firstLimitation.value,
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
