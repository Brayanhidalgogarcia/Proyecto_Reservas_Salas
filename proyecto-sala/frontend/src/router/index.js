import { createRouter, createWebHistory } from 'vue-router'
import AltaUsuarioView from '@/views/AltaUsuarioView.vue'
import DisponibilidadView from '@/views/DisponibilidadView.vue'
import ApartarView from '../views/ApartarView.vue'
import ReportesView from '../views/ReportesView.vue'
import LoginView from '@/views/LoginView.vue'



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      name: 'home',
      redirect: '/disponibilidad'
    },
    {
      path: '/disponibilidad',
      name: 'disponibilidad',
      component: DisponibilidadView,
      meta: { requiresAuth: true }
    },
    {
      path: '/reservar',
      name: 'reservar',
      component: ApartarView,
      meta: { title: 'Nueva Reserva', requiresAuth: true }
    },
    {
      path: '/reportes',
      name: 'reportes',
      component: ReportesView,
      meta: { title: 'Reportes', requiresAuth: true, requiresAdmin: true } 
    },
   
    {
      path: '/admin/alta-usuario',
      name: 'alta-usuario',
      component: AltaUsuarioView,
      
      meta: { title: 'Alta de Usuarios', requiresAuth: true, requiresAdmin: true }
    },
  ]
})


router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
 
  const isSuperUser = localStorage.getItem('is_superuser') === 'true'; 

  
  if (to.meta.requiresAuth && !token) {
    return next('/login');
  }


  if (to.meta.requiresAdmin && !isSuperUser) {
   
    return next('/'); 
  }

  
  next();
});

export default router