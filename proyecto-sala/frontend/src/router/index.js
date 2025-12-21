import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import ApartarView from '../views/ApartarView.vue'
import ReportesView from '../views/ReportesView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  
  routes: [
    {
      path: '/',
      name: 'disponibilidad',
      component: HomeView
    },
    {
      path: '/apartar',
      name: 'apartar',
      component: ApartarView
    },
    {
      path: '/reportes',
      name: 'reportes',
      component: ReportesView
    }
    
  ]
})

export default router
