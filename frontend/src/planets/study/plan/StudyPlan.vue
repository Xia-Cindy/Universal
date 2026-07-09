<template>
  <section class="study-plan" aria-labelledby="plan-title">
    <p class="eyebrow">Plan</p>
    <h2 id="plan-title">Goal and Learning Plan</h2>

    <div v-if="loadState === 'loading'" class="knowledge-state">Loading current plan...</div>

    <template v-else>
      <form v-if="!hasPlan" class="study-form" @submit.prevent="submitGoal">
        <div class="goal-type-picker wide-field" aria-label="Goal type">
          <button
            v-for="option in goalTypes"
            :key="option.value"
            type="button"
            :class="{ selected: goalForm.goalType === option.value }"
            @click="goalForm.goalType = option.value"
          >
            <strong>{{ option.label }}</strong>
            <span>{{ option.description }}</span>
          </button>
        </div>
        <label>
          Goal
          <input v-model="goalForm.goalName" required />
        </label>
        <label>
          Deadline
          <input v-model="goalForm.deadline" type="date" />
        </label>
        <label class="wide-field">
          Description
          <textarea v-model="goalForm.description" rows="3" />
        </label>
        <label>
          Subjects
          <input v-model="subjectsText" placeholder="math, systems, AI engineering" required />
        </label>
        <label>
          Current level
          <input v-model="goalForm.currentLevel" required />
        </label>
        <label>
          Daily minutes
          <input v-model.number="goalForm.dailyAvailableMinutes" type="number" min="1" required />
        </label>
        <button type="submit">Save Goal</button>
      </form>

      <div class="plan-actions">
        <button type="button" @click="generatePlan">Create 7-Day Plan</button>
        <RouterLink class="primary-action" to="/study/onboarding">Onboarding</RouterLink>
        <span>{{ status }}</span>
      </div>

      <div v-if="currentPlan" class="plan-hierarchy" aria-label="Learning plan hierarchy">
        <section class="analytics-section">
          <h3>Long Term Plan</h3>
          <p>{{ currentPlan.yearPlan.title }}</p>
          <small>{{ currentPlan.yearPlan.planType }}</small>
        </section>
        <section class="analytics-section">
          <h3>Monthly Plan</h3>
          <article v-for="month in currentPlan.monthPlans" :key="month.id" class="chunk-item">
            <strong>{{ month.title }}</strong>
            <p>{{ month.focus }}</p>
          </article>
        </section>
        <section class="analytics-section">
          <h3>Weekly Plan</h3>
          <article v-for="week in currentPlan.weekPlans" :key="week.id" class="chunk-item">
            <strong>{{ week.title }}</strong>
            <p>{{ week.weekStart }} - {{ week.weekEnd }} · {{ week.focus }}</p>
          </article>
        </section>
      </div>

      <div v-if="tasks.length" class="task-list">
        <h3>Daily Tasks</h3>
        <article v-for="task in tasks" :key="task.id" class="task-row">
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
        <span>No Daily Tasks are available for the current Goal.</span>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  completeTask,
  createGoal,
  createPlan,
  fetchCurrentPlan,
  updateTask,
  type DailyTask,
  type StudyGoalType,
} from '../../../services/api'

const goalTypes: Array<{ value: StudyGoalType; label: string; description: string }> = [
  { value: 'exam', label: '考试目标', description: '面向考试或证书' },
  { value: 'learning', label: '知识学习', description: '学习课程或主题' },
  { value: 'reading', label: '阅读目标', description: '阅读一本书或一组资料' },
  { value: 'growth', label: '成长目标', description: '长期能力建设' },
]
const goalForm = ref({
  goalType: 'learning' as StudyGoalType,
  goalName: '',
  deadline: '',
  description: '',
  currentLevel: '',
  dailyAvailableMinutes: 60,
  priority: 'medium',
})
const subjectsText = ref('')
const tasks = ref<DailyTask[]>([])
const currentPlan = ref<Record<string, any> | null>(null)
const status = ref('Create a Goal or load the current Plan.')
const loadState = ref('loading')
const hasPlan = computed(() => tasks.value.length > 0)

onMounted(loadCurrentPlan)

async function loadCurrentPlan() {
  loadState.value = 'loading'
  try {
    const plan = await fetchCurrentPlan()
    currentPlan.value = plan
    tasks.value = plan?.dailyTasks || []
    status.value = tasks.value.length ? 'Current Plan loaded.' : 'No active Plan yet.'
  } catch {
    status.value = 'No active Plan yet.'
  } finally {
    loadState.value = 'ready'
  }
}

async function submitGoal() {
  await createGoal({
    ...goalForm.value,
    deadline: goalForm.value.deadline || null,
    examName: goalForm.value.goalType === 'exam' ? goalForm.value.goalName : null,
    subjects: subjectsText.value
      .split(',')
      .map((subject) => subject.trim())
      .filter(Boolean),
  })
  status.value = 'Goal saved.'
}

async function generatePlan() {
  const plan = await createPlan({ startDate: new Date().toISOString().slice(0, 10) })
  currentPlan.value = plan
  tasks.value = plan.dailyTasks
  status.value = 'Plan generated.'
}

async function saveTask(task: DailyTask) {
  const updated = await updateTask(task.id, task)
  Object.assign(task, updated)
  status.value = 'Task saved.'
}

async function markTaskDone(task: DailyTask) {
  const updated = await completeTask(task.id)
  Object.assign(task, updated)
  status.value = 'Task completed.'
}
</script>
