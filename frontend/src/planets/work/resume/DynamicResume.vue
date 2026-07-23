<template>
  <section class="study-plan" aria-labelledby="dynamic-resume-title">
    <p class="eyebrow">Dynamic Resume</p>
    <h2 id="dynamic-resume-title">动态简历</h2>
    <p class="surface-copy">
      选择岗位方向，系统会基于 Work Planet 内已确认的技术栈和项目证据生成草稿。
    </p>

    <form class="study-form" @submit.prevent="createDraft">
      <label>
        岗位方向
        <select v-model="roleTarget">
          <option>AI Engineer</option>
          <option>Data Analyst</option>
          <option>Backend Engineer</option>
          <option>Digital Transformation Consultant</option>
          <option>AI Product Manager</option>
        </select>
      </label>
      <div class="knowledge-actions">
        <button type="submit">Create Resume Draft</button>
        <span>{{ status }}</span>
      </div>
    </form>

    <div v-if="resumes.length" class="goal-list">
      <article v-for="resume in resumes" :key="resume.id" class="knowledge-document resume-card">
        <span class="status-pill">{{ resume.status }}</span>
        <h3>{{ resume.title }}</h3>
        <p class="surface-copy whitespace">{{ resume.content }}</p>
        <small>{{ resume.evidenceRefs.length }} evidence refs · {{ resume.roleTarget }}</small>
      </article>
    </div>
    <div v-else class="knowledge-state">
      <strong>No resume draft yet.</strong>
      <span>Add Tech Stack and project evidence first for stronger drafts.</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { createResumeDraft, fetchResumeVersions, type ResumeVersion } from '../../../services/api'

const resumes = ref<ResumeVersion[]>([])
const roleTarget = ref('AI Engineer')
const status = ref('AI will not invent experience; draft uses confirmed evidence only.')

onMounted(loadResumes)

async function loadResumes() {
  resumes.value = await fetchResumeVersions()
}

async function createDraft() {
  await createResumeDraft({ roleTarget: roleTarget.value })
  status.value = 'Resume draft created from current evidence.'
  await loadResumes()
}
</script>
