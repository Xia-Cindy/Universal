<template>
  <main class="portal-shell">
    <section class="portal-hero" aria-labelledby="portal-title">
      <p class="eyebrow">Universe OS</p>
      <h1 id="portal-title">Enter your personal intelligent world</h1>
      <div class="planet-field">
        <article
          v-for="planet in planets"
          :key="planet.name"
          class="planet-object"
          :class="{ active: planet.enterable }"
        >
          <div class="planet-orbit" aria-hidden="true"></div>
          <h2>{{ planet.displayName }}</h2>
          <p>{{ planet.description }}</p>
          <button type="button" :disabled="!planet.enterable" @click="enterPlanet(planet)">
            {{ planet.primaryAction }}
          </button>
        </article>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import type { PlanetSummary } from '../../services/api'

const router = useRouter()
const planets = ref<PlanetSummary[]>([
  {
    name: 'study',
    displayName: 'Study Planet',
    status: 'active',
    description: 'A calm AI learning workspace focused on next action.',
    primaryAction: 'Enter Study Planet',
    enterable: true,
  },
  {
    name: 'work',
    displayName: 'Work Planet',
    status: 'coming_later',
    description: 'Future professional workspace placeholder.',
    primaryAction: 'Coming Later',
    enterable: false,
  },
  {
    name: 'novel',
    displayName: 'Novel Planet',
    status: 'coming_later',
    description: 'Future creative writing workspace placeholder.',
    primaryAction: 'Coming Later',
    enterable: false,
  },
  {
    name: 'life',
    displayName: 'Life Planet',
    status: 'coming_later',
    description: 'Future personal life rhythm workspace placeholder.',
    primaryAction: 'Coming Later',
    enterable: false,
  },
  {
    name: 'creator',
    displayName: 'Creator Planet',
    status: 'coming_later',
    description: 'Future creator workspace placeholder.',
    primaryAction: 'Coming Later',
    enterable: false,
  },
])

function enterPlanet(planet: PlanetSummary) {
  if (planet.name === 'study' && planet.enterable) {
    router.push('/study')
  }
}
</script>

