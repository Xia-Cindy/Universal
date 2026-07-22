<template>
  <section class="study-plan" aria-labelledby="plan-title">
    <p class="eyebrow">Plan</p>
    <h2 id="plan-title">学习计划</h2>

    <div v-if="loadState === 'loading'" class="knowledge-state">Loading current Goal and Plan...</div>

    <template v-else>
      <div v-if="!workspace.currentGoal" class="knowledge-state">
        <strong>No current Goal.</strong>
        <span>Create a Goal first, then add plans and daily tasks inside it.</span>
        <RouterLink class="primary-action" to="/study/goals">Create Goal</RouterLink>
      </div>

      <template v-else>
        <section class="home-band compact-goal-band" aria-label="Current goal">
          <div>
            <span class="status-pill">{{ goalTypeLabel(workspace.currentGoal.goalType) }}</span>
            <h3>{{ workspace.currentGoal.goalName }} 的推进路线</h3>
            <p>{{ workspace.currentGoal.description || 'Plans and tasks are scoped to this Goal.' }}</p>
          </div>
          <RouterLink class="secondary-action" to="/study/goals">Switch Goal</RouterLink>
        </section>

        <div v-if="!hasPlan" class="plan-empty-state">
          <h3>创建一条计划结构</h3>
          <p>
            Universe OS 会为当前 Goal 创建基础路线：长期计划、月计划、周计划和每日任务。
            结构创建后，你可以继续编辑每日任务。
          </p>
          <button type="button" :disabled="isSaving || hasPlan" @click="createPlanStructure">
            Create Plan Structure
          </button>
          <span>{{ status }}</span>
        </div>

        <div v-else class="plan-roadmap" aria-label="Learning plan route">
          <article class="roadmap-step">
            <span class="step-index">1</span>
            <div>
              <p class="eyebrow">长期计划</p>
              <h3>{{ currentLongTermPlan?.title || 'No long term plan yet' }}</h3>
              <small>{{ currentLongTermPlan?.status || 'missing' }}</small>
              <form v-if="currentLongTermPlan" class="inline-edit-form" @submit.prevent="saveYearPlan">
                <label>
                  Title
                  <input v-model="planEdit.yearTitle" required />
                </label>
                <button type="submit" :disabled="isSaving">Save Long Term Plan</button>
              </form>
            </div>
          </article>

          <article class="roadmap-step">
            <span class="step-index">2</span>
            <div>
              <p class="eyebrow">月计划</p>
              <h3>{{ currentMonthlyPlan?.title || 'No monthly plan yet' }}</h3>
              <p>{{ currentMonthlyPlan?.focus || 'Create the plan structure first.' }}</p>
              <form v-if="currentMonthlyPlan" class="inline-edit-form" @submit.prevent="saveMonthPlan">
                <label>
                  Title
                  <input v-model="planEdit.monthTitle" required />
                </label>
                <label>
                  Focus
                  <textarea v-model="planEdit.monthFocus" rows="2" required />
                </label>
                <button type="submit" :disabled="isSaving">Save Monthly Plan</button>
              </form>
            </div>
          </article>

          <article class="roadmap-step">
            <span class="step-index">3</span>
            <div>
              <p class="eyebrow">周计划</p>
              <h3>{{ currentWeeklyPlan?.title || 'No weekly plan yet' }}</h3>
              <p>
                {{ currentWeeklyPlan ? `${currentWeeklyPlan.weekStart} - ${currentWeeklyPlan.weekEnd}` : '' }}
                <span v-if="currentWeeklyPlan"> · {{ currentWeeklyPlan.focus }}</span>
              </p>
              <form v-if="currentWeeklyPlan" class="inline-edit-form" @submit.prevent="saveWeekPlan">
                <label>
                  Title
                  <input v-model="planEdit.weekTitle" required />
                </label>
                <label>
                  Focus
                  <textarea v-model="planEdit.weekFocus" rows="2" required />
                </label>
                <button type="submit" :disabled="isSaving">Save Weekly Plan</button>
              </form>
            </div>
          </article>

          <article class="roadmap-step">
            <span class="step-index">4</span>
            <div>
              <p class="eyebrow">每日任务</p>
              <h3>{{ workspace.planSummary.dailyTaskCount }} 个任务</h3>
              <p>当前 Goal 已完成 {{ workspace.planSummary.completedTaskCount }} 个任务。</p>
            </div>
          </article>
        </div>

        <section class="home-section">
          <div class="section-heading">
            <h3>每日任务</h3>
            <span>当前 Goal 下有 {{ workspace.plans.dailyTasks.length }} 个任务</span>
          </div>
          <div v-if="workspace.plans.dailyTasks.length" class="task-list">
            <article v-for="task in sortedTasks" :key="task.id" class="task-row readable-task">
              <div>
                <span class="status-pill">{{ task.status }}</span>
                <strong>{{ task.subject }}</strong>
                <span>{{ task.topic }}</span>
                <small>{{ task.taskDate }} · {{ task.estimatedMinutes }} min</small>
              </div>
              <div class="task-actions">
                <button type="button" :disabled="task.status === 'completed'" @click="markTaskDone(task)">
                  Complete
                </button>
                <RouterLink
                  v-if="task.status !== 'completed'"
                  class="primary-action"
                  :to="`/study/session/new?taskId=${task.id}`"
                >
                  Start Session
                </RouterLink>
                <RouterLink v-else class="secondary-action" to="/study/analytics">
                  View Progress
                </RouterLink>
              </div>
              <div class="task-edit-panel">
                <p class="eyebrow">编辑任务</p>
                <div class="task-edit">
                  <label>
                    Subject
                    <input v-model="task.subject" aria-label="Subject" />
                  </label>
                  <label>
                    Topic
                    <input v-model="task.topic" aria-label="Topic" />
                  </label>
                  <label>
                    Date
                    <input v-model="task.taskDate" type="date" aria-label="Task date" />
                  </label>
                  <label>
                    Minutes
                    <input v-model.number="task.estimatedMinutes" type="number" min="1" aria-label="Minutes" />
                  </label>
                </div>
                <button type="button" @click="saveTask(task)">Save Task</button>
              </div>
            </article>
          </div>
          <div v-else class="knowledge-state">
            <span>先创建计划结构，再为当前 Goal 安排每日任务。</span>
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
  updateMonthPlan,
  updateWeekPlan,
  updateYearPlan,
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
    dataQuality: {},
    learningSummary: {},
  },
}

const workspace = ref<StudyWorkspacePayload>(emptyWorkspace)
const loadState = ref('loading')
const isSaving = ref(false)
const status = ref('Plans and tasks belong to the current Goal.')
const planEdit = ref({
  yearTitle: '',
  monthTitle: '',
  monthFocus: '',
  weekTitle: '',
  weekFocus: '',
})
const hasPlan = computed(() => workspace.value.planSummary.hasPlan)
const currentLongTermPlan = computed(() => workspace.value.plans.longTermPlans[0])
const currentMonthlyPlan = computed(() => workspace.value.plans.monthlyPlans[0])
const currentWeeklyPlan = computed(() => workspace.value.plans.weeklyPlans[0])
const sortedTasks = computed(() =>
  [...workspace.value.plans.dailyTasks].sort((left, right) =>
    `${left.taskDate}-${left.id}`.localeCompare(`${right.taskDate}-${right.id}`),
  ),
)

onMounted(loadWorkspace)

async function loadWorkspace() {
  loadState.value = 'loading'
  workspace.value = await fetchStudyWorkspace()
  syncPlanEditForm()
  loadState.value = 'ready'
}

function syncPlanEditForm() {
  planEdit.value = {
    yearTitle: currentLongTermPlan.value?.title || '',
    monthTitle: currentMonthlyPlan.value?.title || '',
    monthFocus: currentMonthlyPlan.value?.focus || '',
    weekTitle: currentWeeklyPlan.value?.title || '',
    weekFocus: currentWeeklyPlan.value?.focus || '',
  }
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

async function saveYearPlan() {
  if (!currentLongTermPlan.value?.id) {
    return
  }
  isSaving.value = true
  try {
    await updateYearPlan(currentLongTermPlan.value.id, { title: planEdit.value.yearTitle })
    status.value = 'Long term plan saved.'
    await loadWorkspace()
  } finally {
    isSaving.value = false
  }
}

async function saveMonthPlan() {
  if (!currentMonthlyPlan.value?.id) {
    return
  }
  isSaving.value = true
  try {
    await updateMonthPlan(currentMonthlyPlan.value.id, {
      title: planEdit.value.monthTitle,
      focus: planEdit.value.monthFocus,
    })
    status.value = 'Monthly plan saved.'
    await loadWorkspace()
  } finally {
    isSaving.value = false
  }
}

async function saveWeekPlan() {
  if (!currentWeeklyPlan.value?.id) {
    return
  }
  isSaving.value = true
  try {
    await updateWeekPlan(currentWeeklyPlan.value.id, {
      title: planEdit.value.weekTitle,
      focus: planEdit.value.weekFocus,
    })
    status.value = 'Weekly plan saved.'
    await loadWorkspace()
  } finally {
    isSaving.value = false
  }
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
