<template>
  <section class="study-plan wordbook-space" aria-labelledby="wordbook-title">
    <div class="wordbook-heading">
      <div>
        <p class="eyebrow">Wordbook</p>
        <h2 id="wordbook-title">Your active word list</h2>
        <p class="wordbook-intro">Choose a language, narrow by a tag, then enrich any word with the phrases and sentences that make it stick.</p>
      </div>
      <label class="wordbook-scope">
        Goal scope
        <select v-model="goalFilter" @change="loadEntries">
          <option value="current">Current Goal</option>
          <option value="all">All Wordbook entries</option>
          <option value="independent">Independent Wordbook</option>
          <option v-for="goal in goals" :key="goal.id" :value="goal.id">{{ goal.goalName }}</option>
        </select>
      </label>
    </div>

    <div class="wordbook-language-rail" aria-label="Wordbook language">
      <span>Language</span>
      <button type="button" :class="{ selected: languageFilter === 'all' }" @click="selectLanguage('all')">All</button>
      <button v-for="language in languages" :key="language" type="button" :class="{ selected: languageFilter === language }" @click="selectLanguage(language)">
        {{ language }}
      </button>
    </div>

    <div class="wordbook-tag-rail" aria-label="Wordbook tags">
      <span>Tags</span>
      <button type="button" :class="{ selected: tagFilter === 'all' }" @click="selectTag('all')">All tags</button>
      <button v-for="tag in availableTags" :key="tag" type="button" :class="{ selected: tagFilter === tag }" @click="selectTag(tag)">
        {{ tag }}
      </button>
    </div>

    <div class="wordbook-list-heading">
      <div>
        <strong>{{ entries.length }} words</strong>
        <span>{{ selectedLanguageLabel }} · {{ selectedTagLabel }}</span>
      </div>
      <div class="wordbook-tools" aria-label="Wordbook tools">
        <button type="button" class="secondary-action" :class="{ selected: activeTool === 'add' }" @click="toggleTool('add')">Add word</button>
        <button type="button" class="secondary-action" :class="{ selected: activeTool === 'import' }" @click="toggleTool('import')">Import list</button>
      </div>
    </div>

    <form v-if="activeTool === 'add'" class="wordbook-quick-form" @submit.prevent="addWord">
      <label>Word<input v-model="newEntry.word" required placeholder="resilient" /></label>
      <label>Meaning<input v-model="newEntry.meaning" placeholder="able to recover quickly" /></label>
      <label>Language<select v-model="newEntry.language"><option v-for="language in languages" :key="language" :value="language">{{ language }}</option></select></label>
      <label>Tags<input v-model="newTags" placeholder="academic, systems" /></label>
      <button type="submit" :disabled="isSaving || !newEntry.word.trim()">Save word</button>
    </form>

    <form v-if="activeTool === 'import'" class="wordbook-import-bar" @submit.prevent="importFile">
      <p>TXT: <code>word[TAB]meaning</code> or <code>word | meaning</code>. CSV: <code>word,meaning,tags</code>.</p>
      <label>Language<select v-model="importLanguage"><option v-for="language in languages" :key="language" :value="language">{{ language }}</option></select></label>
      <input accept=".txt,.csv" required type="file" @change="selectImportFile" />
      <button type="submit" :disabled="isImporting || !importFileName">Import words</button>
      <small>{{ importStatus }}</small>
    </form>

    <p v-if="statusMessage" class="wordbook-status">{{ statusMessage }}</p>

    <div v-if="isLoading" class="knowledge-state">Refreshing your word list...</div>
    <div v-else-if="!entries.length" class="knowledge-state wordbook-empty">
      <strong>No words match this view yet.</strong>
      <span>Use Add word or Import list. Tags, phrases, example sentences and personal notes live in each word detail.</span>
    </div>
    <div v-else class="wordbook-layout">
      <div class="wordbook-list" aria-label="Wordbook entries">
        <button v-for="entry in entries" :key="entry.id" class="wordbook-entry" :class="{ selected: selectedEntry?.id === entry.id }" type="button" @click="selectEntry(entry)">
          <div class="wordbook-entry-head"><span class="wordbook-entry-word">{{ entry.word }}</span><small>{{ entry.language }}</small></div>
          <span>{{ entry.meaning || 'Add a meaning in detail' }}</span>
          <small>{{ entry.tags.length ? entry.tags.join(' · ') : entry.source === 'import' ? 'Imported' : 'Personal note' }}</small>
        </button>
      </div>

      <form v-if="selectedEntry" class="wordbook-detail" @submit.prevent="saveDetail">
        <div class="wordbook-detail-heading"><div><p class="eyebrow">Word detail</p><h3>{{ selectedEntry.word }}</h3></div><span class="status-pill">{{ selectedEntry.source === 'import' ? 'Imported' : 'Manual' }}</span></div>
        <div class="wordbook-detail-basics">
          <label>Word<input v-model="detailDraft.word" required /></label>
          <label>Language<select v-model="detailDraft.language"><option v-for="language in languages" :key="language" :value="language">{{ language }}</option></select></label>
        </div>
        <label>Meaning<textarea v-model="detailDraft.meaning" rows="2" placeholder="What does it mean in your own words?" /></label>
        <label>Pronunciation<input v-model="detailDraft.pronunciation" placeholder="/pronunciation/" /></label>
        <label>Tags<input v-model="detailDraft.tags" placeholder="academic, review, article" /></label>
        <label>Phrases<textarea v-model="detailDraft.phrases" rows="3" placeholder="One phrase per line&#10;a resilient system" /></label>
        <label>Example sentences<textarea v-model="detailDraft.examples" rows="4" placeholder="One sentence per line&#10;The system remained resilient under load." /></label>
        <label>Personal notes<textarea v-model="detailDraft.notes" rows="4" placeholder="Where you met it, contrast words, memory hooks..." /></label>
        <div class="wordbook-detail-actions"><button type="submit" :disabled="isSaving">Save detail</button><span>{{ selectedGoalLabel(selectedEntry.goalId) }}</span></div>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { createWordbookEntry, fetchStudyWorkspace, fetchWordbookEntries, importWordbookEntries, updateWordbookEntry, type StudyGoal, type WordEntry } from '../../../services/api'

const defaultLanguages = ['English', 'Chinese', 'Japanese', 'Korean', 'French', 'German', 'Spanish', 'Other']
const goals = ref<StudyGoal[]>([])
const entries = ref<WordEntry[]>([])
const scopeEntries = ref<WordEntry[]>([])
const selectedEntry = ref<WordEntry | null>(null)
const goalFilter = ref('current')
const currentGoalId = ref('')
const languageFilter = ref('English')
const tagFilter = ref('all')
const activeTool = ref<'add' | 'import' | null>(null)
const isLoading = ref(false)
const isSaving = ref(false)
const isImporting = ref(false)
const statusMessage = ref('')
const importStatus = ref('Choose a TXT or CSV list.')
const importFileName = ref('')
const importContent = ref('')
const importLanguage = ref('English')
const newTags = ref('')
const newEntry = ref({ word: '', meaning: '', language: 'English' })
const detailDraft = ref({ word: '', meaning: '', pronunciation: '', language: 'English', tags: '', phrases: '', examples: '', notes: '' })
const languages = computed(() => Array.from(new Set([...defaultLanguages, ...scopeEntries.value.map((entry) => entry.language)])).sort())
const availableTags = computed(() => Array.from(new Set(scopeEntries.value.flatMap((entry) => entry.tags))).sort())
const selectedLanguageLabel = computed(() => languageFilter.value === 'all' ? 'All languages' : languageFilter.value)
const selectedTagLabel = computed(() => tagFilter.value === 'all' ? 'All tags' : tagFilter.value)

onMounted(loadContext)

async function loadContext() {
  const workspace = await fetchStudyWorkspace()
  goals.value = workspace.goals
  currentGoalId.value = workspace.currentGoal?.id || ''
  if (!workspace.currentGoal) goalFilter.value = 'all'
  await loadEntries()
}

async function loadEntries() {
  isLoading.value = true
  try {
    const baseFilter = { ...scopeFilter(), ...(languageFilter.value === 'all' ? {} : { language: languageFilter.value }) }
    scopeEntries.value = await fetchWordbookEntries(baseFilter)
    if (tagFilter.value !== 'all' && !availableTags.value.includes(tagFilter.value)) tagFilter.value = 'all'
    entries.value = await fetchWordbookEntries({ ...baseFilter, ...(tagFilter.value === 'all' ? {} : { tag: tagFilter.value }) })
    if (!entries.value.some((entry) => entry.id === selectedEntry.value?.id)) selectEntry(entries.value[0] || null)
  } catch (error) {
    statusMessage.value = error instanceof Error ? error.message : 'Unable to load Wordbook.'
  } finally {
    isLoading.value = false
  }
}

function scopeFilter() {
  const goalId = goalFilter.value === 'current' ? currentGoalId.value : goalFilter.value
  return goalFilter.value === 'all' || goalFilter.value === 'independent' || !goalId ? {} : { goalId }
}

function selectLanguage(language: string) {
  languageFilter.value = language
  tagFilter.value = 'all'
  newEntry.value.language = language === 'all' ? 'English' : language
  importLanguage.value = newEntry.value.language
  loadEntries()
}

function selectTag(tag: string) {
  tagFilter.value = tag
  loadEntries()
}

function toggleTool(tool: 'add' | 'import') { activeTool.value = activeTool.value === tool ? null : tool }

async function addWord() {
  isSaving.value = true
  try {
    const entry = await createWordbookEntry({ ...newEntry.value, goalId: selectedGoalId(), tags: splitComma(newTags.value) })
    newEntry.value = { word: '', meaning: '', language: newEntry.value.language }
    newTags.value = ''
    activeTool.value = null
    statusMessage.value = `${entry.word} is now in your Wordbook.`
    await loadEntries()
    selectEntry(entry)
  } catch (error) { statusMessage.value = error instanceof Error ? error.message : 'Unable to add word.' } finally { isSaving.value = false }
}

async function selectImportFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!/\.(txt|csv)$/i.test(file.name)) { importStatus.value = 'Use a .txt or .csv file.'; input.value = ''; return }
  importFileName.value = file.name
  importContent.value = await file.text()
  importStatus.value = `${file.name} is ready to import.`
}

async function importFile() {
  if (!importFileName.value || !importContent.value) return
  isImporting.value = true
  try {
    const result = await importWordbookEntries({ fileName: importFileName.value, content: importContent.value, goalId: selectedGoalId(), language: importLanguage.value })
    importStatus.value = `${result.importedCount} added${result.skippedCount ? ` · ${result.skippedCount} already existed` : ''}.`
    activeTool.value = null
    statusMessage.value = result.importedCount ? 'Your imported words are ready for details.' : 'Every word in this file already exists here.'
    await loadEntries()
    if (result.imported[0]) selectEntry(result.imported[0])
  } catch (error) { importStatus.value = error instanceof Error ? error.message : 'Unable to import this list.' } finally { isImporting.value = false }
}

function selectEntry(entry: WordEntry | null) {
  selectedEntry.value = entry
  detailDraft.value = entry ? { word: entry.word, meaning: entry.meaning, pronunciation: entry.pronunciation, language: entry.language, tags: entry.tags.join(', '), phrases: entry.phrases.join('\n'), examples: entry.examples.join('\n'), notes: entry.notes } : { word: '', meaning: '', pronunciation: '', language: 'English', tags: '', phrases: '', examples: '', notes: '' }
}

async function saveDetail() {
  if (!selectedEntry.value) return
  isSaving.value = true
  try {
    const updated = await updateWordbookEntry(selectedEntry.value.id, { word: detailDraft.value.word, meaning: detailDraft.value.meaning, pronunciation: detailDraft.value.pronunciation, language: detailDraft.value.language, tags: splitComma(detailDraft.value.tags), phrases: splitLines(detailDraft.value.phrases), examples: splitLines(detailDraft.value.examples), notes: detailDraft.value.notes })
    statusMessage.value = `${updated.word} detail saved.`
    await loadEntries()
    selectEntry(updated)
  } catch (error) { statusMessage.value = error instanceof Error ? error.message : 'Unable to save this word.' } finally { isSaving.value = false }
}

function selectedGoalId() { const goalId = goalFilter.value === 'current' ? currentGoalId.value : goalFilter.value; return goalFilter.value === 'all' || goalFilter.value === 'independent' ? null : goalId || null }
function selectedGoalLabel(goalId?: string | null) { return goals.value.find((goal) => goal.id === goalId)?.goalName || 'Independent Wordbook' }
function splitComma(value: string) { return value.split(',').map((item) => item.trim()).filter(Boolean) }
function splitLines(value: string) { return value.split('\n').map((item) => item.trim()).filter(Boolean) }
</script>
