<template>
  <section class="study-home" aria-labelledby="placeholder-title">
    <p class="eyebrow">Placeholder</p>
    <h2 id="placeholder-title">{{ title }}</h2>
    <p>{{ message }}</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => `${String(route.params.section)} starts later`)
const message =
  'Milestone 2 stays inside the learning workflow. Knowledge, Tutor, Review, and Analytics remain placeholders.'
</script>
