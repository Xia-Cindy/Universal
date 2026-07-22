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
      <div v-if="response.groundingChunks?.length" class="grounding-list">
        <article v-for="chunk in response.groundingChunks" :key="chunk.chunkId" class="chunk-item">
          <strong>{{ chunk.metadata?.subject }} / {{ chunk.metadata?.topic }}</strong>
          <p>{{ chunk.content }}</p>
          <small>Score {{ chunk.score }}</small>
        </article>
      </div>
      <h3>Related learning event</h3>
      <p>{{ response.relatedLearningEvent?.summary }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { askStudyTutor } from '../../../services/api'

const question = ref('')
const response = ref<any>(null)
const canAsk = computed(() => question.value.trim().length > 0)

async function askTutor() {
  if (!canAsk.value) {
    return
  }
  response.value = await askStudyTutor(question.value.trim())
}
</script>
