import { createRouter, createWebHistory } from 'vue-router'
import AuctionsView from '@/views/AuctionsView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  linkActiveClass: 'active',
  routes: [
    {
      path: '/',
      name: 'AuctionsView',
      component: AuctionsView,
    },
    {
      path: '/login',
      name: 'LoginView',
      component: LoginView,
    }
  ],
})

export default router
