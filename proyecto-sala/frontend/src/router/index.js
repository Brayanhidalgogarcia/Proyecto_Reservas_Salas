import { createRouter, createWebHistory } from 'vue-router'

import DisponibilidadView from '@/views/DisponibilidadView.vue'
import ApartarView from '../views/ApartarView.vue'
import ReportesView from '../views/ReportesView.vue'
import LoginView from '@/views/LoginView.vue'



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  
  routes: [
     {
      path: '/',
      name: 'home',
      redirect: '/disponibilidad'
    },
    {
      
      path: '/disponibilidad',
      name: 'disponibilidad',
      component: DisponibilidadView
      
    },
    {
      path: '/reservar',
      name: 'reservar',
      component: ApartarView,
      meta: { title: 'Nueva Reserva' }

    },
    {
      path: '/reportes',
      name: 'reportes',
      component: ReportesView,
      meta: { title: 'Reportes' }
    },
  
    //{
      //path: '/admin/alta-usuario',
      //name: 'alta-usuario',
      //component: AltaUsuarioView, 
      //meta: { title: 'Alta de Usuarios' }
    //}
  
  ]
})

export default router
