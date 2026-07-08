<template>
  <section class="study-plan" aria-labelledby="onboarding-title">
    <p class="eyebrow">Study Onboarding</p>
    <h2 id="onboarding-title">Initialize Study Planet</h2>

    <div v-if="state === 'ready' && activeGoal" class="knowledge-state">
      <strong>{{ activeGoal.goalName }}</strong>
      <span>{{ activeGoal.examName }} · {{ activeGoal.deadline }}</span>
      <RouterLink class="primary-action" to="/study">Enter Study Home</RouterLink>
    </div>

    <form v-else class="study-form" @submit.prevent="submit">
      <label>
        Goal name
        <input v-model="form.goalName" required />
      </label>
      <label>
        Exam name
        <input v-model="form.examName" required />
      </label>
      <label>
        Target direction
        <input v-model="form.targetDirection" required />
      </label>
      <label>
        Deadline
        <input v-model="form.deadline" type="date" required />
      </label>
      <label>
        Daily minutes
        <input v-model.number="form.dailyAvailableMinutes" type="number" min="1" required />
      </label>
      <label>
        Current level
        <input v-model="form.currentLevel" required />
      </label>
      <label class="wide-field">
        Subjects
        <input v-model="subjectsText" placeholder="math, english, logic" required />
      </label>
      <button type="submit">Create Goal</button>
      <span>{{ status }}</span>
    </form>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { createOnboardingGoal, fetchStudyOnboarding } from '../../../services/api'

const state = ref<'needs_onboarding' | 'ready'>('needs_onboarding')
const activeGoal = ref<Record<string, any> | null>(null)
const subjectsText = ref('')
const status = ref('Study Planet will open after the Goal is created.')
const form = ref({
  goalName: '',
  examName: '',
  targetDirection: '',
  deadline: '',
  dailyAvailableMinutes: 60,
  currentLevel: '',
  priority: 'medium',
})

onMounted(async () => {
  const onboarding = await fetchStudyOnboarding()
  state.value = onboarding.state
  activeGoal.value = onboarding.activeGoal
})

async function submit() {
  const onboarding = await createOnboardingGoal({
    ...form.value,
    subjects: subjectsText.value
      .split(',')
      .map((subject) => subject.trim())
      .filter(Boolean),
  })
  state.value = onboarding.state
  activeGoal.value = onboarding.activeGoal
  status.value = 'Goal created.'
}
</script>
