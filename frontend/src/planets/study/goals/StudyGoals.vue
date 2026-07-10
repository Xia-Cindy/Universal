<template>
  <section class="study-plan" aria-labelledby="goals-title">
    <p class="eyebrow">Goals</p>
    <h2 id="goals-title">Study Goals</h2>

    <div v-if="loadState === 'loading'" class="knowledge-state">Loading Goals...</div>

    <template v-else>
      <section class="home-section">
        <div class="section-heading">
          <h3>Your learning directions</h3>
          <RouterLink class="secondary-action" to="/study/plan">Open Plan</RouterLink>
        </div>
        <div v-if="goals.length" class="goal-list">
          <article
            v-for="goal in goals"
            :key="goal.id"
            class="knowledge-document"
            :class="{ selected: goal.id === activeGoalId }"
          >
            <div>
              <span class="status-pill">{{ goalTypeLabel(goal.goalType) }}</span>
              <h3>{{ goal.goalName }}</h3>
              <p class="surface-copy">{{ goal.description || fallbackDescription(goal.goalType) }}</p>
              <small>{{ goal.deadline || 'No deadline' }} · {{ goal.status }}</small>
            </div>
            <button type="button" :disabled="goal.id === activeGoalId" @click="switchGoal(goal.id)">
              {{ goal.id === activeGoalId ? 'Current' : 'Switch' }}
            </button>
          </article>
        </div>
        <div v-else class="knowledge-state">
          <strong>No Goal yet.</strong>
          <span>Create one Goal to start connecting plans, tasks, and Knowledge.</span>
        </div>
      </section>

      <form class="study-form" @submit.prevent="submitGoal">
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
          Goal title
          <input v-model="form.goalName" required />
        </label>
        <label>
          Deadline
          <input v-model="form.deadline" type="date" />
        </label>
        <label>
          Daily minutes
          <input v-model.number="form.dailyAvailableMinutes" min="1" required type="number" />
        </label>
        <label>
          Current level
          <input v-model="form.currentLevel" required />
        </label>
        <label class="wide-field">
          Subjects
          <input v-model="subjectsText" required placeholder="systems, algorithms, English" />
        </label>
        <label class="wide-field">
          Description
          <textarea v-model="form.description" rows="3" />
        </label>
        <div class="knowledge-actions">
          <button type="submit">Create Goal</button>
          <span>{{ statusMessage }}</span>
        </div>
      </form>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  createGoal,
  fetchStudyWorkspace,
  switchStudyGoal,
  type StudyGoal,
  type StudyGoalType,
} from '../../../services/api'

const goalTypes: Array<{ value: StudyGoalType; label: string; description: string }> = [
  { value: 'exam', label: '考试目标', description: '考试、证书或申请节点' },
  { value: 'reading', label: '阅读目标', description: '一本书或一组资料' },
  { value: 'learning', label: '知识学习', description: '课程、主题或技能' },
  { value: 'growth', label: '成长目标', description: '长期能力建设' },
]

const goals = ref<StudyGoal[]>([])
const activeGoalId = ref('')
const loadState = ref('loading')
const statusMessage = ref('Create a Goal, then build Plans inside it.')
const form = ref({
  goalType: 'learning' as StudyGoalType,
  goalName: '',
  deadline: '',
  description: '',
  currentLevel: '',
  dailyAvailableMinutes: 60,
  priority: 'medium',
})
const subjectsText = ref('')

const subjects = computed(() =>
  subjectsText.value
    .split(',')
    .map((subject) => subject.trim())
    .filter(Boolean),
)

onMounted(loadGoals)

async function loadGoals() {
  loadState.value = 'loading'
  const workspace = await fetchStudyWorkspace()
  goals.value = workspace.goals
  activeGoalId.value = workspace.currentGoal?.id || ''
  loadState.value = 'ready'
}

async function submitGoal() {
  const goal = await createGoal({
    ...form.value,
    deadline: form.value.deadline || null,
    examName: form.value.goalType === 'exam' ? form.value.goalName : null,
    subjects: subjects.value,
  })
  statusMessage.value = 'Goal created and selected.'
  await switchStudyGoal(goal.id)
  resetForm()
  await loadGoals()
}

async function switchGoal(goalId: string) {
  await switchStudyGoal(goalId)
  statusMessage.value = 'Current Goal switched.'
  await loadGoals()
}

function resetForm() {
  form.value = {
    goalType: 'learning',
    goalName: '',
    deadline: '',
    description: '',
    currentLevel: '',
    dailyAvailableMinutes: 60,
    priority: 'medium',
  }
  subjectsText.value = ''
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

function fallbackDescription(type: StudyGoalType) {
  return type === 'growth' ? 'Long-term capability growth' : 'Personal learning direction'
}
</script>
