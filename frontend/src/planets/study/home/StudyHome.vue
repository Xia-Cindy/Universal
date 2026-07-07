<template>
  <section class="study-home" aria-labelledby="study-home-title">
    <p class="eyebrow">Primary next action</p>
    <h2 id="study-home-title">{{ title }}</h2>
    <p>{{ description }}</p>
    <RouterLink class="primary-action" :to="primaryRoute">{{ primaryLabel }}</RouterLink>

    <div class="progress-snapshot" aria-label="Progress snapshot">
      <span>Today {{ home.progressSnapshot.todayStudyMinutes }} min</span>
      <span>This week {{ home.progressSnapshot.weekStudyMinutes }} min</span>
      <span>Streak {{ home.progressSnapshot.studyStreakDays }} days</span>
    </div>

    <div v-if="home.todayTasks.length" class="task-list">
      <article v-for="task in home.todayTasks" :key="task.id" class="task-row">
        <div>
          <strong>{{ task.subject }}</strong>
          <span>{{ task.topic }}</span>
        </div>
        <span>{{ task.status }}</span>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchStudyHome } from '../../../services/api'

const home = ref({
  state: 'empty',
  currentGoal: null as null | { goalName: string },
  todayTasks: [] as Array<{ id: string; subject: string; topic: string; status: string }>,
  primaryNextAction: {
    label: 'Create Goal',
    route: '/study/plan',
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
const description = computed(() =>
  home.value.currentGoal
    ? "Today's tasks and progress are ready."
    : 'Study Home will show today’s task, study sessions, and progress once a Goal exists.',
)
const primaryLabel = computed(() => home.value.primaryNextAction.label)
const primaryRoute = computed(() => home.value.primaryNextAction.route)

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
