<template>
  <div class="universe-backdrop" :class="`universe-backdrop--${tone}`" aria-hidden="true">
    <i
      v-for="star in stars"
      :key="star.id"
      class="universe-star"
      :style="{
        '--star-left': `${star.left}%`,
        '--star-top': `${star.top}%`,
        '--star-delay': `${star.delay}s`,
        '--star-size': `${star.size}px`,
      }"
    />
    <i
      v-for="meteor in meteors"
      :key="meteor.id"
      class="universe-meteor"
      :style="{
        '--meteor-left': `${meteor.left}%`,
        '--meteor-top': `${meteor.top}%`,
        '--meteor-delay': `${meteor.delay}s`,
        '--meteor-duration': `${meteor.duration}s`,
      }"
    />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ tone?: 'portal' | 'study' | 'work' }>(), { tone: 'portal' })

function fraction(seed: number) {
  return Math.abs(Math.sin(seed * 12.9898) * 43758.5453) % 1
}

const stars = Array.from({ length: 92 }, (_, index) => ({
  id: index,
  left: Math.round(fraction(index + 1) * 1000) / 10,
  top: Math.round(fraction(index + 101) * 1000) / 10,
  delay: Math.round(fraction(index + 201) * 200) / 10,
  size: index % 11 === 0 ? 2 : 1,
}))

const meteors = [
  { id: 'north-east', left: 8, top: 18, delay: 1, duration: 16 },
  { id: 'center', left: 42, top: 6, delay: 7, duration: 18 },
  { id: 'south-west', left: 71, top: 60, delay: 11, duration: 15 },
  { id: 'quiet', left: 19, top: 78, delay: 16, duration: 20 },
]
</script>
