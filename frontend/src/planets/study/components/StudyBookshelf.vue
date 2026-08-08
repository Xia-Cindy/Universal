<template>
  <section class="study-bookshelf" :aria-label="label">
    <div class="study-bookshelf-ledge" aria-hidden="true"></div>
    <div class="study-bookshelf-books">
      <button
        v-for="book in books"
        :key="book.id"
        class="study-shelf-book"
        :class="{ selected: book.id === selectedId }"
        :style="{ '--book-accent': book.color || '#4da9c8' }"
        type="button"
        :aria-pressed="book.id === selectedId"
        @click="$emit('select', book.id)"
      >
        <span class="study-shelf-book-shine" aria-hidden="true"></span>
        <span class="study-shelf-book-spine">{{ book.spine || 'BOOK' }}</span>
        <span class="study-shelf-book-title">{{ book.title }}</span>
        <span class="study-shelf-book-meta">{{ book.meta }}</span>
        <span class="study-shelf-book-status">{{ book.status }}</span>
      </button>
    </div>
    <div class="study-bookshelf-plinth" aria-hidden="true"></div>
  </section>
</template>

<script setup lang="ts">
export interface StudyShelfBook {
  id: string
  title: string
  spine?: string
  meta: string
  status: string
  color?: string
}

defineProps<{
  books: StudyShelfBook[]
  selectedId?: string | null
  label: string
}>()

defineEmits<{
  select: [id: string]
}>()
</script>
