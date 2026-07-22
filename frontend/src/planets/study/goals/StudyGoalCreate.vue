<template>
  <section class="study-plan goal-create-flow" aria-labelledby="goal-create-title">
    <p class="eyebrow">Create Goal</p>
    <h2 id="goal-create-title">创建新的学习空间</h2>
    <p class="surface-copy">
      先选择目标类型，Universe OS 会为不同目标准备不同的 Knowledge 组织方式。
    </p>

    <div class="goal-wizard-steps" aria-label="Goal creation steps">
      <span :class="{ active: step === 1 }">1 目标类型</span>
      <span :class="{ active: step === 2 }">2 目标信息</span>
      <span :class="{ active: step === 3 }">3 Knowledge Space</span>
    </div>

    <section v-if="step === 1" class="home-section">
      <h3>你想推进哪一种目标？</h3>
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
      <div class="knowledge-actions">
        <button type="button" @click="step = 2">继续</button>
        <RouterLink class="secondary-action" to="/study/goals">返回 Goals</RouterLink>
      </div>
    </section>

    <form v-else-if="step === 2" class="study-form" @submit.prevent="step = 3">
      <label>
        目标名称
        <input v-model="form.goalName" required :placeholder="goalNamePlaceholder" />
      </label>
      <label v-if="form.goalType === 'exam'">
        考试名称
        <input v-model="form.examName" placeholder="MEM / PMP / 研究生考试" />
      </label>
      <label>
        截止时间
        <input v-model="form.deadline" type="date" />
      </label>
      <label>
        每日可用时间
        <input v-model.number="form.dailyAvailableMinutes" min="1" required type="number" />
      </label>
      <label>
        当前水平
        <input v-model="form.currentLevel" required placeholder="基础 / 入门 / 有项目经验" />
      </label>
      <label class="wide-field">
        {{ subjectLabel }}
        <input v-model="subjectsText" required :placeholder="subjectPlaceholder" />
      </label>
      <label class="wide-field">
        描述
        <textarea v-model="form.description" rows="3" :placeholder="descriptionPlaceholder" />
      </label>
      <div class="knowledge-actions">
        <button type="submit">继续配置 Knowledge Space</button>
        <button type="button" class="secondary-action" @click="step = 1">上一步</button>
      </div>
    </form>

    <section v-else class="home-section">
      <h3>{{ knowledgeTitle }}</h3>
      <p class="surface-copy">{{ knowledgeDescription }}</p>
      <div class="knowledge-mode-preview">
        <article v-for="item in knowledgePreviewItems" :key="item.title" class="knowledge-document">
          <span class="status-pill">{{ item.label }}</span>
          <h3>{{ item.title }}</h3>
          <p class="surface-copy">{{ item.description }}</p>
        </article>
      </div>
      <div class="knowledge-actions">
        <button type="button" :disabled="isSaving || !canCreate" @click="submitGoal">
          Create Goal
        </button>
        <button type="button" class="secondary-action" @click="step = 2">上一步</button>
        <span>{{ statusMessage }}</span>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createGoal, switchStudyGoal, type StudyGoalType } from '../../../services/api'

const router = useRouter()
const step = ref(1)
const isSaving = ref(false)
const statusMessage = ref('确认后会创建 Goal，并自动切换为 Current Goal。')
const subjectsText = ref('')
const form = ref({
  goalType: 'learning' as StudyGoalType,
  goalName: '',
  examName: '',
  deadline: '',
  description: '',
  currentLevel: '',
  dailyAvailableMinutes: 60,
  priority: 'medium',
})

const goalTypes: Array<{ value: StudyGoalType; label: string; description: string }> = [
  { value: 'exam', label: '考试目标', description: '科目隔离的考试 Knowledge Space' },
  { value: 'reading', label: '阅读目标', description: '像书架一样组织书和笔记' },
  { value: 'learning', label: '知识学习', description: '用知识卡片沉淀主题理解' },
  { value: 'growth', label: '成长目标', description: '长期能力建设和阶段记录' },
]

const subjects = computed(() =>
  subjectsText.value
    .split(',')
    .map((subject) => subject.trim())
    .filter(Boolean),
)
const canCreate = computed(
  () => Boolean(form.value.goalName.trim()) && Boolean(form.value.currentLevel.trim()) && subjects.value.length > 0,
)
const goalNamePlaceholder = computed(() => {
  const map: Record<StudyGoalType, string> = {
    exam: 'AI 方向研究生',
    reading: '阅读 CSAPP',
    learning: '学习 RAG 系统',
    growth: '成为 AI 工程师',
  }
  return map[form.value.goalType]
})
const subjectLabel = computed(() => {
  if (form.value.goalType === 'exam') {
    return '考试科目'
  }
  if (form.value.goalType === 'reading') {
    return '书籍 / 资料'
  }
  return '主题'
})
const subjectPlaceholder = computed(() => {
  if (form.value.goalType === 'exam') {
    return '数学, 英语, 408 数据结构'
  }
  if (form.value.goalType === 'reading') {
    return 'CSAPP, 阅读笔记, 操作系统'
  }
  return 'RAG, Embedding, Retrieval'
})
const descriptionPlaceholder = computed(() => {
  if (form.value.goalType === 'reading') {
    return '这本书希望解决什么问题？准备如何读完？'
  }
  if (form.value.goalType === 'exam') {
    return '考试方向、目标院校或证书要求。'
  }
  return '你希望通过这个目标形成什么能力？'
})
const knowledgeTitle = computed(() => {
  const map: Record<StudyGoalType, string> = {
    exam: '将创建隔离的考试知识库',
    reading: '将创建阅读书架',
    learning: '将创建知识卡片空间',
    growth: '将创建长期成长知识空间',
  }
  return map[form.value.goalType]
})
const knowledgeDescription = computed(() => {
  const map: Record<StudyGoalType, string> = {
    exam: '该目标下上传的资料会默认绑定当前考试目标，Tutor 检索时优先使用这个目标的资料。',
    reading: '阅读目标会以书架方式组织 PDF、笔记、摘录和标签。',
    learning: '知识学习目标会以卡片方式沉淀主题理解，并关联文档和 chunk。',
    growth: '成长目标会保留长期能力线索，后续可连接 Work Planet。',
  }
  return map[form.value.goalType]
})
const knowledgePreviewItems = computed(() => {
  if (form.value.goalType === 'exam') {
    return [
      { label: 'Subject', title: '科目分区', description: '不同考试科目默认隔离展示。' },
      { label: 'RAG', title: '目标内检索', description: '问答优先使用当前考试目标资料。' },
    ]
  }
  if (form.value.goalType === 'reading') {
    return [
      { label: 'Book', title: '书架', description: '每本书可以挂 PDF、笔记和标签。' },
      { label: 'Tags', title: '自定义标签', description: '支持章节、主题、状态和复习标签。' },
    ]
  }
  if (form.value.goalType === 'learning') {
    return [
      { label: 'Card', title: '知识卡片', description: '围绕概念、方法和问题沉淀理解。' },
      { label: 'Source', title: '来源关联', description: '卡片后续可关联文档和 chunk。' },
    ]
  }
  return [
    { label: 'Stage', title: '成长阶段', description: '记录长期能力建设的阶段线索。' },
    { label: 'Memory', title: '事实记忆', description: '只保存用户确认过的目标和偏好。' },
  ]
})

async function submitGoal() {
  if (!canCreate.value) {
    statusMessage.value = '请填写目标名称、当前水平和至少一个主题。'
    return
  }
  isSaving.value = true
  try {
    const goal = await createGoal({
      ...form.value,
      deadline: form.value.deadline || null,
      examName: form.value.goalType === 'exam' ? form.value.examName || form.value.goalName : null,
      subjects: subjects.value,
    })
    await switchStudyGoal(goal.id)
    statusMessage.value = 'Goal 已创建，正在进入 Study Workspace。'
    await router.push('/study')
  } finally {
    isSaving.value = false
  }
}
</script>
