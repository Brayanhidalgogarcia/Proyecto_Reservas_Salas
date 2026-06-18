/**
 * @file index.js (Vue Router)
 * @description Configuración central del enrutador de la aplicación.
 * Define el mapa de navegación, implementa 'Lazy Loading' para optimización de rendimiento
 * y gestiona los 'Navigation Guards' para proteger rutas mediante tokens JWT y roles.
 */

// ==========================================
// 1. IMPORTS PRINCIPALES
// ==========================================
import { createRouter, createWebHistory } from 'vue-router'

// ==========================================
// 2. MAPA DE RUTAS (CON LAZY LOADING)
// ==========================================
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      // Carga perezosa: Solo descarga esta vista si el usuario entra a /login
      component: () => import('@/views/LoginView.vue'),
      meta: { title: 'Iniciar Sesión' }
    },
    {
      path: '/',
      alias: '/home',
      name: 'home',
      component: () => import('@/views/InicioView.vue'),
      meta: { title: 'Inicio', requiresAuth: true },
    },
    {
      path: '/disponibilidad',
      name: 'disponibilidad',
      component: () => import('@/views/DisponibilidadView.vue'),
      meta: { title: 'Disponibilidad', requiresAuth: true }
    },
    {
      path: '/reservar',
      name: 'reservar',
      component: () => import('@/views/ApartarView.vue'),
      meta: { title: 'Nueva Reserva', requiresAuth: true }
    },
    {
      path: '/reportes',
      name: 'reportes',
      component: () => import('@/views/ReportesView.vue'),
      meta: { title: 'Reportes BI', requiresAuth: true, requiresAdmin: true } 
    },
    {
      path: '/admin/alta-usuario',
      name: 'alta-usuario',
      component: () => import('@/views/AltaUsuarioView.vue'),
      meta: { title: 'Alta de Usuarios', requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/catalogos',
      name: 'catalogos',
      component: () => import('@/views/CatalogosView.vue'),
      meta: { title: 'Gestión de Catálogos', requiresAuth: true, requiresAdmin: true }
    }
  ]
})

// ==========================================
// 3. FUNCIONES AUXILIARES (SEGURIDAD)
// ==========================================

/**
 * Función criptográfica experta: Verifica si un JSON Web Token (JWT) ha expirado
 * desencriptando el payload en Base64 y comparando el timestamp ('exp') con el reloj local.
 * @param {string} token - El JWT de acceso.
 * @returns {boolean} Retorna true si expiró, si es nulo o si está corrupto.
 */
function esTokenExpirado(token) {
  if (!token) return true;
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''));
    const payload = JSON.parse(jsonPayload);
    
    // Multiplicamos por 1000 porque el JWT usa segundos y JavaScript usa milisegundos
    return (payload.exp * 1000) < Date.now();
  } catch (e) {
    // Si el token está corrupto o manipulado, lo damos por expirado por seguridad
    return true; 
  }
}

// ==========================================
// 4. MIDDLEWARE (NAVIGATION GUARDS)
// ==========================================

/**
 * Guardia de navegación global. Intercepta TODAS las transiciones de ruta para
 * validar autenticación, permisos de administrador y actualizar la UI (título).
 */
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
  const isSuperUser = localStorage.getItem('is_superuser') === 'true'; 
  
  const tieneSesionActiva = token && !esTokenExpirado(token);

  // REGLA 1: La Puerta Giratoria (Evitar que usuarios logueados vean el login)
  if (to.name === 'login' && tieneSesionActiva) {
    return next('/'); 
  }

  // REGLA 2: El Fantasma (Proteger rutas privadas asegurando que el token esté vivo)
  if (to.meta.requiresAuth && !tieneSesionActiva) {
    // Limpieza preventiva: Si había basura o un token muerto en local, lo destruimos
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('is_superuser');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    localStorage.removeItem('nombre_usuario'); 
    localStorage.removeItem('user_division');
    
    return next('/login');
  }

  // REGLA 3: Control de Acceso (Proteger el acceso a reportes y catálogos)
  if (to.meta.requiresAdmin && !isSuperUser) {
    return next('/'); 
  }
  
  // REGLA 4: Actualización Dinámica del Título de la Pestaña
  if (to.meta.title) {
    document.title = `${to.meta.title} | Sistema de Reservas`;
  } else {
    document.title = 'Sistema de Reservas';
  }

  // Permite que la navegación continúe si pasó todas las validaciones
  next();
});

export default router;