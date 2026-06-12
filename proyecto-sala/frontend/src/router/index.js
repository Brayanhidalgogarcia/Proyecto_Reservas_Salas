import { createRouter, createWebHistory } from 'vue-router'
import AltaUsuarioView from '@/views/AltaUsuarioView.vue'
import DisponibilidadView from '@/views/DisponibilidadView.vue'
import ApartarView from '../views/ApartarView.vue'
import ReportesView from '../views/ReportesView.vue'
import LoginView from '@/views/LoginView.vue'
import CatalogosView from '@/views/CatalogosView.vue'

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
    {
      path: '/admin/catalogos',
      name: 'catalogos',
      component: CatalogosView,
      meta: { title: 'Gestión de Catálogos', requiresAuth: true, requiresAdmin: true }
    },

  ]
})

// FUNCIÓN AUXILIAR: Verifica si el JWT ya caducó matemáticamente
function esTokenExpirado(token) {
  if (!token) return true;
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''));
    const payload = JSON.parse(jsonPayload);
    
    // Multiplicamos por 1000 porque JWT usa segundos y JS usa milisegundos
    return (payload.exp * 1000) < Date.now();
  } catch (e) {
    return true; // Si el token está corrupto o manipulado, lo damos por expirado
  }
}

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
  const isSuperUser = localStorage.getItem('is_superuser') === 'true'; 
  
  const tieneSesionActiva = token && !esTokenExpirado(token);

  // 1. REGLA DE LA PUERTA GIRATORIA: Evitar que usuarios logueados vean el login
  if (to.name === 'login' && tieneSesionActiva) {
    return next('/'); 
  }

  // 2. REGLA DEL FANTASMA: Proteger rutas privadas asegurando que el token esté VIVO
  if (to.meta.requiresAuth && !tieneSesionActiva) {
    // Limpieza preventiva: Si había basura o un token muerto, lo destruimos
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('is_superuser');
    localStorage.removeItem('user_id');
    
    return next('/login');
  }

  // 3. REGLA DEL ADMINISTRADOR: Proteger el acceso a reportes y catálogos
  if (to.meta.requiresAdmin && !isSuperUser) {
    return next('/'); 
  }
  
  // 4. ACTUALIZACIÓN DE TÍTULO DE PESTAÑA (Detalle UX Premium)
  if (to.meta.title) {
    document.title = `${to.meta.title} | Sistema de Reservas`;
  } else {
    document.title = 'Sistema de Reservas';
  }

  next();
});

export default router