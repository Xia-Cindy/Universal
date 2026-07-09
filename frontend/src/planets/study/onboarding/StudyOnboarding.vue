<template>
  <section class="study-plan" aria-labelledby="onboarding-title">
    <p class="eyebrow">Study Onboarding</p>
    <h2 id="onboarding-title">Initialize Study Planet</h2>

    <div v-if="state === 'ready' && activeGoal" class="knowledge-state">
      <strong>{{ activeGoal.goalName }}</strong>
      <span>{{ goalTypeLabel(activeGoal.goalType) }} · {{ activeGoal.deadline || 'Long-term' }}</span>
      <RouterLink class="primary-action" to="/study">Enter Study Home</RouterLink>
    </div>

    <form v-else class="study-form" @submit.prevent="submit">
      <div class="goal-type-picker wide-field" aria-label="Goal type">
        <button
          v-for="option in goalTypes"
          :key="option.value"
          type="button"
          :class="{ selected: form.goalType === option.value }"
          @click="form.goalType = option.value"
        >
          <strong>{{ option.label }}</strong>
          <span>{{ option.description }}</span>
        </button>
      </div>
      <label>
        Goal name
        <input v-model="form.goalName" required />
      </label>
      <label>
        Deadline
        <input v-model="form.deadline" type="date" />
      </label>
      <label class="wide-field">
        Description
        <textarea v-model="form.description" rows="3" />
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
        Subjects or topics
        <input v-model="subjectsText" placeholder="systems, AI engineering, math" required />
      </label>
      <button type="submit">Create Goal</button>
      <span>{{ status }}</span>
    </form>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  createOnboardingGoal,
  fetchStudyOnboarding,
  type StudyGoalType,
} from '../../../services/api'

const state = ref<'needs_onboarding' | 'ready'>('needs_onboarding')
const activeGoal = ref<Record<string, any> | null>(null)
const subjectsText = ref('')
const status = ref('Study Planet will open after the Goal is created.')
const goalTypes: Array<{ value: StudyGoalType; label: string; description: string }> = [
  { value: 'exam', label: '考试目标', description: '有明确考试或截止日期' },
  { value: 'learning', label: '知识学习', description: '学习一本书、一门课或一个主题' },
  { value: 'growth', label: '成长目标', description: '长期能力建设和职业成长' },
]
const form = ref({
  goalType: 'learning' as StudyGoalType,
  goalName: '',
  deadline: '',
  description: '',
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
    deadline: form.value.deadline || null,
    examName: form.value.goalType === 'exam' ? form.value.goalName : null,
    subjects: subjectsText.value
      .split(',')
      .map((subject) => subject.trim())
      .filter(Boolean),
  })
  state.value = onboarding.state
  activeGoal.value = onboarding.activeGoal
  status.value = 'Goal created.'
}

function goalTypeLabel(type: string) {
  return goalTypes.find((option) => option.value === type)?.label || '学习目标'
}
</script>
