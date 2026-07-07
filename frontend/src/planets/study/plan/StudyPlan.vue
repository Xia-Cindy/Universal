<template>
  <section class="study-plan" aria-labelledby="plan-title">
    <p class="eyebrow">Plan</p>
    <h2 id="plan-title">Goal and Learning Plan</h2>

    <form class="study-form" @submit.prevent="submitGoal">
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
      <button type="button" @click="generatePlan">Generate 7-Day Plan</button>
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
          <span>{{ task.status }}</span>
          <button type="button" @click="saveTask(task)">Save</button>
          <button type="button" :disabled="task.status === 'completed'" @click="markTaskDone(task)">
            Complete
          </button>
          <button type="button" @click="recordSession(task)">Record 25 min</button>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  completeTask,
  createGoal,
  createPlan,
  finishSession,
  startSession,
  updateTask,
  type DailyTask,
} from '../../../services/api'

const goalForm = ref({
  goalName: '2027 MEM',
  examName: 'MEM',
  deadline: new Date(Date.now() + 1000 * 60 * 60 * 24 * 120).toISOString().slice(0, 10),
  currentLevel: 'basic',
  dailyAvailableMinutes: 45,
  priority: 'high',
})
const subjectsText = ref('math, english, logic')
const tasks = ref<DailyTask[]>([])
const status = ref('Create a Goal, then generate a plan.')

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

async function recordSession(task: DailyTask) {
  const start = new Date(Date.now() - 25 * 60 * 1000)
  const session = await startSession({
    taskId: task.id,
    startTime: start.toISOString(),
  })
  await finishSession(session.id, {
    endTime: new Date().toISOString(),
    notes: `Recorded learning activity for ${task.topic}`,
    feeling: 'focused',
  })
  status.value = 'Study session recorded.'
}
</script>
