import { createRouter, createWebHistory } from 'vue-router'
import AuctionsView from '@/views/AuctionsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'AuctionsView',
      component: AuctionsView,
    }
  ],
})

export default router
