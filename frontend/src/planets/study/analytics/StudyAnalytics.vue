<template>
  <section class="study-plan analytics-space" aria-labelledby="analytics-title">
    <p class="eyebrow">Analytics</p>
    <h2 id="analytics-title">Study Intelligence</h2>

    <div v-if="isLoading" class="knowledge-state">Reading your Study signals...</div>

    <template v-else-if="analytics">
      <div v-if="analytics.dataQuality.state === 'insufficient'" class="knowledge-state">
        <strong>Not enough signal yet.</strong>
        <span>{{ analytics.dataQuality.limitations?.[0] }}</span>
      </div>

      <div class="analytics-summary">
        <span>
          <strong>{{ analytics.progressSummary.completedTasks || 0 }}</strong>
          tasks completed
        </span>
        <span>
          <strong>{{ analytics.progressSummary.totalStudyMinutes || 0 }}</strong>
          minutes studied
        </span>
        <span>
          <strong>{{ completionRateLabel }}</strong>
          completion rate
        </span>
      </div>

      <section class="analytics-section">
        <h3>Insights</h3>
        <ul>
          <li v-for="insight in analytics.learningInsights" :key="insight">{{ insight }}</li>
        </ul>
      </section>

      <section class="analytics-section">
        <h3>Next actions</h3>
        <ul>
          <li v-for="action in analytics.recommendedActions" :key="action">{{ action }}</li>
        </ul>
      </section>

      <section v-if="analytics.weakAreas.length" class="analytics-section">
        <h3>Weak areas</h3>
        <article v-for="area in analytics.weakAreas" :key="area.subject" class="chunk-item">
          <strong>{{ area.subject }}</strong>
          <p>{{ weakAreaReason(area.reason) }} · {{ Math.round((area.completionRate || 0) * 100) }}% completion</p>
        </article>
      </section>

      <section class="analytics-section">
        <h3>Report</h3>
        <p>{{ analytics.report.summary }}</p>
        <div v-if="analytics.report.groundingChunks?.length" class="grounding-list">
          <article
            v-for="chunk in analytics.report.groundingChunks"
            :key="chunk.chunkId"
            class="chunk-item"
          >
            <strong>{{ chunk.metadata?.subject }} / {{ chunk.metadata?.topic }}</strong>
            <p>{{ chunk.content }}</p>
          </article>
        </div>
      </section>

      <div class="plan-actions">
        <button type="button" @click="refreshReport">Refresh Report</button>
        <span>{{ status }}</span>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  createStudyAnalyticsReport,
  fetchStudyAnalytics,
  type StudyAnalyticsPayload,
} from '../../../services/api'

const analytics = ref<StudyAnalyticsPayload | null>(null)
const isLoading = ref(false)
const status = ref('Analyst reads current Study signals.')
const completionRateLabel = computed(() =>
  `${Math.round(((analytics.value?.progressSummary.taskCompletionRate as number) || 0) * 100)}%`,
)

onMounted(loadAnalytics)

async function loadAnalytics() {
  isLoading.value = true
  try {
    analytics.value = await fetchStudyAnalytics()
  } finally {
    isLoading.value = false
  }
}

async function refreshReport() {
  isLoading.value = true
  try {
    analytics.value = await createStudyAnalyticsReport()
    status.value = 'Report refreshed.'
  } finally {
    isLoading.value = false
  }
}

function weakAreaReason(reason: string) {
  const labels: Record<string, string> = {
    low_task_completion: '任务推进偏慢',
  }
  return labels[reason] || reason
}
</script>
