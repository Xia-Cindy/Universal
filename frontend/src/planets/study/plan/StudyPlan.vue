<template>
  <section class="study-plan" aria-labelledby="plan-title">
    <p class="eyebrow">Plan</p>
    <h2 id="plan-title">Goal and Learning Plan</h2>

    <div v-if="loadState === 'loading'" class="knowledge-state">Loading current plan...</div>

    <template v-else>
      <form v-if="!hasPlan" class="study-form" @submit.prevent="submitGoal">
        <label>
          Goal
          <input v-model="goalForm.goalName" required />
        </label>
        <label>
          Exam
          <input v-model="goalForm.examName" required />
        </label>
        <label>
          Deadline
          <input v-model="goalForm.deadline" type="date" required />
        </label>
        <label>
          Subjects
          <input v-model="subjectsText" placeholder="math, english, logic" required />
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

      <div v-if="tasks.length" class="task-list">
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
} from '../../../services/api'

const goalForm = ref({
  goalName: '',
  examName: '',
  deadline: '',
  currentLevel: '',
  dailyAvailableMinutes: 60,
  priority: 'medium',
})
const subjectsText = ref('')
const tasks = ref<DailyTask[]>([])
const status = ref('Create a Goal or load the current Plan.')
const loadState = ref('loading')
const hasPlan = computed(() => tasks.value.length > 0)

onMounted(loadCurrentPlan)

async function loadCurrentPlan() {
  loadState.value = 'loading'
  try {
    const plan = await fetchCurrentPlan()
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
    subjects: subjectsText.value
      .split(',')
      .map((subject) => subject.trim())
      .filter(Boolean),
  })
  status.value = 'Goal saved.'
}

async function generatePlan() {
  const plan = await createPlan({ startDate: new Date().toISOString().slice(0, 10) })
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
