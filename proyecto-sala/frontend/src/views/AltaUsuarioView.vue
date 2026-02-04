<template>
  <div class="container-fluid px-4 py-4">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold text-dark mb-0">Agregar Usuario</h2>
    </div>

    <div class="card shadow-sm border rounded-3">
      <div class="card-body p-4">
        
      
        <div v-if="mensaje.texto" :class="`alert alert-${mensaje.tipo} d-flex align-items-center`" role="alert">
          <i :class="mensaje.icono" class="me-2 fs-5"></i>
          <div>{{ mensaje.texto }}</div>
        </div>

        <p class="text-muted mb-4 small">
          Ingrese la matrícula del docente para vincularle una nueva cuenta de acceso.
        </p>

        <form @submit.prevent="registrar">
          
          <div class="row g-3">
            
            
            <div class="col-12">
              <h6 class="border-bottom pb-2 text-primary">Identificación del Docente</h6>
            </div>

            <div class="col-md-6">
              <label class="form-label fw-bold small text-secondary">Matrícula del Maestro:</label>
              <div class="input-group">
                <span class="input-group-text bg-white text-muted"><i class="bi bi-person-vcard"></i></span>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="formulario.matricula" 
                  required 
                  placeholder="Ej. 19203040"
                >
              </div>
              <div class="form-text small">El sistema buscará al maestro en el padrón automáticamente.</div>
            </div>

           
            <div class="col-12 mt-4">
              <h6 class="border-bottom pb-2 text-primary">Credenciales de Acceso</h6>
            </div>

            <div class="col-md-6">
              <label class="form-label fw-bold small text-secondary">Nombre de Usuario:</label>
              <input type="text" class="form-control" v-model="formulario.username" required placeholder="Ej. juan.perez">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-bold small text-secondary">Email (Opcional):</label>
              <input type="email" class="form-control" v-model="formulario.email" placeholder="correo@institucional.mx">
            </div>

            <div class="col-md-6">
              <label class="form-label fw-bold small text-secondary">Contraseña:</label>
              <input type="password" class="form-control" v-model="formulario.password" required>
            </div>

            <div class="col-md-6">
              <label class="form-label fw-bold small text-secondary">Confirmar Contraseña:</label>
              <input type="password" class="form-control" v-model="formulario.confirmPassword" required>
            </div>

          </div>

        
          <div class="d-flex justify-content-end gap-2 mt-4 pt-3 border-top">
            <button type="button" class="btn btn-outline-secondary" @click="limpiarFormulario">
              Cancelar
            </button>
            <button type="submit" class="btn btn-primary px-4" :disabled="cargando">
              <span v-if="cargando" class="spinner-border spinner-border-sm me-2"></span>
              {{ cargando ? 'Vinculando...' : 'Crear Usuario' }}
            </button>
          </div>

        </form>
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
    mensaje.texto = 'Las contraseñas no coinciden.';
    mensaje.icono = 'bi bi-exclamation-triangle-fill';
    return;
  }

  cargando.value = true;

  try {
    const datosEnvio = { ...formulario };
    delete datosEnvio.confirmPassword;

    await ApiService.registrarUsuario(datosEnvio);

    mensaje.tipo = 'success';
    mensaje.texto = `Usuario creado y vinculado correctamente al maestro con matrícula ${formulario.matricula}.`;
    mensaje.icono = 'bi bi-check-circle-fill';
    
    setTimeout(() => limpiarFormulario(), 3000);

  } catch (error) {
    console.error(error);
    mensaje.tipo = 'danger';
    mensaje.icono = 'bi bi-x-circle-fill';
    
    if (error.response && error.response.data) {
      
      const data = error.response.data;
      
      if (data.username) mensaje.texto = `Usuario: ${data.username[0]}`;
      else if (data.matricula) mensaje.texto = data.matricula[0]; 
      else if (data.detail) mensaje.texto = data.detail;
      else mensaje.texto = 'Error al registrar. Verifique los datos.';
    } else {
      mensaje.texto = 'Error de conexión con el servidor.';
    }
  } finally {
    cargando.value = false;
  }
};
</script>

<style scoped>
.card { border-color: #dee2e6; }
.form-label { color: #495057; }
</style>