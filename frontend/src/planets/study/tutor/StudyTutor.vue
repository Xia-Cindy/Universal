<template>
  <section class="study-plan" aria-labelledby="tutor-title">
    <p class="eyebrow">Tutor</p>
    <h2 id="tutor-title">Study Tutor</h2>
    <p>
      Tutor uses your Goal, Plan, Daily Tasks, Study Sessions, and Learning Events.
      Knowledge sources and citations start in a later milestone.
    </p>

    <form class="tutor-form" @submit.prevent="askTutor">
      <label>
        Question
        <textarea v-model="question" rows="4" required />
      </label>
      <button type="submit">Ask Tutor</button>
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
      <h3>Related learning event</h3>
      <p>{{ response.relatedLearningEvent?.summary }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { askStudyTutor } from '../../../services/api'

const question = ref('What should I study next?')
const response = ref<any>(null)

async function askTutor() {
  response.value = await askStudyTutor(question.value)
}
</script>
