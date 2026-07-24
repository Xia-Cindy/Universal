<template>
  <section class="study-plan" aria-labelledby="plan-title">
    <p class="eyebrow">Plan</p>
    <h2 id="plan-title">学习计划</h2>

    <div v-if="loadState === 'loading'" class="knowledge-state">Loading current Goal and Plan...</div>

    <template v-else>
      <div v-if="!workspace.currentGoal" class="knowledge-state">
        <strong>No current Goal.</strong>
        <span>Create a Goal first, then add plans and daily tasks inside it.</span>
        <RouterLink class="primary-action" to="/study/goals/new">Create Goal</RouterLink>
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

        <section class="home-section plan-builder-section" aria-labelledby="plan-builder-title">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Plan Builder</p>
              <h3 id="plan-builder-title">按路线添加计划节点</h3>
            </div>
            <span>所有节点必须挂在当前 Goal 下</span>
          </div>
          <form class="plan-node-form" @submit.prevent="addPlanNode">
            <label>
              层级
              <select v-model="nodeForm.planType">
                <option value="long_term">长期计划</option>
                <option value="monthly">月计划</option>
                <option value="weekly">周计划</option>
                <option value="daily">每日任务</option>
              </select>
            </label>
            <label class="wide-field">
              标题
              <input v-model="nodeForm.title" required placeholder="例如：完成操作系统内存章节" />
            </label>
            <label v-if="nodeForm.planType === 'monthly'">
              所属长期计划
              <select v-model="nodeForm.yearPlanId" required>
                <option value="" disabled>选择长期计划</option>
                <option v-for="plan in workspace.plans.longTermPlans" :key="plan.id" :value="plan.id">{{ plan.title }}</option>
              </select>
            </label>
            <label v-if="nodeForm.planType === 'weekly'">
              所属月计划
              <select v-model="nodeForm.monthPlanId" required>
                <option value="" disabled>选择月计划</option>
                <option v-for="plan in workspace.plans.monthlyPlans" :key="plan.id" :value="plan.id">{{ plan.title }}</option>
              </select>
            </label>
            <label v-if="nodeForm.planType === 'daily'">
              所属周计划
              <select v-model="nodeForm.weekPlanId" required>
                <option value="" disabled>选择周计划</option>
                <option v-for="plan in workspace.plans.weeklyPlans" :key="plan.id" :value="plan.id">{{ plan.title }}</option>
              </select>
            </label>
            <label v-if="nodeForm.planType === 'daily'">
              日期
              <input v-model="nodeForm.taskDate" type="date" required />
            </label>
            <label v-if="nodeForm.planType === 'daily'">
              分钟
              <input v-model.number="nodeForm.estimatedMinutes" type="number" min="1" required />
            </label>
            <label v-if="nodeForm.planType === 'daily'">
              科目
              <input v-model="nodeForm.subject" required placeholder="科目" />
            </label>
            <label v-if="nodeForm.planType === 'daily'">
              优先级
              <select v-model="nodeForm.priority">
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
              </select>
            </label>
            <label v-if="['monthly', 'weekly'].includes(nodeForm.planType)" class="wide-field">
              重点
              <input v-model="nodeForm.focus" placeholder="这一层要推进什么？" />
            </label>
            <label v-if="nodeForm.planType === 'daily'" class="wide-field">
              主题
              <input v-model="nodeForm.topic" required placeholder="具体要完成的学习内容" />
            </label>
            <button type="submit" :disabled="isSaving">添加到路线</button>
          </form>
          <p class="surface-copy">{{ status }}</p>
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

        <section v-if="hasPlan" class="home-section plan-calendar-section" aria-labelledby="plan-calendar-title">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Calendar</p>
              <h3 id="plan-calendar-title">本周任务日历</h3>
            </div>
            <span>{{ calendarSummary }}</span>
          </div>
          <div class="plan-calendar" role="list" aria-label="Daily task calendar">
            <article
              v-for="day in calendarDays"
              :key="day.date"
              class="calendar-day"
              :class="{ today: day.isToday, empty: !day.tasks.length }"
              role="listitem"
            >
              <div class="calendar-day-heading">
                <span>{{ day.weekday }}</span>
                <strong>{{ day.dayLabel }}</strong>
              </div>
              <div v-if="day.tasks.length" class="calendar-task-stack">
                <button
                  v-for="task in day.tasks"
                  :key="task.id"
                  type="button"
                  class="calendar-task"
                  :class="[task.status, priorityClass(task.priority)]"
                  @click="focusTask(task.id)"
                >
                  <span>{{ task.subject }}</span>
                  <small>{{ task.topic }}</small>
                  <em>{{ priorityLabel(task.priority) }} · {{ task.estimatedMinutes }} min</em>
                </button>
              </div>
              <p v-else class="surface-copy">No task</p>
            </article>
          </div>
        </section>

        <section class="home-section">
          <div class="section-heading">
            <h3>每日任务</h3>
            <span>当前 Goal 下有 {{ workspace.plans.dailyTasks.length }} 个任务</span>
          </div>
          <div v-if="workspace.plans.dailyTasks.length" class="task-list">
            <article
              v-for="task in sortedTasks"
              :key="task.id"
              class="task-row readable-task"
              :data-task-id="task.id"
            >
              <div>
                <span class="status-pill">{{ task.status }}</span>
                <span class="status-pill priority-pill">{{ priorityLabel(task.priority) }}</span>
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
                <button type="button" class="secondary-action" @click="moveTask(task, -1)">上移</button>
                <button type="button" class="secondary-action" @click="moveTask(task, 1)">下移</button>
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
                  <label>
                    Priority
                    <select v-model="task.priority" aria-label="Priority">
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
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
  createPlanNode,
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
    route: '/study/goals/new',
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
const nodeForm = ref({
  planType: 'long_term',
  title: '',
  focus: '',
  yearPlanId: '',
  monthPlanId: '',
  weekPlanId: '',
  taskDate: new Date().toISOString().slice(0, 10),
  subject: '',
  topic: '',
  estimatedMinutes: 30,
  priority: 'medium',
})
const hasPlan = computed(() => workspace.value.planSummary.hasPlan)
const currentLongTermPlan = computed(() => workspace.value.plans.longTermPlans[0])
const currentMonthlyPlan = computed(() => workspace.value.plans.monthlyPlans[0])
const currentWeeklyPlan = computed(() => workspace.value.plans.weeklyPlans[0])
const sortedTasks = computed(() =>
  [...workspace.value.plans.dailyTasks].sort((left, right) =>
    `${left.taskDate}-${String(left.sortOrder ?? 0).padStart(5, '0')}-${left.id}`.localeCompare(
      `${right.taskDate}-${String(right.sortOrder ?? 0).padStart(5, '0')}-${right.id}`,
    ),
  ),
)
const calendarDays = computed(() => buildCalendarDays(sortedTasks.value))
const calendarSummary = computed(() => {
  const totalMinutes = sortedTasks.value.reduce((sum, task) => sum + Number(task.estimatedMinutes || 0), 0)
  const highCount = sortedTasks.value.filter((task) => task.priority === 'high').length
  return `${sortedTasks.value.length} tasks · ${totalMinutes} min · ${highCount} high priority`
})

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

async function addPlanNode() {
  isSaving.value = true
  try {
    await createPlanNode({
      planType: nodeForm.value.planType,
      title: nodeForm.value.title,
      focus: nodeForm.value.focus,
      yearPlanId: nodeForm.value.yearPlanId || undefined,
      monthPlanId: nodeForm.value.monthPlanId || undefined,
      weekPlanId: nodeForm.value.weekPlanId || undefined,
      taskDate: nodeForm.value.taskDate,
      subject: nodeForm.value.subject,
      topic: nodeForm.value.topic,
      estimatedMinutes: nodeForm.value.estimatedMinutes,
      priority: nodeForm.value.priority,
      sortOrder: workspace.value.plans.dailyTasks.length,
    })
    status.value = 'Plan node added to the current Goal route.'
    nodeForm.value.title = ''
    nodeForm.value.focus = ''
    nodeForm.value.subject = ''
    nodeForm.value.topic = ''
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

async function moveTask(task: DailyTask, direction: -1 | 1) {
  const sameDay = sortedTasks.value.filter((item) => item.taskDate === task.taskDate)
  const index = sameDay.findIndex((item) => item.id === task.id)
  const target = sameDay[index + direction]
  if (!target) return
  const currentOrder = task.sortOrder ?? index
  const targetOrder = target.sortOrder ?? index + direction
  await Promise.all([
    updateTask(task.id, { sortOrder: targetOrder }),
    updateTask(target.id, { sortOrder: currentOrder }),
  ])
  status.value = 'Task order updated.'
  await loadWorkspace()
}

function buildCalendarDays(tasks: DailyTask[]) {
  const start = currentWeeklyPlan.value?.weekStart || tasks[0]?.taskDate || new Date().toISOString().slice(0, 10)
  const startDate = parseDate(start)
  const today = new Date().toISOString().slice(0, 10)
  return Array.from({ length: 7 }, (_, offset) => {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + offset)
    const isoDate = toIsoDate(date)
    return {
      date: isoDate,
      weekday: weekdayLabel(date),
      dayLabel: `${date.getMonth() + 1}/${date.getDate()}`,
      isToday: isoDate === today,
      tasks: tasks.filter((task) => task.taskDate === isoDate),
    }
  })
}

function parseDate(value: string) {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function toIsoDate(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function weekdayLabel(date: Date) {
  return ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date.getDay()]
}

function focusTask(taskId: string) {
  const element = document.querySelector(`[data-task-id="${taskId}"]`)
  element?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

function priorityLabel(priority: DailyTask['priority']) {
  const labels: Record<DailyTask['priority'], string> = {
    high: 'High',
    medium: 'Medium',
    low: 'Low',
  }
  return labels[priority] || 'Medium'
}

function priorityClass(priority: DailyTask['priority']) {
  return `priority-${priority || 'medium'}`
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
