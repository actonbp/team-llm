import { createRouter, createWebHistory } from 'vue-router'

// Import views
import Home from '@/views/Home.vue'
import ParticipantJoin from '@/views/participant/Join.vue'
import ParticipantChat from '@/views/participant/Chat.vue'
import ResearcherDashboard from '@/views/researcher/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/join',
    name: 'participant-join',
    component: ParticipantJoin
  },
  {
    path: '/chat/:sessionId',
    name: 'participant-chat',
    component: ParticipantChat,
    props: true
  },
  {
    path: '/researcher',
    name: 'researcher-dashboard',
    component: ResearcherDashboard
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router