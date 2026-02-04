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
    // --- NUEVA RUTA: ALTA DE USUARIOS ---
    {
      path: '/admin/alta-usuario',
      name: 'alta-usuario',
      component: AltaUsuarioView,
      // Aplicamos el candado doble: Login + Admin
      meta: { title: 'Alta de Usuarios', requiresAuth: true, requiresAdmin: true }
    },
  ]
})

// --- EL PORTERO (GUARDIA DE NAVEGACIÓN) ---
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
  // Obtenemos si es superusuario (guardado como string 'true' o 'false')
  const isSuperUser = localStorage.getItem('is_superuser') === 'true'; 

  // 1. Verificación de Autenticación
  if (to.meta.requiresAuth && !token) {
    return next('/login');
  }

  // 2. Verificación de Permisos de Admin
  if (to.meta.requiresAdmin && !isSuperUser) {
    // Si intenta entrar a zona protegida sin ser admin, lo mandamos al inicio
    return next('/'); 
  }

  // 3. Pase adelante
  next();
});

export default router