<template>
  <section class="study-plan" aria-labelledby="goals-title">
    <p class="eyebrow">Goals</p>
    <h2 id="goals-title">Study Goals</h2>

    <div v-if="loadState === 'loading'" class="knowledge-state">Loading Goals...</div>

    <template v-else>
      <section class="home-section">
        <div class="section-heading">
          <h3>Current Goal</h3>
          <RouterLink class="secondary-action" to="/study/plan">Open Plan</RouterLink>
        </div>
        <p class="surface-copy">
          The current Goal is the context for Home, Plan, Knowledge, Tutor, and Analytics.
        </p>
        <article v-if="activeGoal" class="knowledge-document selected">
          <div>
            <span class="status-pill">{{ goalTypeLabel(activeGoal.goalType) }}</span>
            <h3>{{ activeGoal.goalName }}</h3>
            <p class="surface-copy">{{ activeGoal.description || fallbackDescription(activeGoal.goalType) }}</p>
            <small>{{ activeGoal.deadline || 'No deadline' }} · {{ activeGoal.status }}</small>
          </div>
          <div class="task-actions">
            <button type="button" class="secondary-action" @click="startEdit(activeGoal)">Edit Goal</button>
            <RouterLink class="secondary-action" to="/study/plan">View Plan</RouterLink>
          </div>
        </article>
        <form
          v-if="editingGoalId === activeGoal?.id"
          class="study-form edit-surface"
          @submit.prevent="submitGoalEdit"
        >
          <div class="goal-type-picker wide-field" aria-label="Edit goal type">
            <button
              v-for="option in goalTypes"
              :key="option.value"
              type="button"
              :class="{ selected: editForm.goalType === option.value }"
              @click="editForm.goalType = option.value"
            >
              <strong>{{ option.label }}</strong>
              <span>{{ option.description }}</span>
            </button>
          </div>
          <label>
            Goal title
            <input v-model="editForm.goalName" required />
          </label>
          <label>
            Deadline
            <input v-model="editForm.deadline" type="date" />
          </label>
          <label>
            Daily minutes
            <input v-model.number="editForm.dailyAvailableMinutes" min="1" required type="number" />
          </label>
          <label>
            Current level
            <input v-model="editForm.currentLevel" required />
          </label>
          <label class="wide-field">
            Subjects
            <input v-model="editSubjectsText" required placeholder="systems, algorithms, English" />
          </label>
          <label class="wide-field">
            Description
            <textarea v-model="editForm.description" rows="3" />
          </label>
          <div class="knowledge-actions">
            <button type="submit" :disabled="isSavingEdit">Save Goal</button>
            <button type="button" class="secondary-action" @click="cancelEdit">Cancel</button>
          </div>
        </form>
        <div v-else class="knowledge-state">
          <strong>No current Goal yet.</strong>
          <span>Create one Goal to start connecting plans, tasks, and Knowledge.</span>
        </div>
      </section>

      <section class="home-section">
        <h3>Other Goals</h3>
        <div v-if="otherGoals.length" class="goal-list">
          <article
            v-for="goal in otherGoals"
            :key="goal.id"
            class="knowledge-document"
          >
            <div>
              <span class="status-pill">{{ goalTypeLabel(goal.goalType) }}</span>
              <h3>{{ goal.goalName }}</h3>
              <p class="surface-copy">{{ goal.description || fallbackDescription(goal.goalType) }}</p>
              <small>{{ goal.deadline || 'No deadline' }} · {{ goal.status }}</small>
            </div>
            <div class="task-actions">
              <button type="button" class="secondary-action" @click="startEdit(goal)">Edit</button>
              <button type="button" @click="switchGoal(goal.id)">Switch</button>
            </div>
            <form
              v-if="editingGoalId === goal.id"
              class="study-form edit-surface"
              @submit.prevent="submitGoalEdit"
            >
              <label>
                Goal title
                <input v-model="editForm.goalName" required />
              </label>
              <label>
                Deadline
                <input v-model="editForm.deadline" type="date" />
              </label>
              <label>
                Daily minutes
                <input v-model.number="editForm.dailyAvailableMinutes" min="1" required type="number" />
              </label>
              <label>
                Current level
                <input v-model="editForm.currentLevel" required />
              </label>
              <label class="wide-field">
                Subjects
                <input v-model="editSubjectsText" required />
              </label>
              <label class="wide-field">
                Description
                <textarea v-model="editForm.description" rows="3" />
              </label>
              <div class="knowledge-actions">
                <button type="submit" :disabled="isSavingEdit">Save Goal</button>
                <button type="button" class="secondary-action" @click="cancelEdit">Cancel</button>
              </div>
            </form>
          </article>
        </div>
        <div v-else class="knowledge-state">
          <span>No other Goals yet.</span>
        </div>
      </section>

      <section class="home-section">
        <h3>Create Goal</h3>
        <p class="surface-copy">
          A Goal can be exam preparation, reading, general learning, or long-term growth.
        </p>
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
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  createGoal,
  fetchStudyWorkspace,
  switchStudyGoal,
  updateGoal,
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
const editingGoalId = ref('')
const isSavingEdit = ref(false)
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
const editForm = ref({
  goalType: 'learning' as StudyGoalType,
  goalName: '',
  deadline: '',
  description: '',
  currentLevel: '',
  dailyAvailableMinutes: 60,
  priority: 'medium',
})
const editSubjectsText = ref('')

const subjects = computed(() =>
  subjectsText.value
    .split(',')
    .map((subject) => subject.trim())
    .filter(Boolean),
)
const editSubjects = computed(() =>
  editSubjectsText.value
    .split(',')
    .map((subject) => subject.trim())
    .filter(Boolean),
)
const activeGoal = computed(() => goals.value.find((goal) => goal.id === activeGoalId.value) || null)
const otherGoals = computed(() => goals.value.filter((goal) => goal.id !== activeGoalId.value))

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

function startEdit(goal: StudyGoal) {
  editingGoalId.value = goal.id
  editForm.value = {
    goalType: goal.goalType,
    goalName: goal.goalName,
    deadline: goal.deadline || '',
    description: goal.description || '',
    currentLevel: goal.currentLevel,
    dailyAvailableMinutes: goal.dailyAvailableMinutes,
    priority: goal.priority,
  }
  editSubjectsText.value = goal.subjects.join(', ')
  statusMessage.value = `Editing ${goal.goalName}.`
}

function cancelEdit() {
  editingGoalId.value = ''
  statusMessage.value = 'Goal editing cancelled.'
}

async function submitGoalEdit() {
  if (!editingGoalId.value) {
    return
  }
  isSavingEdit.value = true
  try {
    await updateGoal(editingGoalId.value, {
      ...editForm.value,
      deadline: editForm.value.deadline || null,
      examName: editForm.value.goalType === 'exam' ? editForm.value.goalName : null,
      subjects: editSubjects.value,
    })
    statusMessage.value = 'Goal updated.'
    editingGoalId.value = ''
    await loadGoals()
  } finally {
    isSavingEdit.value = false
  }
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
