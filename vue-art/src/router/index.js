import { createRouter, createWebHistory } from 'vue-router'
import AuctionsView from '@/views/AuctionsView.vue'
import LoginView from '@/views/LoginView.vue'
import ProfileView from '@/views/ProfileView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  linkActiveClass: 'active',
  routes: [
    {
      path: '/auctions',
      name: 'AuctionsView',
      component: AuctionsView,
    },
    {
      path: '/login',
      name: 'LoginView',
      component: LoginView,
    },
    {
      path: '/',
      name: 'ProfileView',
      component: ProfileView,
    }
  ],
})

export default router
