import { createRouter, createWebHistory } from 'vue-router'
import UniversePortal from '../universe/portal/UniversePortal.vue'
import StudyWorkspace from '../planets/study/layout/StudyWorkspace.vue'
import StudyHome from '../planets/study/home/StudyHome.vue'
import StudyPlan from '../planets/study/plan/StudyPlan.vue'
import StudyPlaceholder from '../planets/study/placeholder/StudyPlaceholder.vue'
import StudyTutor from '../planets/study/tutor/StudyTutor.vue'
import StudyKnowledge from '../planets/study/knowledge/StudyKnowledge.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'UniversePortal', component: UniversePortal },
    {
      path: '/study',
      component: StudyWorkspace,
      children: [
        { path: '', name: 'StudyHome', component: StudyHome },
        { path: 'plan', name: 'StudyPlan', component: StudyPlan },
        { path: 'knowledge', name: 'StudyKnowledge', component: StudyKnowledge },
        { path: 'tutor', name: 'StudyTutor', component: StudyTutor },
        {
          path: ':section(review|analytics)',
          name: 'StudyPlaceholder',
          component: StudyPlaceholder,
        },
      ],
    },
    { path: '/:futurePlanet(work|novel|life|creator)', redirect: '/' },
  ],
})
