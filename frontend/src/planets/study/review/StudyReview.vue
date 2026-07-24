<template>
  <section class="study-plan review-page" aria-labelledby="review-title">
    <p class="eyebrow">Review</p>
    <div class="review-heading">
      <div>
        <h2 id="review-title">Wrong Questions & Review</h2>
        <p>把一次错误变成四次可追踪的复习机会。</p>
      </div>
      <button type="button" class="secondary-action" @click="loadQueue">Refresh</button>
    </div>

    <form class="review-form" @submit.prevent="createQuestion">
      <label class="wide-field">
        Question
        <textarea v-model="form.question" required rows="3" placeholder="记录你这次没有答对的问题" />
      </label>
      <label>
        Subject
        <input v-model="form.subject" placeholder="例如：数据结构" />
      </label>
      <label>
        Topic
        <input v-model="form.topic" placeholder="例如：二叉树" />
      </label>
      <label class="wide-field">
        Correct answer / note
        <textarea v-model="form.correctAnswer" rows="3" placeholder="写下正确答案或复习提示" />
      </label>
      <div class="knowledge-actions">
        <button type="submit" :disabled="!form.question.trim()">Save Wrong Question</button>
        <span>{{ formStatus }}</span>
      </div>
    </form>

    <div v-if="isLoading" class="knowledge-state">Loading Review queue...</div>
    <div v-else-if="!queue.length" class="knowledge-state">
      <strong>No review items yet.</strong>
      <span>保存一道错题后，会自动建立 1 / 3 / 7 / 30 天复习节奏。</span>
    </div>
    <div v-else class="review-list">
      <article v-for="item in queue" :key="item.review.id" class="review-item">
        <div>
          <p class="eyebrow">{{ item.wrongQuestion.subject || 'Study' }} · {{ item.wrongQuestion.topic || 'Review' }}</p>
          <h3>{{ item.wrongQuestion.question }}</h3>
          <p v-if="item.wrongQuestion.correctAnswer">{{ item.wrongQuestion.correctAnswer }}</p>
          <small>第 {{ item.review.stage }} 次复习 · {{ item.review.intervalDays }} 天后 · {{ item.review.dueDate }}</small>
        </div>
        <button type="button" class="secondary-action" @click="complete(item.review.id)">Mark Reviewed</button>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { completeReviewItem, createWrongQuestion, fetchReviewQueue, type ReviewQueueItem } from '../../../services/api'

const queue = ref<ReviewQueueItem[]>([])
const isLoading = ref(false)
const formStatus = ref('')
const form = ref({ question: '', subject: '', topic: '', correctAnswer: '' })

onMounted(loadQueue)

async function loadQueue() {
  isLoading.value = true
  try {
    queue.value = await fetchReviewQueue(true)
  } catch (error) {
    formStatus.value = error instanceof Error ? error.message : 'Unable to load Review queue.'
  } finally {
    isLoading.value = false
  }
}

async function createQuestion() {
  try {
    await createWrongQuestion(form.value)
    form.value = { question: '', subject: '', topic: '', correctAnswer: '' }
    formStatus.value = 'Wrong Question saved with four review dates.'
    await loadQueue()
  } catch (error) {
    formStatus.value = error instanceof Error ? error.message : 'Unable to save Wrong Question.'
  }
}

async function complete(reviewId: string) {
  try {
    await completeReviewItem(reviewId)
    formStatus.value = 'Review completed.'
    await loadQueue()
  } catch (error) {
    formStatus.value = error instanceof Error ? error.message : 'Unable to complete Review.'
  }
}
</script>
