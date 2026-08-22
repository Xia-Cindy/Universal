import { createRouter, createWebHistory } from 'vue-router'
import UniversePortal from '../universe/portal/UniversePortal.vue'
import StudyWorkspace from '../planets/study/layout/StudyWorkspace.vue'
import StudyHome from '../planets/study/home/StudyHome.vue'
import StudyOnboarding from '../planets/study/onboarding/StudyOnboarding.vue'
import StudyGoals from '../planets/study/goals/StudyGoals.vue'
import StudyGoalCreate from '../planets/study/goals/StudyGoalCreate.vue'
import StudyPlan from '../planets/study/plan/StudyPlan.vue'
import StudySession from '../planets/study/session/StudySession.vue'
import StudyPlaceholder from '../planets/study/placeholder/StudyPlaceholder.vue'
import StudyReview from '../planets/study/review/StudyReview.vue'
import StudyTutor from '../planets/study/tutor/StudyTutor.vue'
import StudyKnowledge from '../planets/study/knowledge/StudyKnowledge.vue'
import StudyWordbook from '../planets/study/wordbook/StudyWordbook.vue'
import StudyAnalytics from '../planets/study/analytics/StudyAnalytics.vue'
import WorkWorkspace from '../planets/work/layout/WorkWorkspace.vue'
import WorkHome from '../planets/work/home/WorkHome.vue'
import TechStackDirectory from '../planets/work/tech-stack/TechStackDirectory.vue'
import TechStackDetail from '../planets/work/tech-stack/TechStackDetail.vue'
import WorkProjects from '../planets/work/projects/WorkProjects.vue'
import DynamicResume from '../planets/work/resume/DynamicResume.vue'
import Register from '../pages/Register.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'UniversePortal', component: UniversePortal },
    { path: '/register', name: 'Register', component: Register },
    {
      path: '/study',
      component: StudyWorkspace,
      children: [
        { path: '', name: 'StudyHome', component: StudyHome },
        { path: 'onboarding', name: 'StudyOnboarding', component: StudyOnboarding },
        { path: 'goals', name: 'StudyGoals', component: StudyGoals },
        { path: 'goals/new', name: 'StudyGoalCreate', component: StudyGoalCreate },
        { path: 'plan', name: 'StudyPlan', component: StudyPlan },
        { path: 'session/:sessionId', name: 'StudySession', component: StudySession },
        { path: 'knowledge', name: 'StudyKnowledge', component: StudyKnowledge },
        { path: 'wordbook', name: 'StudyWordbook', component: StudyWordbook },
        { path: 'tutor', name: 'StudyTutor', component: StudyTutor },
        { path: 'analytics', name: 'StudyAnalytics', component: StudyAnalytics },
        { path: 'review', name: 'StudyReview', component: StudyReview },
        { path: ':section', name: 'StudyPlaceholder', component: StudyPlaceholder },
      ],
    },
    {
      path: '/work',
      component: WorkWorkspace,
      children: [
        { path: '', name: 'WorkHome', component: WorkHome },
        { path: 'tech-stack', name: 'TechStackDirectory', component: TechStackDirectory },
        { path: 'tech-stack/:techStackId', name: 'TechStackDetail', component: TechStackDetail },
        { path: 'projects', name: 'WorkProjects', component: WorkProjects },
        { path: 'resume', name: 'DynamicResume', component: DynamicResume },
      ],
    },
    { path: '/:futurePlanet(novel|life|creator)', redirect: '/' },
  ],
})
