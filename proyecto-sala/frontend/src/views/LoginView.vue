<script setup>
/**
 * @file LoginView.vue
 * @description Pantalla de autenticación principal del sistema.
 * Gestiona la obtención de tokens JWT y la persistencia de la sesión
 * en el navegador (LocalStorage) antes de redirigir al panel administrativo.
 */

// ==========================================
// 1. IMPORTS
// ==========================================
import { ref } from 'vue';
import { useRouter } from 'vue-router';

// ==========================================
// 2. CONFIGURACIÓN Y COMPOSABLES
// ==========================================
const router = useRouter();

// ==========================================
// 3. ESTADO REACTIVO (Variables)
// ==========================================
const form = ref({
  username: "", 
  password: ""
});

const error = ref(null);
const cargando = ref(false);

// ==========================================
// 4. PROPIEDADES COMPUTADAS
// ==========================================
// N/A para esta vista

// ==========================================
// 5. FUNCIONES Y MÉTODOS
// ==========================================

/**
 * Valida las credenciales en el frontend, solicita el token de acceso al servidor Django,
 * y en caso de éxito, almacena los datos de identidad para mantener la sesión activa.
 */
async function login() {
  if (!form.value.username || !form.value.password) {
    error.value = "Por favor, completa todos los campos.";
    return;
  }
  
  cargando.value = true;
  error.value = null;

  try {
    const response = await fetch('http://127.0.0.1:8000/api/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: form.value.username,
            password: form.value.password
        })
    });

    const data = await response.json();

    if (response.ok) {
        // 1. Guardar Tokens de Seguridad
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        
        // 2. Guardar Identidad y Permisos
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('is_superuser', data.is_superuser); 
        
        const nombreMostrar = data.nombre_completo || data.username;
        localStorage.setItem('nombre_usuario', nombreMostrar);
        localStorage.setItem('user_division', data.division || '');

        // 3. Redirección nativa de Vue (Sin recargar la página)
        router.push('/home'); 

    } else {
        error.value = data.detail || "Usuario o contraseña incorrectos.";
    }

  } catch (err) {
    error.value = "Error de conexión. Verifica que el servidor Backend esté encendido.";
    console.error("Error de red:", err);
  } finally {
    cargando.value = false;
  }
}

// ==========================================
// 6. CICLO DE VIDA (Hooks)
// ==========================================
// N/A para esta vista
</script>

<template>
  <div class="login-container">
    
    <div class="left-side"></div>

    <div class="right-side">
      <div class="topbar shadow-sm">
        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e9/Logo_de_la_UJAT.svg" alt="Logo UJAT">
        <span class="fw-bold fs-4">Universidad Juárez Autónoma de Tabasco</span>
      </div>

      <div class="form-box">
        <div class="form-box-inner p-4 p-md-5 bg-white rounded-4 shadow-sm border border-light-subtle">
          <h3 class="fw-bold text-dark mb-1">Inicia sesión</h3>
          <p class="text-muted small mb-4">Ingresa tus credenciales administrativas para continuar.</p>
          
          <div v-if="error" class="alert alert-danger border-0 shadow-sm d-flex align-items-center fade-in py-2">
            <i class="bi bi-exclamation-triangle-fill me-2 fs-5"></i> {{ error }}
          </div>

          <form @submit.prevent="login">
            <div class="mb-3">
              <label for="username" class="form-label fw-bold small text-dark-emphasis mb-1">Usuario</label> 
              <div class="input-group">
                <span class="input-group-text bg-light text-muted border-end-0"><i class="bi bi-person-fill"></i></span>
                <input type="text" v-model="form.username" class="form-control border-start-0 ps-0 bg-light" id="username" placeholder="Tu usuario administrativo" required>
              </div>
            </div>

            <div class="mb-4">
              <label for="password" class="form-label fw-bold small text-dark-emphasis mb-1">Contraseña</label>
              <div class="input-group">
                <span class="input-group-text bg-light text-muted border-end-0"><i class="bi bi-lock-fill"></i></span>
                <input type="password" v-model="form.password" class="form-control border-start-0 ps-0 bg-light" id="password" placeholder="Tu contraseña" required>
              </div>
            </div>

            <button type="submit" class="btn btn-primary w-100 py-2 fw-bold shadow-sm" :disabled="cargando">
              <span v-if="cargando" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-box-arrow-in-right me-2"></i>
              {{ cargando ? 'Verificando...' : 'Acceder al Sistema' }}
            </button>
          </form>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

/* Botones y colores institucionales */
.text-primary { color: #005f86 !important; }
.btn-primary { background-color: #005f86; border-color: #005f86; }
.btn-primary:hover { background-color: #004a69; border-color: #004a69; }
.btn-primary:disabled { background-color: #005f86; opacity: 0.6; }

.login-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: #f8f9fa;
}

.left-side {
  flex: 0.5;
  background: url('@/assets/imagenes/sesion.jpg') no-repeat center center; 
  background-size: cover;
  filter: brightness(0.9);
  background-color: #e9ecef; 
  border-right: 1px solid rgba(0,0,0,0.1);
}

@media (max-width: 768px) {
  .left-side { display: none; }
  .right-side { flex: 1; }
}

.right-side {
  flex: 0.5;
  display: flex;
  flex-direction: column;
  background: #f8f9fa; /* Fondo ligeramente gris para resaltar el formulario blanco */
}

.topbar {
  background-color: #005f86; /* Azul UJAT duro en caso de que var() falle */
  background-color: var(--color-primario, #005f86);
  color: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  z-index: 10;
}

.topbar img {
  height: 50px; 
  margin-right: 15px;
  filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.2));
}

.form-box {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow-y: auto;
  padding: 20px;
}

.form-box-inner {
  width: 100%;
  max-width: 450px;
}
</style>