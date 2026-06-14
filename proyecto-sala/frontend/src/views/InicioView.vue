<<script setup>
import { ref, onMounted } from 'vue';
import ApiService from '@/services/ApiService.js';

const nombreUsuario = ref('Cargando credenciales...');
const rolUsuario = ref('Autenticando...');

// Función experta para descifrar el JWT y sacar tu ID de usuario
function obtenerIdDesdeToken() {
    const token = localStorage.getItem('access_token') || localStorage.getItem('access');
    if (!token) return null;
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''));
        return JSON.parse(jsonPayload).user_id;
    } catch (e) {
        return null;
    }
}

onMounted(async () => {
    const isSuper = String(localStorage.getItem('is_superuser')).toLowerCase() === 'true';
    const userId = localStorage.getItem('user_id') || obtenerIdDesdeToken();

    if (isSuper) {
        rolUsuario.value = 'Administrador del Sistema';
        nombreUsuario.value = 'Administrador'; 
    } else {
        rolUsuario.value = 'Catedrático';
        try {
            // Buscamos en el catálogo de maestros quién es el dueño de esta sesión
            const resMaestros = await ApiService.obtenerMaestros();
            const maestros = resMaestros.data || resMaestros;
            
            const maestroLogueado = maestros.find(m => {
                let uId = m.usuario_id || m.usuario;
                if (typeof uId === 'object' && uId !== null) uId = uId.id;
                return String(uId) === String(userId);
            });

            if (maestroLogueado) {
                // Si te encuentra, arma el saludo perfecto
                nombreUsuario.value = `Maestro ${maestroLogueado.nombre} ${maestroLogueado.apellido_p || ''}`.trim();
            } else {
                nombreUsuario.value = 'Docente';
            }
        } catch (error) {
            console.error("Error al obtener perfil:", error);
            nombreUsuario.value = 'Usuario';
        }
    }
});
</script>

<template>
  <div class="container-fluid p-4 d-flex align-items-center justify-content-center" style="min-height: 85vh;">
    
    <div class="card border-0 shadow-lg rounded-4 overflow-hidden fade-in" style="max-width: 950px; width: 100%;">
      <div class="row g-0">
        
        <div class="col-md-5 d-none d-md-block position-relative" style="background-color: #004c6d; min-height: 400px;">
          
          <div class="position-absolute top-0 start-0 w-100 h-100 opacity-25" style="background-color: #005f86; z-index: 1;"></div>
          
          <img
            src="@/assets/imagenes/ujat-imagen.png"
            alt="Instalaciones UJAT"
            class="w-100 h-100"
            style="position: absolute; top: 0; left: 0; object-fit: cover;"
          >
          
          <div class="position-absolute bottom-0 start-0 w-100 p-4 text-white" style="z-index: 2; background: linear-gradient(to top, rgba(0, 50, 75, 0.95), transparent);">
            <h5 class="fw-bold mb-1" style="letter-spacing: 1px;">UJAT</h5>
            <small class="opacity-75 fw-medium d-block">División Académica de Informática y Sistemas</small>
          </div>
        </div>

        <div class="col-md-7 p-5 bg-white d-flex flex-column justify-content-center position-relative">
          
          <div class="position-absolute top-0 start-0 w-100" style="height: 6px; background-color: #005f86;"></div>

          <div class="mb-4 d-md-none text-center">
             <img src="@/assets/imagenes/ujat-imagen.png" class="img-fluid rounded shadow-sm" style="max-height: 140px; object-fit: cover; width: 100%;">
          </div>

          <span class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 align-self-start mb-4 fw-bold shadow-sm" style="font-size: 0.85rem;">
            <i class="bi bi-shield-check me-1"></i> {{ rolUsuario }}
          </span>

          <h1 class="display-6 fw-bold text-dark mb-2" style="line-height: 1.2;">
            Sistema Institucional <br>de Reservas
          </h1>

          <p class="fs-4 text-secondary mb-4 mt-2">
            Bienvenido de vuelta,<br>
            <span class="fw-bold" style="color: #005f86;">{{ nombreUsuario }}</span>.
          </p>

          <hr class="border-light-subtle mb-4 w-75">

          <p class="text-muted" style="font-size: 0.95rem; line-height: 1.6;">
            Utilice el menú de navegación lateral para consultar la disponibilidad de los espacios audiovisuales, programar sus próximas actividades académicas o acceder a las herramientas correspondientes a su perfil.
          </p>

          <div class="mt-4 pt-2">
            <router-link to="/disponibilidad" class="btn text-white px-4 py-2 fw-semibold shadow-sm rounded-3 transition-all" style="background-color: #005f86; border-color: #005f86;">
              <i class="bi bi-calendar-week me-2"></i>Ver Disponibilidad de Salas
            </router-link>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.fade-in {
    animation: fadeIn 0.6s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Efecto hover suave para el botón */
.btn:hover {
    filter: brightness(1.1);
    transform: translateY(-1px);
}
</style>