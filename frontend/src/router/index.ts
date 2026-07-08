import { createRouter, createWebHistory } from 'vue-router'
import UniversePortal from '../universe/portal/UniversePortal.vue'
import StudyWorkspace from '../planets/study/layout/StudyWorkspace.vue'
import StudyHome from '../planets/study/home/StudyHome.vue'
import StudyOnboarding from '../planets/study/onboarding/StudyOnboarding.vue'
import StudyPlan from '../planets/study/plan/StudyPlan.vue'
import StudySession from '../planets/study/session/StudySession.vue'
import StudyPlaceholder from '../planets/study/placeholder/StudyPlaceholder.vue'
import StudyTutor from '../planets/study/tutor/StudyTutor.vue'
import StudyKnowledge from '../planets/study/knowledge/StudyKnowledge.vue'
import StudyAnalytics from '../planets/study/analytics/StudyAnalytics.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'UniversePortal', component: UniversePortal },
    {
      path: '/study',
      component: StudyWorkspace,
      children: [
        { path: '', name: 'StudyHome', component: StudyHome },
        { path: 'onboarding', name: 'StudyOnboarding', component: StudyOnboarding },
        { path: 'plan', name: 'StudyPlan', component: StudyPlan },
        { path: 'session/:sessionId', name: 'StudySession', component: StudySession },
        { path: 'knowledge', name: 'StudyKnowledge', component: StudyKnowledge },
        { path: 'tutor', name: 'StudyTutor', component: StudyTutor },
        { path: 'analytics', name: 'StudyAnalytics', component: StudyAnalytics },
        {
          path: ':section(review)',
          name: 'StudyPlaceholder',
          component: StudyPlaceholder,
        },
      ],
    },
    { path: '/:futurePlanet(work|novel|life|creator)', redirect: '/' },
  ],
})
