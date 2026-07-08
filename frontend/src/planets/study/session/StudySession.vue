<template>
  <section class="study-plan" aria-labelledby="session-title">
    <p class="eyebrow">Study Session</p>
    <h2 id="session-title">{{ task ? task.subject : sessionForm.subject }}</h2>

    <div v-if="task" class="home-band">
      <div>
        <span class="status-pill">{{ task.status }}</span>
        <h3>{{ task.topic }}</h3>
        <p>{{ task.estimatedMinutes }} min planned</p>
      </div>
    </div>

    <form v-if="!activeSession" class="study-form" @submit.prevent="start">
      <label>
        Subject
        <input v-model="sessionForm.subject" :disabled="Boolean(task)" required />
      </label>
      <label>
        Topic
        <input v-model="sessionForm.topic" :disabled="Boolean(task)" required />
      </label>
      <button type="submit">Start Session</button>
      <span>{{ status }}</span>
    </form>

    <div v-else-if="!finishedSession" class="session-active">
      <strong>{{ elapsedMinutes }} min</strong>
      <span>{{ activeSession.subject }} / {{ activeSession.topic }}</span>
      <label>
        Notes
        <textarea v-model="finishForm.notes" rows="3"></textarea>
      </label>
      <label>
        Feeling
        <input v-model="finishForm.feeling" />
      </label>
      <button type="button" @click="finish">Finish Session</button>
    </div>

    <div v-else class="knowledge-state">
      <strong>{{ finishedSession.durationMinutes }} minutes saved.</strong>
      <span>{{ finishedSession.subject }} / {{ finishedSession.topic }}</span>
      <RouterLink class="primary-action" to="/study">Back to Home</RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  fetchCurrentPlan,
  finishExecutionSession,
  startExecutionSession,
  type DailyTask,
} from '../../../services/api'

interface StudySessionPayload {
  id: string
  subject: string
  topic: string
  startTime: string
  durationMinutes: number
}

const route = useRoute()
const task = ref<DailyTask | null>(null)
const activeSession = ref<StudySessionPayload | null>(null)
const finishedSession = ref<StudySessionPayload | null>(null)
const status = ref('Ready to start.')
const now = ref(Date.now())
const intervalId = ref<number | null>(null)
const sessionForm = ref({
  subject: '',
  topic: '',
})
const finishForm = ref({
  notes: '',
  feeling: '',
})

const elapsedMinutes = computed(() => {
  if (!activeSession.value) {
    return 0
  }
  const started = new Date(activeSession.value.startTime).getTime()
  return Math.max(Math.floor((now.value - started) / 60000), 0)
})

onMounted(async () => {
  const taskId = String(route.query.taskId || '')
  if (taskId) {
    const plan = await fetchCurrentPlan()
    task.value = plan?.dailyTasks.find((item: DailyTask) => item.id === taskId) || null
    if (task.value) {
      sessionForm.value.subject = task.value.subject
      sessionForm.value.topic = task.value.topic
    }
  }
})

onBeforeUnmount(() => {
  if (intervalId.value !== null) {
    window.clearInterval(intervalId.value)
  }
})

async function start() {
  const response = await startExecutionSession({
    taskId: task.value?.id,
    subject: sessionForm.value.subject,
    topic: sessionForm.value.topic,
    startTime: new Date().toISOString(),
  })
  activeSession.value = response.session
  status.value = 'Session active.'
  intervalId.value = window.setInterval(() => {
    now.value = Date.now()
  }, 1000)
}

async function finish() {
  if (!activeSession.value) {
    return
  }
  const response = await finishExecutionSession(activeSession.value.id, {
    endTime: new Date(Date.now() + 60000).toISOString(),
    notes: finishForm.value.notes,
    feeling: finishForm.value.feeling,
  })
  finishedSession.value = response.session
  if (intervalId.value !== null) {
    window.clearInterval(intervalId.value)
    intervalId.value = null
  }
}
</script>
