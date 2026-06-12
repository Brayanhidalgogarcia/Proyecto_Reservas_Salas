<template>
  <div class="container-fluid px-4 py-4 d-flex justify-content-center">
    
    <div class="w-100" style="max-width: 800px;">
        
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold text-dark mb-0">
                    <i class="bi bi-person-plus-fill text-primary me-2"></i>Alta de Usuarios
                </h2>
                <p class="text-muted small mb-0 mt-1">Vinculación de credenciales para padrón docente existente.</p>
            </div>
        </div>

        <div class="card shadow-sm border-0 rounded-3 bg-white">
            <div class="card-body p-5">
            
                <div v-if="mensaje.texto" class="fade-in mb-4">
                    <div :class="`alert alert-${mensaje.tipo} border-0 shadow-sm d-flex align-items-center mb-0`" role="alert">
                        <i :class="mensaje.icono" class="me-3 fs-4"></i>
                        <div>
                            <strong class="d-block">{{ mensaje.tipo === 'success' ? 'Operación Exitosa' : (mensaje.tipo === 'warning' ? 'Atención' : 'Error del Sistema') }}</strong>
                            <span class="small">{{ mensaje.texto }}</span>
                        </div>
                    </div>
                </div>

                <form @submit.prevent="registrar">
                    
                    <div class="row g-4">
                        
                        <div class="col-12">
                            <h6 class="fw-bold text-primary mb-3 text-uppercase" style="font-size: 0.85rem; letter-spacing: 0.5px;">
                                <i class="bi bi-link-45deg me-1"></i>1. Identificación del Docente
                            </h6>
                            <div class="bg-light p-3 rounded border border-light-subtle">
                                <label class="form-label fw-bold small text-dark-emphasis mb-1">Matrícula Universitaria Registrada</label>
                                <div class="input-group">
                                    <span class="input-group-text bg-white border-end-0 text-muted"><i class="bi bi-upc-scan"></i></span>
                                    <input 
                                        type="text" 
                                        class="form-control border-start-0 ps-0 fw-semibold text-primary" 
                                        v-model="formulario.matricula" 
                                        required 
                                        placeholder="Ej. 12345678"
                                    >
                                </div>
                                <div class="form-text small text-muted mt-2">
                                    <i class="bi bi-info-circle me-1"></i>El sistema buscará en la base de datos de "Maestros" y enlazará esta nueva cuenta automáticamente.
                                </div>
                            </div>
                        </div>

                        <div class="col-12 mt-4">
                            <h6 class="fw-bold text-primary mb-3 text-uppercase border-top pt-4" style="font-size: 0.85rem; letter-spacing: 0.5px;">
                                <i class="bi bi-key-fill me-1"></i>2. Credenciales de Acceso Web
                            </h6>
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold small text-dark-emphasis mb-1">Nombre de Usuario (Alias)</label>
                            <input 
                                type="text" 
                                class="form-control bg-light" 
                                v-model="formulario.username" 
                                required 
                                pattern="^\S+$"
                                title="El nombre de usuario no debe contener espacios"
                                placeholder="Ej. jrodriguez"
                            >
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold small text-dark-emphasis mb-1">Correo Electrónico <span class="fw-normal text-muted">(Opcional)</span></label>
                            <input type="email" class="form-control bg-light" v-model="formulario.email" placeholder="usuario@ujat.mx">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold small text-dark-emphasis mb-1">Contraseña de Acceso</label>
                            <div class="input-group">
                                <span class="input-group-text bg-white text-muted border-end-0"><i class="bi bi-shield-lock"></i></span>
                                <input 
                                    type="password" 
                                    class="form-control border-start-0 ps-0 bg-light" 
                                    v-model="formulario.password" 
                                    minlength="8"
                                    required
                                >
                            </div>
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold small text-dark-emphasis mb-1">Confirmar Contraseña</label>
                            <input 
                                type="password" 
                                class="form-control bg-light" 
                                :class="{'is-invalid': formulario.confirmPassword && formulario.password !== formulario.confirmPassword}"
                                v-model="formulario.confirmPassword" 
                                minlength="8"
                                required
                            >
                        </div>
                    </div>

                    <div class="d-flex justify-content-end gap-3 mt-5 pt-3 border-top">
                        <button type="button" class="btn btn-light fw-semibold text-secondary px-4" @click="limpiarFormulario" :disabled="cargando">
                            <i class="bi bi-eraser me-1"></i> Limpiar
                        </button>
                        <button type="submit" class="btn btn-primary fw-bold px-4 shadow-sm" :disabled="cargando || (formulario.password !== formulario.confirmPassword)">
                            <span v-if="cargando" class="spinner-border spinner-border-sm me-2"></span>
                            <i v-else class="bi bi-cloud-arrow-up-fill me-1"></i> {{ cargando ? 'Procesando Enlace...' : 'Registrar y Vincular' }}
                        </button>
                    </div>

                </form>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import ApiService from '@/services/ApiService';

const cargando = ref(false);
const mensaje = reactive({ tipo: '', texto: '', icono: '' });

const formulario = reactive({
  matricula: '',  
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const limpiarFormulario = () => {
  Object.keys(formulario).forEach(key => formulario[key] = '');
  mensaje.texto = '';
};

const registrar = async () => {
  mensaje.texto = '';
  
  if (formulario.password !== formulario.confirmPassword) {
    mensaje.tipo = 'warning';
    mensaje.texto = 'Las contraseñas no coinciden. Verifique su escritura.';
    mensaje.icono = 'bi bi-exclamation-triangle-fill';
    return;
  }

  cargando.value = true;

  try {
    const datosEnvio = { ...formulario };
    delete datosEnvio.confirmPassword;

    await ApiService.registrarUsuario(datosEnvio);

    mensaje.tipo = 'success';
    mensaje.texto = `Credenciales creadas y vinculadas exitosamente a la matrícula ${formulario.matricula}.`;
    mensaje.icono = 'bi bi-check-circle-fill';
    
    setTimeout(() => limpiarFormulario(), 4000);

  } catch (error) {
    console.error(error);
    mensaje.tipo = 'danger';
    mensaje.icono = 'bi bi-x-circle-fill';
    
    if (error.response && error.response.data) {
      const data = error.response.data;
      if (data.username) mensaje.texto = `Error en Usuario: ${data.username[0]}`;
      else if (data.matricula) mensaje.texto = `Error en Matrícula: ${data.matricula[0]}`; 
      else if (data.detail) mensaje.texto = data.detail;
      else mensaje.texto = 'El servidor rechazó el registro. Verifique que la matrícula exista o que el usuario no esté duplicado.';
    } else {
      mensaje.texto = 'Error de conexión con el servidor. Intente más tarde.';
    }
  } finally {
    cargando.value = false;
  }
};
</script>

<style scoped>
/* Transiciones estéticas */
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

/* Ajustes de color institucional */
.text-primary { color: #005f86 !important; }
.btn-primary { background-color: #005f86; border-color: #005f86; }
.btn-primary:hover { background-color: #004a69; border-color: #004a69; }
.btn-primary:disabled { background-color: #005f86; opacity: 0.6; }
</style>