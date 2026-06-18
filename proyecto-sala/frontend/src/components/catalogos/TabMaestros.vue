<script setup>
/**
 * @file TabMaestros.vue
 * @description Sub-componente del módulo de Catálogos.
 * Gestiona el CRUD del Padrón Docente (Catedráticos).
 * Implementa carga paralela para resolver la llave foránea de la División
 * a la que pertenece cada maestro.
 */

// ==========================================
// 1. IMPORTS
// ==========================================
import { ref, reactive, onMounted } from 'vue';
import ApiService from '@/services/ApiService.js';

// ==========================================
// 2. ESTADO REACTIVO (Variables)
// ==========================================
const maestros = ref([]);
const divisiones = ref([]);
const cargandoTabla = ref(false);
const guardando = ref(false);
const modoEdicion = ref(false);
const matriculaOriginal = ref(null); 
const mensaje = reactive({ tipo: '', texto: '', icono: '' });

const formulario = reactive({
  matricula_m: '',
  nombre: '',
  apellido_p: '',
  apellido_m: '',
  division: null
});

// ==========================================
// 3. FUNCIONES Y MÉTODOS
// ==========================================

/**
 * Consulta la base de datos de Maestros y Divisiones simultáneamente (Carga Paralela).
 */
const cargarDatos = async () => {
  cargandoTabla.value = true;
  try {
    const [resMaestros, resDivisiones] = await Promise.all([
      ApiService.obtenerMaestros(),
      ApiService.obtenerDivisiones()
    ]);
    maestros.value = resMaestros.data || resMaestros;
    divisiones.value = resDivisiones.data || resDivisiones;
  } catch (error) {
    console.error("Error al cargar maestros:", error);
    mostrarMensaje('danger', 'Error al sincronizar con el servidor.', 'bi-wifi-off');
  } finally {
    cargandoTabla.value = false;
  }
};

/**
 * Registra o actualiza el expediente de un catedrático.
 */
const guardarMaestro = async () => {
  guardando.value = true;
  ocultarMensaje();

  try {
    const payload = {
      matricula_m: formulario.matricula_m,
      nombre: formulario.nombre,
      apellido_p: formulario.apellido_p,
      apellido_m: formulario.apellido_m || null,
      division: formulario.division
    };

    if (modoEdicion.value) {
      await ApiService.actualizarMaestro(matriculaOriginal.value, payload);
      mostrarMensaje('success', 'Expediente docente actualizado.', 'bi-check-circle-fill');
    } else {
      await ApiService.crearMaestro(payload);
      mostrarMensaje('success', 'Docente registrado exitosamente.', 'bi-check-circle-fill');
    }

    cancelarEdicion();
    await cargarDatos();
    
  } catch (error) {
    console.error("Error al guardar maestro:", error);
    const detalle = error.response?.data?.detail || error.response?.data?.matricula_m?.[0] || 'Revisa que la matrícula no esté duplicada.';
    mostrarMensaje('danger', `Error: ${detalle}`, 'bi-exclamation-octagon-fill');
  } finally {
    guardando.value = false;
  }
};

/**
 * Da de baja a un docente del padrón. Captura errores de protección (ProtectedError)
 * si el maestro ya tiene cuentas de usuario creadas o reservas en el historial.
 * @param {string} matricula - Matrícula universitaria del maestro.
 */
const eliminarMaestro = async (matricula) => {
  if (!confirm(`¿Eliminar al docente con matrícula ${matricula}? Esto podría afectar el historial de reservas.`)) return;
  
  try {
    await ApiService.eliminarMaestro(matricula);
    mostrarMensaje('success', 'Docente dado de baja del sistema.', 'bi-trash-fill');
    
    if (formulario.matricula_m === matricula) cancelarEdicion();
    await cargarDatos();
  } catch (error) {
    const status = error.response?.status;
    if (status === 403) {
      mostrarMensaje('danger', 'Permisos insuficientes.', 'bi-shield-lock-fill');
    } else if (status === 409 || error.response?.data?.ProtectedError || error.response?.data?.detail?.includes('Protect')) {
      mostrarMensaje('warning', 'Existen cuentas de usuario o reservas ancladas a este maestro.', 'bi-exclamation-triangle-fill');
    } else {
      mostrarMensaje('danger', 'Error interno del servidor.', 'bi-bug-fill');
    }
  }
};

/**
 * Carga los datos de la tabla al formulario lateral y aísla la matrícula original.
 */
const prepararEdicion = (maestro) => {
  modoEdicion.value = true;
  matriculaOriginal.value = maestro.matricula_m; 
  formulario.matricula_m = maestro.matricula_m;
  formulario.nombre = maestro.nombre;
  formulario.apellido_p = maestro.apellido_p;
  formulario.apellido_m = maestro.apellido_m || '';
  
  formulario.division = (maestro.division && typeof maestro.division === 'object') 
                        ? (maestro.division.nombre_division || maestro.division.clave_division) 
                        : maestro.division;
                        
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const cancelarEdicion = () => {
  modoEdicion.value = false;
  matriculaOriginal.value = null;
  formulario.matricula_m = '';
  formulario.nombre = '';
  formulario.apellido_p = '';
  formulario.apellido_m = '';
  formulario.division = null;
};

const mostrarMensaje = (tipo, texto, icono) => {
  mensaje.tipo = tipo;
  mensaje.texto = texto;
  mensaje.icono = icono;
  setTimeout(() => ocultarMensaje(), 5000);
};

const ocultarMensaje = () => { mensaje.texto = ''; };

/**
 * Mapea el objeto foráneo de la división para extraer su nombre legible.
 * Adaptado para soportar tanto identificadores directos como objetos serializados.
 */
const obtenerNombreDivision = (divisionIdObj) => {
  if (!divisionIdObj) return 'Sin Asignar';
  const divId = typeof divisionIdObj === 'object' ? divisionIdObj.nombre_division : divisionIdObj;
  const div = divisiones.value.find(d => String(d.nombre_division) === String(divId));
  return div ? div.nombre_division : 'División Desconocida';
};

// ==========================================
// 4. CICLO DE VIDA (Hooks)
// ==========================================
onMounted(() => {
  cargarDatos();
});
</script>

<template>
  <div class="fade-in">
    
    <div v-if="mensaje.texto" :class="`alert alert-${mensaje.tipo} shadow-sm border-0 d-flex align-items-center mb-4`">
      <i :class="mensaje.icono" class="me-2 fs-5"></i>
      {{ mensaje.texto }}
    </div>

    <div class="row g-4">
      
      <div class="col-lg-8">
        <div class="card shadow-sm border-light-subtle rounded-3 h-100 bg-white">
          <div class="card-header bg-white border-bottom py-3 d-flex justify-content-between align-items-center">
            <h6 class="mb-0 fw-bold text-dark"><i class="bi bi-person-badge-fill me-2 text-primary-custom"></i>Padrón Docente</h6>
            <button class="btn btn-sm btn-outline-secondary shadow-sm fw-semibold" @click="cargarDatos" :disabled="cargandoTabla">
              <i class="bi bi-arrow-clockwise" :class="{'spin-icon': cargandoTabla}"></i> Sincronizar
            </button>
          </div>
          
          <div class="card-body p-0">
            
            <div v-if="cargandoTabla" class="text-center py-5 text-muted">
              <div class="spinner-border text-primary-custom mb-2" role="status"></div>
              <p class="small fw-semibold">Cargando padrón...</p>
            </div>

            <div v-else-if="maestros.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-person-x display-4 opacity-25 mb-3 d-block"></i>
              <h6 class="fw-bold text-dark">No hay maestros registrados</h6>
              <p class="small mb-0">Comienza a nutrir el padrón docente desde el panel lateral.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="custom-table-header">
                  <tr>
                    <th class="ps-4">Matrícula</th>
                    <th>Nombre Completo</th>
                    <th>División</th>
                    <th class="text-end pe-4">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="maestro in maestros" :key="maestro.matricula_m" class="border-bottom border-light-subtle">
                    <td class="ps-4 text-muted font-monospace small">{{ maestro.matricula_m }}</td>
                    <td class="fw-bold text-dark">
                      {{ maestro.nombre }} {{ maestro.apellido_p }} {{ maestro.apellido_m || '' }}
                    </td>
                    <td class="text-muted small">
                      <span class="badge bg-light text-secondary border">
                        {{ obtenerNombreDivision(maestro.division) }}
                      </span>
                    </td>
                    <td class="text-end pe-4">
                      <div class="btn-group gap-2">
                        <button 
                          @click="prepararEdicion(maestro)" 
                          class="btn btn-sm btn-outline-primary border-0"
                          title="Editar Maestro"
                        >
                          <i class="bi bi-pencil-square fs-6"></i>
                        </button>
                        <button 
                          @click="eliminarMaestro(maestro.matricula_m)" 
                          class="btn btn-sm btn-outline-danger border-0"
                          title="Eliminar Maestro"
                        >
                          <i class="bi bi-trash3-fill fs-6"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card shadow-sm border-0 border-top border-4 rounded-3 h-100 bg-white" :class="modoEdicion ? 'border-warning' : 'border-primary-custom'">
          <div class="card-body p-4">
            
            <h6 class="fw-bold mb-3 d-flex align-items-center" :class="modoEdicion ? 'text-warning-emphasis' : 'text-primary-custom'">
              <i class="bi me-2" :class="modoEdicion ? 'bi-pencil-fill' : 'bi-person-plus-fill'"></i>
              {{ modoEdicion ? 'Editar Registro Docente' : 'Nuevo Docente' }}
            </h6>
            
            <hr class="text-muted opacity-25 mb-4">

            <form @submit.prevent="guardarMaestro">
              
              <div class="mb-3">
                <label class="form-label fw-bold small text-dark-emphasis">Matrícula Universitaria</label>
                <div class="input-group">
                  <span class="input-group-text bg-white text-muted"><i class="bi bi-upc-scan"></i></span>
                  <input 
                    type="text" 
                    class="form-control font-monospace" 
                    :class="modoEdicion ? 'bg-secondary-subtle text-muted' : 'bg-light'"
                    v-model="formulario.matricula_m" 
                    required
                    :disabled="modoEdicion"
                    placeholder="Ej. 12345678"
                  >
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold small text-dark-emphasis">Nombre(s)</label>
                <input 
                  type="text" 
                  class="form-control bg-light border-light-subtle" 
                  v-model="formulario.nombre" 
                  required
                >
              </div>

              <div class="row g-2 mb-3">
                <div class="col-6">
                  <label class="form-label fw-bold small text-dark-emphasis">Apellido Paterno</label>
                  <input 
                    type="text" 
                    class="form-control bg-light border-light-subtle" 
                    v-model="formulario.apellido_p" 
                    required
                  >
                </div>
                <div class="col-6">
                  <label class="form-label fw-bold small text-dark-emphasis">Apellido Materno</label>
                  <input 
                    type="text" 
                    class="form-control bg-light border-light-subtle" 
                    v-model="formulario.apellido_m"
                  >
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label fw-bold small text-dark-emphasis">División de Adscripción</label>
                <select class="form-select bg-light border-light-subtle" v-model="formulario.division" required>
                  <option :value="null">Seleccionar...</option>
                  <option v-for="div in divisiones" :key="div.nombre_division" :value="div.nombre_division">
                    {{ div.nombre_division }}
                  </option>
                </select>
              </div>

              <div class="d-grid gap-2 mt-4">
                <button type="submit" class="btn fw-bold shadow-sm" :class="modoEdicion ? 'btn-warning text-dark' : 'btn-primary-custom text-white'" :disabled="guardando">
                  <span v-if="guardando" class="spinner-border spinner-border-sm me-2"></span>
                  {{ guardando ? 'Guardando...' : (modoEdicion ? 'Actualizar Docente' : 'Registrar Docente') }}
                </button>
                <button v-if="modoEdicion" type="button" class="btn btn-light fw-semibold text-muted border shadow-sm" @click="cancelarEdicion" :disabled="guardando">
                  Cancelar Edición
                </button>
              </div>

            </form>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Transición de entrada */
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

/* Estandarización de Colores Institucionales UJAT */
.text-primary-custom { color: #005f86 !important; }
.btn-primary-custom { background-color: #005f86; border-color: #005f86; }
.btn-primary-custom:hover { background-color: #004a69; border-color: #004a69; }
.btn-outline-primary { color: #005f86; border-color: #005f86; }
.btn-outline-primary:hover { background-color: #005f86; color: white; }
.border-primary-custom { border-color: #005f86 !important; }

/* Estilos de tabla unificados */
.custom-table-header { background-color: #005f86 !important; }
.custom-table-header th {
  color: #ffffff !important;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  padding-top: 10px;
  padding-bottom: 10px;
  border: none;
}

/* Animación sutil de sincronización */
@keyframes spin { 100% { transform: rotate(360deg); } }
.spin-icon { animation: spin 1s linear infinite; display: inline-block; }
</style>