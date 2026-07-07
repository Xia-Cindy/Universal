import { createRouter, createWebHistory } from 'vue-router'
import UniversePortal from '../universe/portal/UniversePortal.vue'
import StudyWorkspace from '../planets/study/layout/StudyWorkspace.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'UniversePortal', component: UniversePortal },
    { path: '/study', name: 'StudyWorkspace', component: StudyWorkspace },
    { path: '/:futurePlanet(work|novel|life|creator)', redirect: '/' },
  ],
})

