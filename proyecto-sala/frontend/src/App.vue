<script setup>
/**
 * @file App.vue
 * @description Componente raíz de la aplicación.
 * Gestiona el layout principal (Topbar y Sidebar), el contenedor dinámico de vistas (RouterView),
 * el control de cierre de sesión y la visibilidad del menú según el rol (Admin/Docente).
 */

// ==========================================
// 1. IMPORTS
// ==========================================
import { ref, watch, onMounted } from 'vue'; 
import { RouterLink, RouterView, useRouter, useRoute } from 'vue-router';

// ==========================================
// 2. CONFIGURACIÓN Y COMPOSABLES
// ==========================================
const router = useRouter();
const route = useRoute();

// ==========================================
// 3. ESTADO REACTIVO (Variables)
// ==========================================
const esAdmin = ref(false);

// ==========================================
// 4. PROPIEDADES COMPUTADAS
// ==========================================
// N/A

// ==========================================
// 5. FUNCIONES Y MÉTODOS
// ==========================================

/**
 * Lee el almacenamiento local para determinar si el usuario actual
 * tiene privilegios de superusuario para mostrar las opciones administrativas.
 */
const verificarAdmin = () => {
  esAdmin.value = localStorage.getItem('is_superuser') === 'true';
};

/**
 * Destruye los tokens de seguridad y los datos de identidad local,
 * resetea el estado y expulsa al usuario hacia la pantalla de Login.
 */
const logout = () => {
  if (confirm("¿Estás seguro de que deseas cerrar sesión?")) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('is_superuser');
    localStorage.removeItem('username');
    localStorage.removeItem('nombre_usuario'); 
    localStorage.removeItem('user_division');
    
    esAdmin.value = false; 
    router.push('/login');
  }
}

// ==========================================
// 6. CICLO DE VIDA (Hooks y Watchers)
// ==========================================

onMounted(() => {
  verificarAdmin();
});

// Vigila los cambios de ruta para re-evaluar permisos (Útil en SPAs)
watch(route, () => {
  verificarAdmin();
});
</script>

<template>
  <div v-if="route.name === 'login'" class="w-100 h-100">
      <RouterView />
  </div>

  <div v-else class="app-layout">
   
    <div class="topbar shadow-sm">
      <div class="logo-text">
        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e9/Logo_de_la_UJAT.svg" alt="Logo UJAT" class="logo-img">
        <span class="d-none d-md-inline">Universidad Juárez Autónoma de Tabasco</span>
        <span class="d-md-none">UJAT</span>
      </div>
      
      <div class="topbar-icons">
        <button @click="logout" class="btn btn-outline-light d-flex align-items-center gap-2 py-1 px-3 rounded-2" title="Cerrar Sesión">
            <span class="d-none d-sm-inline fw-semibold" style="font-size: 0.9rem;">Cerrar Sesión</span>
            <i class="bi bi-box-arrow-right fs-6"></i>
        </button>
      </div>
    </div>

    <div class="container-fluid main-container p-0">
      <div class="row flex-nowrap g-0">
        
        <div class="col-auto col-md-3 col-xl-2 px-0 sidebar shadow-sm z-1">
          <div class="d-flex flex-column align-items-center align-items-sm-start pt-3 text-white min-vh-100 w-100">
            
            <ul class="nav nav-pills flex-column mb-sm-auto mb-0 align-items-center align-items-sm-start w-100" id="menu">
              
              <li class="nav-item w-100 mb-1">
                <RouterLink to="/home" class="nav-link align-middle text-dark w-100 transition-all">
                  <i class="bi bi-house-door-fill fs-5 me-sm-2 text-center icon-fixed"></i>
                  <span class="d-none d-sm-inline fw-semibold">Inicio</span>
                </RouterLink>
              </li>

              <li class="nav-item w-100 mb-1">
                <RouterLink to="/disponibilidad" class="nav-link align-middle text-dark w-100 transition-all">
                  <i class="bi bi-calendar-week fs-5 me-sm-2 text-center icon-fixed"></i>
                  <span class="d-none d-sm-inline fw-semibold">Disponibilidad</span>
                </RouterLink>
              </li>
              
              <li class="nav-item w-100 mb-1 border-bottom pb-2">
                <RouterLink to="/reservar" class="nav-link align-middle text-dark w-100 transition-all">
                  <i class="bi bi-calendar-plus-fill fs-5 me-sm-2 text-center icon-fixed"></i>
                  <span class="d-none d-sm-inline fw-semibold">Reservar Sala</span>
                </RouterLink>
              </li>
              
              <div v-if="esAdmin" class="w-100 mt-2">
                <small class="text-muted text-uppercase fw-bold px-3 d-none d-sm-block mb-2" style="font-size: 0.7rem; letter-spacing: 0.5px;">Administración</small>
                
                <li class="nav-item w-100 mb-1">
                  <RouterLink to="/reportes" class="nav-link align-middle text-dark w-100 transition-all">
                    <i class="bi bi-bar-chart-fill fs-5 me-sm-2 text-center icon-fixed"></i>
                    <span class="d-none d-sm-inline fw-semibold">Reportes </span>
                  </RouterLink>
                </li>

                <li class="nav-item w-100 mb-1">
                  <RouterLink to="/admin/alta-usuario" class="nav-link align-middle text-dark w-100 transition-all"> 
                    <i class="bi bi-people-fill fs-5 me-sm-2 text-center icon-fixed"></i>
                    <span class="d-none d-sm-inline fw-semibold">Usuarios</span>
                  </RouterLink>
                </li>

                <li class="nav-item w-100 mb-1">
                  <RouterLink to="/admin/catalogos" class="nav-link align-middle text-dark w-100 transition-all"> 
                    <i class="bi bi-database-fill-gear fs-5 me-sm-2 text-center icon-fixed"></i>
                    <span class="d-none d-sm-inline fw-semibold">Catálogos</span>
                  </RouterLink>
                </li>
              </div>

            </ul>
          </div>
        </div>

        <div class="col py-3 content-area">
          <RouterView />
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.topbar {
  background-color: var(--color-primario, #005f86);
  color: white;
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
  z-index: 10;
}

.logo-text {
  font-weight: bold;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  letter-spacing: 0.5px;
}

.logo-img {
  height: 45px;
  margin-right: 15px;
  filter: drop-shadow(0px 2px 3px rgba(0,0,0,0.2));
}

.sidebar {
  background-color: #f8f9fa;
  border-right: 1px solid #e9ecef;
  overflow-y: auto;
}

.icon-fixed {
  width: 25px;
  display: inline-block;
  color: #6c757d;
  transition: color 0.2s ease;
}

.nav-link {
  padding: 12px 20px;
  font-size: 0.95rem;
  border-left: 4px solid transparent;
}

.nav-link:hover {
  background-color: #e9ecef;
}

.nav-link:hover .icon-fixed {
  color: var(--color-primario, #005f86);
}

/* Estilo avanzado para la vista activa */
.router-link-active {
  background-color: #e9ecef;
  color: var(--color-primario, #005f86) !important;
  border-left: 4px solid var(--color-primario, #005f86);
}

.router-link-active .icon-fixed {
  color: var(--color-primario, #005f86);
}

.transition-all {
  transition: all 0.2s ease;
}

.content-area {
  background-color: #f0f2f5;
  height: calc(100vh - 70px);
  overflow-y: auto;
}
</style>