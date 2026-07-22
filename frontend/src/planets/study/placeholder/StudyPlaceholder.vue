<template>
  <section class="study-home" aria-labelledby="placeholder-title">
    <p class="eyebrow">Coming Later</p>
    <h2 id="placeholder-title">{{ title }}</h2>
    <p>{{ message }}</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => `${String(route.params.section)} is not ready yet`)
const message =
  'Wrong Questions and Review are part of the Study Planet MVP direction, but this workspace does not have the review loop implemented yet.'
</script>
