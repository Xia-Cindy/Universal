<template>
  <main class="portal-shell universe-screen">
    <UniverseBackdrop tone="portal" />
    <section class="portal-hero" aria-labelledby="portal-title">
      <div class="portal-copy">
        <p class="portal-mark">UNIVERSE OS</p>
        <h1 id="portal-title">UNIVERSE</h1>
        <p class="portal-subtitle">YOUR PERSONAL AI OPERATING SYSTEM</p>
      </div>
      <div class="planet-field" aria-label="Universe planets">
        <component
          v-for="planet in planets"
          :key="planet.name"
          :is="planet.enterable ? 'button' : 'article'"
          :disabled="planet.enterable ? false : undefined"
          class="planet-object"
          :class="[planet.name, { active: planet.enterable }]"
          :aria-label="planet.primaryAction"
          :type="planet.enterable ? 'button' : undefined"
          @click="enterPlanet(planet)"
        >
          <div class="planet-orbit" aria-hidden="true"></div>
          <span class="planet-code">{{ planet.displayName.replace(' Planet', '') }}</span>
          <span class="planet-name">{{ planet.displayName }}</span>
          <span class="planet-description">{{ planet.description }}</span>
          <span class="planet-status">{{ planet.status === 'active' ? 'Enter workspace' : 'Coming later' }}</span>
        </component>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import type { PlanetSummary } from '../../services/api'
import UniverseBackdrop from '../../ui/UniverseBackdrop.vue'

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
    status: 'active',
    description: 'A professional capability workspace for tech stack, evidence, and dynamic resume.',
    primaryAction: 'Enter Work Planet',
    enterable: true,
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
  if (planet.name === 'work' && planet.enterable) {
    router.push('/work')
  }
}
</script>
