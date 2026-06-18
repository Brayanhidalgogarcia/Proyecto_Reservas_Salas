<script setup>
/**
 * @file TabEdificios.vue
 * @description Sub-componente del módulo de Catálogos.
 * Proporciona un CRUD (Crear, Leer, Actualizar, Eliminar) para los edificios.
 * Implementa la carga paralela de catálogos foráneos (Divisiones) para
 * mantener la integridad relacional de los datos en el formulario.
 */

// ==========================================
// 1. IMPORTS
// ==========================================
import { ref, reactive, onMounted } from 'vue';
import ApiService from '@/services/ApiService.js';

// ==========================================
// 2. CONFIGURACIÓN Y COMPOSABLES
// ==========================================
// N/A

// ==========================================
// 3. ESTADO REACTIVO (Variables)
// ==========================================
const edificios = ref([]);
const divisiones = ref([]);
const cargandoTabla = ref(false);
const guardando = ref(false);
const modoEdicion = ref(false);
const mensaje = reactive({ tipo: '', texto: '', icono: '' });

const formulario = reactive({
  id: null,
  nombre_edificio: '',
  division: null
});

// ==========================================
// 4. PROPIEDADES COMPUTADAS
// ==========================================
// N/A

// ==========================================
// 5. FUNCIONES Y MÉTODOS
// ==========================================

/**
 * Consulta la base de datos de Edificios y Divisiones simultáneamente (Carga Paralela).
 */
const cargarDatos = async () => {
  cargandoTabla.value = true;
  try {
    const [resEdificios, resDivisiones] = await Promise.all([
      ApiService.obtenerEdificios(),
      ApiService.obtenerDivisiones()
    ]);
    
    edificios.value = resEdificios.data || resEdificios;
    divisiones.value = resDivisiones.data || resDivisiones;
    
  } catch (error) {
    console.error("Error al cargar catálogos:", error);
    mostrarMensaje('danger', 'Error al sincronizar con el servidor. Verifica tu conexión.', 'bi-wifi-off');
  } finally {
    cargandoTabla.value = false;
  }
};

/**
 * Orquesta la creación (POST) o actualización (PUT) de un edificio.
 */
const guardarEdificio = async () => {
  guardando.value = true;
  ocultarMensaje();

  try {
    const payload = {
      nombre_edificio: formulario.nombre_edificio,
      division: formulario.division
    };

    if (modoEdicion.value) {
      await ApiService.actualizarEdificio(formulario.id, payload);
      mostrarMensaje('success', 'Edificio actualizado correctamente.', 'bi-check-circle-fill');
    } else {
      await ApiService.crearEdificio(payload);
      mostrarMensaje('success', 'Nuevo edificio registrado con éxito.', 'bi-check-circle-fill');
    }

    cancelarEdicion();
    await cargarDatos(); 
    
  } catch (error) {
    console.error("Error al guardar edificio:", error);
    const detalle = error.response?.data?.detail || error.response?.data?.nombre_edificio?.[0] || 'Revisa que los datos sean correctos.';
    mostrarMensaje('danger', `Error al guardar: ${detalle}`, 'bi-exclamation-octagon-fill');
  } finally {
    guardando.value = false;
  }
};

/**
 * Elimina el registro físico protegiendo la integridad de la base de datos (ProtectedError).
 * @param {number|string} id - Llave primaria del edificio.
 */
const eliminarEdificio = async (id) => {
  if (!confirm('ATENCIÓN: Si eliminas este edificio, las salas y reservas asociadas podrían verse afectadas. ¿Estás seguro?')) return;
  
  try {
    await ApiService.eliminarEdificio(id);
    mostrarMensaje('success', 'Edificio eliminado de la base de datos.', 'bi-trash-fill');
    
    if (formulario.id === id) cancelarEdicion();
    await cargarDatos();
  } catch (error) {
    const status = error.response?.status;
    if (status === 403) {
      mostrarMensaje('danger', 'No tienes permisos de superusuario para borrar este registro.', 'bi-shield-lock-fill');
    } else if (status === 409 || error.response?.data?.ProtectedError || error.response?.data?.detail?.includes('Protect')) {
      mostrarMensaje('warning', 'No se puede borrar porque existen salas asignadas a este edificio.', 'bi-exclamation-triangle-fill');
    } else {
      mostrarMensaje('danger', 'Error interno del servidor al intentar eliminar.', 'bi-bug-fill');
    }
  }
};

/**
 * Extrae la llave foránea de la división y prepara el formulario.
 * @param {Object} edificio - El objeto de datos a editar.
 */
const prepararEdicion = (edificio) => {
  modoEdicion.value = true;
  formulario.id = edificio.id;
  formulario.nombre_edificio = edificio.nombre_edificio;
  
  formulario.division = (edificio.division && typeof edificio.division === 'object') 
                        ? (edificio.division.id || edificio.division.clave_division) 
                        : edificio.division;
                        
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const cancelarEdicion = () => {
  modoEdicion.value = false;
  formulario.id = null;
  formulario.nombre_edificio = '';
  formulario.division = null;
};

/**
 * Función resolutiva que busca el nombre legible de una división a partir de su ID.
 * @param {string|number|Object} divisionIdObj - Referencia de la división.
 * @returns {string} Nombre legible o fallback.
 */
const obtenerNombreDivision = (divisionIdObj) => {
  if (!divisionIdObj) return 'Sin Asignar';
  
  const divId = typeof divisionIdObj === 'object' ? (divisionIdObj.id || divisionIdObj.clave_division) : divisionIdObj;
  const div = divisiones.value.find(d => String(d.id || d.clave_division) === String(divId));
  
  return div ? (div.nombre_division || div.nombre || div.clave_division) : 'División Desconocida';
};

const mostrarMensaje = (tipo, texto, icono) => {
  mensaje.tipo = tipo;
  mensaje.texto = texto;
  mensaje.icono = icono;
  setTimeout(() => ocultarMensaje(), 5000); 
};

const ocultarMensaje = () => { mensaje.texto = ''; };

// ==========================================
// 6. CICLO DE VIDA (Hooks)
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
            <h6 class="mb-0 fw-bold text-dark"><i class="bi bi-list-ul me-2 text-primary-custom"></i>Edificios Registrados</h6>
            <button class="btn btn-sm btn-outline-secondary shadow-sm fw-semibold" @click="cargarDatos" :disabled="cargandoTabla">
              <i class="bi bi-arrow-clockwise" :class="{'spin-icon': cargandoTabla}"></i> Sincronizar
            </button>
          </div>
          
          <div class="card-body p-0">
            
            <div v-if="cargandoTabla" class="text-center py-5 text-muted">
              <div class="spinner-border text-primary-custom mb-2" role="status"></div>
              <p class="small fw-semibold">Cargando infraestructura...</p>
            </div>

            <div v-else-if="edificios.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-building-slash display-4 opacity-25 mb-3 d-block"></i>
              <h6 class="fw-bold text-dark">No hay edificios registrados</h6>
              <p class="small mb-0">Utiliza el formulario lateral para dar de alta la primera instalación.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="custom-table-header">
                  <tr>
                    <th class="ps-4">Nombre del Edificio</th>
                    <th>División Académica</th>
                    <th class="text-end pe-4">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="edificio in edificios" :key="edificio.id" class="border-bottom border-light-subtle">
                    <td class="ps-4 fw-bold text-dark">{{ edificio.nombre_edificio }}</td>
                    <td class="text-muted small">
                      <span class="badge bg-light text-secondary border">
                        {{ obtenerNombreDivision(edificio.division) }}
                      </span>
                    </td>
                    <td class="text-end pe-4">
                      <div class="btn-group gap-2">
                        <button 
                          @click="prepararEdicion(edificio)" 
                          class="btn btn-sm btn-outline-primary border-0"
                          title="Editar Edificio"
                        >
                          <i class="bi bi-pencil-square fs-6"></i>
                        </button>
                        <button 
                          @click="eliminarEdificio(edificio.id)" 
                          class="btn btn-sm btn-outline-danger border-0"
                          title="Eliminar Edificio"
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
              <i class="bi me-2" :class="modoEdicion ? 'bi-pencil-fill' : 'bi-plus-circle-fill'"></i>
              {{ modoEdicion ? 'Editar Edificio' : 'Nuevo Edificio' }}
            </h6>
            
            <hr class="text-muted opacity-25 mb-4">

            <form @submit.prevent="guardarEdificio">
              
              <div class="mb-3">
                <label class="form-label fw-bold small text-dark-emphasis">Nombre del Edificio</label>
                <input 
                  type="text" 
                  class="form-control bg-light border-light-subtle" 
                  v-model="formulario.nombre_edificio" 
                  required
                  placeholder="Ej. Edificio F, Laboratorios..."
                >
              </div>

              <div class="mb-4">
                <label class="form-label fw-bold small text-dark-emphasis">División a la que pertenece</label>
                <select class="form-select bg-light border-light-subtle" v-model="formulario.division" required>
                  <option :value="null">Seleccionar División...</option>
                  <option v-for="div in divisiones" :key="div.id || div.clave_division" :value="div.id || div.clave_division">
                    {{ div.nombre_division || div.nombre || div.clave_division }}
                  </option>
                </select>
                
              </div>

              <div class="d-grid gap-2 mt-4">
                <button type="submit" class="btn fw-bold shadow-sm" :class="modoEdicion ? 'btn-warning text-dark' : 'btn-primary-custom text-white'" :disabled="guardando">
                  <span v-if="guardando" class="spinner-border spinner-border-sm me-2"></span>
                  {{ guardando ? 'Guardando...' : (modoEdicion ? 'Actualizar Cambios' : 'Registrar Edificio') }}
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