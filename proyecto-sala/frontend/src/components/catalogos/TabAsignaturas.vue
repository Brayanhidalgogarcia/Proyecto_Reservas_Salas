<script setup>
/**
 * @file TabAsignaturas.vue
 * @description Sub-componente del módulo de Catálogos.
 * Proporciona un CRUD (Crear, Leer, Actualizar, Eliminar) para el padrón de materias.
 * Utiliza un diseño de pantalla dividida (Tabla / Formulario) para agilizar la gestión.
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
const asignaturas = ref([]);
const cargandoTabla = ref(false);
const guardando = ref(false);
const modoEdicion = ref(false);
const claveOriginal = ref(null); // Almacena la llave primaria real para solicitudes PUT
const mensaje = reactive({ tipo: '', texto: '', icono: '' });

const formulario = reactive({
  clave_asignatura: '',
  nombre_asignatura: ''
});

// ==========================================
// 4. PROPIEDADES COMPUTADAS
// ==========================================
// N/A

// ==========================================
// 5. FUNCIONES Y MÉTODOS
// ==========================================

/**
 * Utilidades para el manejo de alertas visuales no intrusivas.
 */
const mostrarMensaje = (tipo, texto, icono) => {
  mensaje.tipo = tipo;
  mensaje.texto = texto;
  mensaje.icono = icono;
  setTimeout(() => ocultarMensaje(), 5000);
};

const ocultarMensaje = () => { mensaje.texto = ''; };

/**
 * Consulta el catálogo completo de asignaturas desde el servidor.
 */
const cargarDatos = async () => {
  cargandoTabla.value = true;
  try {
    const response = await ApiService.obtenerAsignaturas();
    asignaturas.value = response.data || response;
  } catch (error) {
    console.error("Error al cargar asignaturas:", error);
    mostrarMensaje('danger', 'Error al sincronizar con el servidor.', 'bi-wifi-off');
  } finally {
    cargandoTabla.value = false;
  }
};

/**
 * Orquesta la creación (POST) o actualización (PUT) de un registro.
 * La validación de la llave primaria (clave) se delega al backend.
 */
const guardarAsignatura = async () => {
  guardando.value = true;
  ocultarMensaje();

  try {
    const payload = {
      clave_asignatura: formulario.clave_asignatura,
      nombre_asignatura: formulario.nombre_asignatura
    };

    if (modoEdicion.value) {
      // Inyección de la clave guardada en memoria (claveOriginal) a la URL
      await ApiService.actualizarAsignatura(claveOriginal.value, payload);
      mostrarMensaje('success', 'Asignatura actualizada correctamente.', 'bi-check-circle-fill');
    } else {
      await ApiService.crearAsignatura(payload);
      mostrarMensaje('success', 'Nueva asignatura registrada con éxito.', 'bi-check-circle-fill');
    }

    cancelarEdicion();
    await cargarDatos();
    
  } catch (error) {
    console.error("Error al guardar asignatura:", error);
    const detalle = error.response?.data?.detail || error.response?.data?.clave_asignatura?.[0] || 'Verifica que la clave no esté duplicada.';
    mostrarMensaje('danger', `Error: ${detalle}`, 'bi-exclamation-octagon-fill');
  } finally {
    guardando.value = false;
  }
};

/**
 * Elimina un registro de la base de datos.
 * Captura excepciones de integridad referencial si la materia está vinculada a una reserva.
 * @param {string} clave - La llave primaria de la asignatura.
 */
const eliminarAsignatura = async (clave) => {
  if (!confirm(`¿Estás seguro de eliminar la asignatura ${clave}? Las reservas vinculadas podrían verse afectadas.`)) return;
  
  try {
    await ApiService.eliminarAsignatura(clave);
    mostrarMensaje('success', 'Asignatura eliminada de la base de datos.', 'bi-trash-fill');
    
    // Si el usuario estaba editando la misma materia que acaba de borrar, reseteamos el formulario
    if (formulario.clave_asignatura === clave) cancelarEdicion();
    await cargarDatos();
  } catch (error) {
    const status = error.response?.status;
    if (status === 403) {
      mostrarMensaje('danger', 'No tienes permisos para borrar este registro.', 'bi-shield-lock-fill');
    } else if (status === 409 || error.response?.data?.detail?.includes('Protect') || error.response?.data?.ProtectedError) {
      mostrarMensaje('warning', 'No se puede borrar porque existen reservas asignadas a esta materia.', 'bi-exclamation-triangle-fill');
    } else {
      mostrarMensaje('danger', 'Error interno del servidor.', 'bi-bug-fill');
    }
  }
};

/**
 * Transfiere los datos de la fila seleccionada en la tabla hacia el formulario lateral
 * y bloquea la edición de la llave primaria.
 * @param {Object} asignatura - El objeto del registro seleccionado.
 */
const prepararEdicion = (asignatura) => {
  modoEdicion.value = true;
  claveOriginal.value = asignatura.clave_asignatura; 
  formulario.clave_asignatura = asignatura.clave_asignatura;
  formulario.nombre_asignatura = asignatura.nombre_asignatura;
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const cancelarEdicion = () => {
  modoEdicion.value = false;
  claveOriginal.value = null;
  formulario.clave_asignatura = '';
  formulario.nombre_asignatura = '';
};

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
            <h6 class="mb-0 fw-bold text-dark"><i class="bi bi-journal-bookmark-fill me-2 text-primary-custom"></i>Catálogo de Asignaturas</h6>
            <button class="btn btn-sm btn-outline-secondary shadow-sm fw-semibold" @click="cargarDatos" :disabled="cargandoTabla">
              <i class="bi bi-arrow-clockwise" :class="{'spin-icon': cargandoTabla}"></i> Sincronizar
            </button>
          </div>
          
          <div class="card-body p-0">
            
            <div v-if="cargandoTabla" class="text-center py-5 text-muted">
              <div class="spinner-border text-primary-custom mb-2" role="status"></div>
              <p class="small fw-semibold">Cargando materias...</p>
            </div>

            <div v-else-if="asignaturas.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-journal-x display-4 opacity-25 mb-3 d-block"></i>
              <h6 class="fw-bold text-dark">Padrón de asignaturas vacío</h6>
              <p class="small mb-0">Registra la primera materia utilizando el formulario lateral.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="custom-table-header">
                  <tr>
                    <th class="ps-4" style="width: 15%;">Clave</th>
                    <th>Nombre de la Asignatura</th>
                    <th class="text-end pe-4">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="asignatura in asignaturas" :key="asignatura.clave_asignatura" class="border-bottom border-light-subtle">
                    <td class="ps-4 text-muted font-monospace small">{{ asignatura.clave_asignatura }}</td>
                    <td class="fw-bold text-dark">{{ asignatura.nombre_asignatura }}</td>
                    <td class="text-end pe-4">
                      <div class="btn-group gap-2">
                        <button 
                          @click="prepararEdicion(asignatura)" 
                          class="btn btn-sm btn-outline-primary border-0"
                          title="Editar Asignatura"
                        >
                          <i class="bi bi-pencil-square fs-6"></i>
                        </button>
                        <button 
                          @click="eliminarAsignatura(asignatura.clave_asignatura)" 
                          class="btn btn-sm btn-outline-danger border-0"
                          title="Eliminar Asignatura"
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
              {{ modoEdicion ? 'Editar Asignatura' : 'Nueva Asignatura' }}
            </h6>
            
            <hr class="text-muted opacity-25 mb-4">

            <form @submit.prevent="guardarAsignatura">
              
              <div class="mb-3">
                <label class="form-label fw-bold small text-dark-emphasis">Clave de la Asignatura</label>
                <div class="input-group">
                  <span class="input-group-text bg-white text-muted"><i class="bi bi-hash"></i></span>
                  <input 
                    type="text" 
                    class="form-control font-monospace" 
                    :class="modoEdicion ? 'bg-secondary-subtle text-muted' : 'bg-light'"
                    v-model="formulario.clave_asignatura" 
                    required
                    :disabled="modoEdicion"
                    placeholder="Ej. F001"
                  >
                </div>
                <div v-if="modoEdicion" class="form-text small text-warning mt-1 fw-semibold">
                  <i class="bi bi-lock-fill"></i> La clave no se puede modificar una vez creada.
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label fw-bold small text-dark-emphasis">Nombre Oficial</label>
                <input 
                  type="text" 
                  class="form-control bg-light border-light-subtle" 
                  v-model="formulario.nombre_asignatura" 
                  required
                  placeholder="Ej. Programación Orientada a Objetos"
                >
              </div>

              <div class="d-grid gap-2 mt-4">
                <button type="submit" class="btn fw-bold shadow-sm" :class="modoEdicion ? 'btn-warning text-dark' : 'btn-primary-custom text-white'" :disabled="guardando">
                  <span v-if="guardando" class="spinner-border spinner-border-sm me-2"></span>
                  {{ guardando ? 'Guardando...' : (modoEdicion ? 'Actualizar Nombre' : 'Registrar Asignatura') }}
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

/* Estandarización de Colores UJAT */
.text-primary-custom { color: #005f86 !important; }
.btn-primary-custom { background-color: #005f86; border-color: #005f86; }
.btn-primary-custom:hover { background-color: #004a69; border-color: #004a69; }
.btn-outline-primary { color: #005f86; border-color: #005f86; }
.btn-outline-primary:hover { background-color: #005f86; color: white; }
.border-primary-custom { border-color: #005f86 !important; }

/* Estilos de Tabla */
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

/* Animación de Sincronización */
@keyframes spin { 100% { transform: rotate(360deg); } }
.spin-icon { animation: spin 1s linear infinite; display: inline-block; }
</style>