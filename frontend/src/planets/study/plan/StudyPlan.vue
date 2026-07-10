<template>
  <section class="study-plan" aria-labelledby="plan-title">
    <p class="eyebrow">Plan</p>
    <h2 id="plan-title">Learning Plan</h2>

    <div v-if="loadState === 'loading'" class="knowledge-state">Loading current Goal and Plan...</div>

    <template v-else>
      <div v-if="!workspace.currentGoal" class="knowledge-state">
        <strong>No current Goal.</strong>
        <span>Create a Goal first, then add plans and daily tasks inside it.</span>
        <RouterLink class="primary-action" to="/study/goals">Create Goal</RouterLink>
      </div>

      <template v-else>
        <section class="home-band" aria-label="Current goal">
          <div>
            <span class="status-pill">{{ goalTypeLabel(workspace.currentGoal.goalType) }}</span>
            <h3>{{ workspace.currentGoal.goalName }}</h3>
            <p>{{ workspace.currentGoal.description || 'Plans and tasks are scoped to this Goal.' }}</p>
          </div>
          <RouterLink class="secondary-action" to="/study/goals">Switch Goal</RouterLink>
        </section>

        <div class="plan-actions">
          <button type="button" :disabled="isSaving || hasPlan" @click="createPlanStructure">
            Create Plan Structure
          </button>
          <span>{{ status }}</span>
        </div>

        <div class="plan-tree" aria-label="Learning plan hierarchy">
          <section class="analytics-section">
            <h3>Long Term Plan</h3>
            <article v-if="workspace.plans.longTermPlans.length" class="chunk-item">
              <strong>{{ workspace.plans.longTermPlans[0].title }}</strong>
              <small>{{ workspace.plans.longTermPlans[0].status }}</small>
            </article>
            <div v-else class="knowledge-state">No long term plan under this Goal.</div>
          </section>

          <section class="analytics-section">
            <h3>Monthly Plan</h3>
            <article v-for="month in workspace.plans.monthlyPlans" :key="month.id" class="chunk-item">
              <strong>{{ month.title }}</strong>
              <p>{{ month.focus }}</p>
            </article>
            <div v-if="!workspace.plans.monthlyPlans.length" class="knowledge-state">
              No monthly plan under this Goal.
            </div>
          </section>

          <section class="analytics-section">
            <h3>Weekly Plan</h3>
            <article v-for="week in workspace.plans.weeklyPlans" :key="week.id" class="chunk-item">
              <strong>{{ week.title }}</strong>
              <p>{{ week.weekStart }} - {{ week.weekEnd }} · {{ week.focus }}</p>
            </article>
            <div v-if="!workspace.plans.weeklyPlans.length" class="knowledge-state">
              No weekly plan under this Goal.
            </div>
          </section>
        </div>

        <section class="home-section">
          <div class="section-heading">
            <h3>Daily Tasks</h3>
            <span>{{ workspace.plans.dailyTasks.length }} tasks in current Goal</span>
          </div>
          <div v-if="workspace.plans.dailyTasks.length" class="task-list">
            <article v-for="task in workspace.plans.dailyTasks" :key="task.id" class="task-row">
              <div class="task-edit">
                <input v-model="task.subject" aria-label="Subject" />
                <input v-model="task.topic" aria-label="Topic" />
                <input v-model="task.taskDate" type="date" aria-label="Task date" />
                <input v-model.number="task.estimatedMinutes" type="number" min="1" aria-label="Minutes" />
              </div>
              <div class="task-actions">
                <span class="status-pill">{{ task.status }}</span>
                <button type="button" @click="saveTask(task)">Save</button>
                <button type="button" :disabled="task.status === 'completed'" @click="markTaskDone(task)">
                  Complete
                </button>
                <RouterLink class="primary-action" :to="`/study/session/new?taskId=${task.id}`">
                  Start Session
                </RouterLink>
              </div>
            </article>
          </div>
          <div v-else class="knowledge-state">
            <span>Add a plan structure to create daily tasks scoped to this Goal.</span>
          </div>
        </section>
      </template>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  completeTask,
  createPlan,
  fetchStudyWorkspace,
  updateTask,
  type DailyTask,
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
    dataQuality: {},
    learningSummary: {},
  },
}

const workspace = ref<StudyWorkspacePayload>(emptyWorkspace)
const loadState = ref('loading')
const isSaving = ref(false)
const status = ref('Plans and tasks belong to the current Goal.')
const hasPlan = computed(() => workspace.value.planSummary.hasPlan)

onMounted(loadWorkspace)

async function loadWorkspace() {
  loadState.value = 'loading'
  workspace.value = await fetchStudyWorkspace()
  loadState.value = 'ready'
}

async function createPlanStructure() {
  if (!workspace.value.currentGoal) {
    return
  }
  isSaving.value = true
  try {
    await createPlan({ startDate: new Date().toISOString().slice(0, 10) })
    status.value = 'Plan hierarchy created for the current Goal.'
    await loadWorkspace()
  } finally {
    isSaving.value = false
  }
}

async function saveTask(task: DailyTask) {
  const updated = await updateTask(task.id, task)
  Object.assign(task, updated)
  status.value = 'Task saved inside the current Goal.'
}

async function markTaskDone(task: DailyTask) {
  const updated = await completeTask(task.id)
  Object.assign(task, updated)
  status.value = 'Task completed.'
}

function goalTypeLabel(type: StudyGoalType) {
  const labels: Record<StudyGoalType, string> = {
    exam: '考试目标',
    learning: '知识学习',
    reading: '阅读目标',
    growth: '成长目标',
  }
  return labels[type]
}
</script>
