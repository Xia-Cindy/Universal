<template>
  <section class="study-plan" aria-labelledby="tutor-title">
    <p class="eyebrow">Tutor</p>
    <h2 id="tutor-title">Study Tutor</h2>
    <p>
      Tutor uses your Goal, Plan, Daily Tasks, Study Sessions, Learning Events, and prepared
      Knowledge chunks when available.
    </p>

    <form class="tutor-form" @submit.prevent="askTutor">
      <label>
        Knowledge scope
        <select v-model="scope">
          <option value="current_goal">Current Goal Knowledge</option>
          <option value="all_study">All Study Knowledge</option>
        </select>
      </label>
      <label>
        Question
        <textarea
          v-model="question"
          placeholder="Ask about your current Goal, Plan, task, or uploaded Knowledge."
          rows="4"
          required
        />
      </label>
      <div class="knowledge-actions">
        <button type="submit" :disabled="!canAsk">Ask Tutor</button>
        <span v-if="!canAsk">Enter a question to ask Tutor.</span>
      </div>
    </form>

    <article v-if="response" class="tutor-response">
      <h3>Answer</h3>
      <p>{{ response.answer }}</p>
      <h3>Reasoning</h3>
      <p>{{ response.reasoning }}</p>
      <h3>Suggested next action</h3>
      <p>{{ response.suggestedNextAction }}</p>
      <h3>Knowledge sources</h3>
      <p>{{ response.sourceNotice }}</p>
      <div v-if="response.sources?.length" class="grounding-list">
        <article v-for="source in response.sources" :key="source.sourceId" class="chunk-item">
          <strong>{{ source.title }}</strong>
          <p>{{ source.quote }}</p>
          <small>Score {{ source.score }}</small>
          <a v-if="source.sourceUrl" :href="source.sourceUrl">Open source</a>
        </article>
      </div>
      <p v-else class="knowledge-state">No prepared Knowledge source matched this question.</p>
      <div class="knowledge-actions">
        <button type="button" :disabled="isSaving" @click="saveAnswer">Save as Learning Event</button>
        <span>{{ saveStatus }}</span>
      </div>
      <h3>Related learning event</h3>
      <p>{{ response.relatedLearningEvent?.summary }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { askStudyTutor, saveTutorAnswerEvent, type EvidenceSource } from '../../../services/api'

const question = ref('')
const response = ref<any>(null)
const scope = ref('current_goal')
const isSaving = ref(false)
const saveStatus = ref('')
const canAsk = computed(() => question.value.trim().length > 0)

async function askTutor() {
  if (!canAsk.value) {
    return
  }
  saveStatus.value = ''
  response.value = await askStudyTutor(question.value.trim(), scope.value)
}

async function saveAnswer() {
  if (!response.value || isSaving.value) {
    return
  }
  isSaving.value = true
  try {
    await saveTutorAnswerEvent({
      question: question.value.trim(),
      answer: response.value.answer,
      sources: (response.value.sources || []) as EvidenceSource[],
    })
    saveStatus.value = 'Saved to Learning Events.'
  } catch (error) {
    saveStatus.value = error instanceof Error ? error.message : 'Unable to save Learning Event.'
  } finally {
    isSaving.value = false
  }
}
</script>
