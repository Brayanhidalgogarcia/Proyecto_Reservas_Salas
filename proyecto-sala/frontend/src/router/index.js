import { createRouter, createWebHistory } from 'vue-router'

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
      // AGREGAMOS 'requiresAdmin: true'
      meta: { title: 'Reportes', requiresAuth: true, requiresAdmin: true } 
    },
  ]
})

// --- EL PORTERO (GUARDIA DE NAVEGACIÓN MEJORADO) ---
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
  // Asumimos que guardaste esto en el Login. Si es 'true' o '1', es admin.
  const isSuperUser = localStorage.getItem('is_superuser') === 'true'; 

  // 1. Verificación de Autenticación (¿Estás logueado?)
  if (to.meta.requiresAuth && !token) {
    return next('/login');
  }

  // 2. Verificación de Permisos de Admin (¿Eres el jefe?)
  if (to.meta.requiresAdmin && !isSuperUser) {
    // Si intenta entrar a reportes pero no es admin, lo regresamos al inicio
    // para que no vea cosas que no debe.
    return next('/'); 
  }

  // 3. Pase adelante
  next();
});

export default router