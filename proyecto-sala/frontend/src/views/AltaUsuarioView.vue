<template>
  <div class="container-fluid px-4 py-4 d-flex justify-content-center">
    
    <div class="w-100" style="max-width: 1000px;">
        
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold text-dark mb-0">
                    <i class="bi bi-people-fill text-primary me-2"></i>Alta de Usuarios
                </h2>
                <p class="text-muted small mb-0 mt-1">Alta y administración de credenciales de acceso al sistema.</p>
            </div>
        </div>

        <div class="card shadow-sm border-0 rounded-3 bg-white mb-5">
            <div class="card-body p-4 p-md-5">
            
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
                                <i class="bi bi-person-plus-fill me-1"></i>1. Nuevo Registro Docente
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

                    <div class="d-flex justify-content-end gap-3 mt-4 pt-3 border-top">
                        <button type="button" class="btn btn-light fw-semibold text-secondary px-4" @click="limpiarFormulario" :disabled="cargandoRegistro">
                            <i class="bi bi-eraser me-1"></i> Limpiar
                        </button>
                        <button type="submit" class="btn btn-primary fw-bold px-4 shadow-sm" :disabled="cargandoRegistro || (formulario.password !== formulario.confirmPassword)">
                            <span v-if="cargandoRegistro" class="spinner-border spinner-border-sm me-2"></span>
                            <i v-else class="bi bi-cloud-arrow-up-fill me-1"></i> {{ cargandoRegistro ? 'Procesando...' : 'Registrar Usuario' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <div class="card shadow-sm border-0 rounded-3 bg-white">
            <div class="card-body p-4 p-md-5">
                <h6 class="fw-bold text-primary mb-4 text-uppercase" style="font-size: 0.85rem; letter-spacing: 0.5px;">
                    <i class="bi bi-journal-text me-1"></i>Directorio de Usuarios Activos
                </h6>

                <div v-if="cargandoTabla" class="text-center py-5 text-muted">
                    <div class="spinner-border text-primary mb-2" role="status"></div>
                    <p class="small">Cargando directorio...</p>
                </div>

                <div v-else class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th class="text-secondary small fw-semibold">ID</th>
                                <th class="text-secondary small fw-semibold">Usuario</th>
                                <th class="text-secondary small fw-semibold">Correo</th>
                                <th class="text-secondary small fw-semibold">Perfil</th>
                                <th class="text-secondary small fw-semibold text-center">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="user in listaUsuarios" :key="user.id">
                                <td class="text-muted small fw-bold">#{{ user.id }}</td>
                                <td class="fw-semibold text-dark">{{ user.username }}</td>
                                <td class="text-muted small">{{ user.email || 'No registrado' }}</td>
                                <td>
                                    <span v-if="user.is_superuser" class="badge bg-danger-subtle text-danger border border-danger-subtle rounded-pill">Administrador</span>
                                    <span v-else class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill">Docente</span>
                                </td>
                                <td class="text-center">
                                    <button 
                                        class="btn btn-sm btn-outline-primary shadow-sm fw-semibold" 
                                        title="Actualizar Contraseña"
                                        data-bs-toggle="modal" 
                                        data-bs-target="#modalPassword"
                                        @click="prepararEdicionPassword(user)"
                                    >
                                        <i class="bi bi-shield-lock-fill me-1"></i> Cambiar Clave
                                    </button>
                                </td>   
                            </tr>
                            <tr v-if="listaUsuarios.length === 0">
                                <td colspan="5" class="text-center text-muted py-4 small">No hay usuarios registrados en el sistema.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </div>

    <div class="modal fade" id="modalPassword" tabindex="-1" aria-labelledby="modalPasswordLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
                
                <div class="position-absolute top-0 start-0 w-100" style="height: 5px; background-color: #005f86;"></div>
                
                <div class="modal-header border-0 pb-0 pt-4 px-4">
                    <h5 class="modal-title fw-bold text-dark" id="modalPasswordLabel">
                        <i class="bi bi-shield-lock text-primary me-2"></i>Actualizar Credenciales
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" id="btnCerrarModal"></button>
                </div>
                
                <div class="modal-body px-4 py-4">
                    <p class="text-muted small mb-4">
                        Asigne una nueva contraseña permanente para el usuario 
                        <strong class="text-dark">{{ modalData.username }}</strong>. 
                        La sesión actual de este usuario será terminada por seguridad.
                    </p>

                    <div v-if="modalData.mensajeExito" class="alert alert-success small py-2 d-flex align-items-center fade-in">
                        <i class="bi bi-check-circle-fill me-2"></i> {{ modalData.mensajeExito }}
                    </div>
                    <div v-if="modalData.mensajeError" class="alert alert-danger small py-2 d-flex align-items-center fade-in">
                        <i class="bi bi-x-circle-fill me-2"></i> {{ modalData.mensajeError }}
                    </div>

                    <form @submit.prevent="guardarNuevaPassword">
                        <label class="form-label fw-bold small text-dark-emphasis mb-1">Nueva Contraseña</label>
                        <div class="input-group mb-3">
                            <span class="input-group-text bg-light text-muted border-end-0"><i class="bi bi-key"></i></span>
                            <input 
                                type="text" 
                                class="form-control border-start-0 ps-0 bg-light" 
                                v-model="modalData.nuevaPassword" 
                                placeholder="Escriba la nueva clave segura..."
                                minlength="8"
                                required
                            >
                        </div>
                        <div class="d-flex justify-content-end mt-4">
                            <button type="button" class="btn btn-light fw-semibold text-secondary me-2" data-bs-dismiss="modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary fw-bold shadow-sm" :disabled="modalData.cargando || modalData.nuevaPassword.length < 8">
                                <span v-if="modalData.cargando" class="spinner-border spinner-border-sm me-2"></span>
                                {{ modalData.cargando ? 'Guardando...' : 'Aplicar Cambio' }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import ApiService from '@/services/ApiService';

// --- ESTADO PARA REGISTRO (ARRIBA) ---
const cargandoRegistro = ref(false);
const mensaje = reactive({ tipo: '', texto: '', icono: '' });

const formulario = reactive({
  matricula: '',  
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

// --- ESTADO PARA DIRECTORIO (ABAJO) ---
const listaUsuarios = ref([]);
const cargandoTabla = ref(false);

// --- ESTADO PARA MODAL DE CONTRASEÑA ---
const modalData = reactive({
    idUsuario: null,
    username: '',
    nuevaPassword: '',
    cargando: false,
    mensajeExito: '',
    mensajeError: ''
});

// --- LÓGICA DE DIRECTORIO ---
const cargarDirectorio = async () => {
    cargandoTabla.value = true;
    try {
        const res = await ApiService.obtenerUsuarios();
        listaUsuarios.value = res.data || res;
    } catch (error) {
        console.error("Error al cargar usuarios:", error);
    } finally {
        cargandoTabla.value = false;
    }
};

onMounted(() => {
    cargarDirectorio();
});

// --- LÓGICA DE REGISTRO ---
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

  cargandoRegistro.value = true;

  try {
    const datosEnvio = { ...formulario };
    delete datosEnvio.confirmPassword;

    // Utilizamos la función de crearUsuario que ya tienes en ApiService
    await ApiService.crearUsuario(datosEnvio);

    mensaje.tipo = 'success';
    mensaje.texto = `Credenciales creadas y vinculadas exitosamente a la matrícula ${formulario.matricula}.`;
    mensaje.icono = 'bi bi-check-circle-fill';
    
    // Recargar la tabla inmediatamente para mostrar al nuevo usuario
    cargarDirectorio();
    
    setTimeout(() => limpiarFormulario(), 4000);

  } catch (error) {
    console.error("Error al registrar:", error);
    mensaje.tipo = 'danger';
    mensaje.icono = 'bi bi-x-circle-fill';
    
    if (error.response && error.response.data) {
      const data = error.response.data;
      if (data.username) mensaje.texto = `Error en Usuario: ${data.username[0]}`;
      else if (data.matricula) mensaje.texto = `Error en Matrícula: ${data.matricula[0]}`; 
      else if (data.detail) mensaje.texto = data.detail;
      else mensaje.texto = 'El servidor rechazó el registro. Verifique duplicidad.';
    } else {
      mensaje.texto = 'Error de conexión con el servidor. Intente más tarde.';
    }
  } finally {
    cargandoRegistro.value = false;
  }
};

// --- LÓGICA DEL MODAL ---
const prepararEdicionPassword = (user) => {
    modalData.idUsuario = user.id;
    modalData.username = user.username;
    modalData.nuevaPassword = '';
    modalData.mensajeExito = '';
    modalData.mensajeError = '';
};

const guardarNuevaPassword = async () => {
    modalData.mensajeExito = '';
    modalData.mensajeError = '';
    modalData.cargando = true;

    try {
        await ApiService.actualizarPasswordUsuario(modalData.idUsuario, modalData.nuevaPassword);
        modalData.mensajeExito = 'Se ha cambiado la contraseña correctamente.';
        modalData.nuevaPassword = ''; // Limpiamos por seguridad
        
        // Cerramos el modal automáticamente tras un breve retraso
        setTimeout(() => {
            const btnCerrar = document.getElementById('btnCerrarModal');
            if (btnCerrar) btnCerrar.click();
        }, 1500);

    } catch (error) {
        console.error("Fallo al actualizar contraseña:", error);
        modalData.mensajeError = 'Error de conexión o falta de permisos administrativos.';
    } finally {
        modalData.cargando = false;
    }
};
</script>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

.text-primary { color: #005f86 !important; }
.btn-primary { background-color: #005f86; border-color: #005f86; }
.btn-primary:hover { background-color: #004a69; border-color: #004a69; }
.btn-primary:disabled { background-color: #005f86; opacity: 0.6; }
</style>