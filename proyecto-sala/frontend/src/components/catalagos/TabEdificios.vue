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
            <h6 class="mb-0 fw-bold text-dark"><i class="bi bi-list-ul me-2 text-primary"></i>Edificios Registrados</h6>
            <button class="btn btn-sm btn-outline-secondary" @click="cargarDatos" :disabled="cargandoTabla">
              <i class="bi bi-arrow-clockwise" :class="{'spin-icon': cargandoTabla}"></i> Sincronizar
            </button>
          </div>
          
          <div class="card-body p-0">
            
            <div v-if="cargandoTabla" class="text-center py-5 text-muted">
              <div class="spinner-border text-primary mb-2" role="status"></div>
              <p class="small">Cargando infraestructura...</p>
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
        <div class="card shadow-sm border-0 border-top border-4 rounded-3 h-100 bg-white" :class="modoEdicion ? 'border-warning' : 'border-primary'">
          <div class="card-body p-4">
            
            <h6 class="fw-bold mb-3 d-flex align-items-center" :class="modoEdicion ? 'text-warning-emphasis' : 'text-primary'">
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
                <div class="form-text small mt-1">Este dato es crucial para el aislamiento de seguridad por roles.</div>
              </div>

              <div class="d-grid gap-2 mt-4">
                <button type="submit" class="btn fw-bold shadow-sm" :class="modoEdicion ? 'btn-warning text-dark' : 'btn-primary'" :disabled="guardando">
                  <span v-if="guardando" class="spinner-border spinner-border-sm me-2"></span>
                  {{ guardando ? 'Guardando...' : (modoEdicion ? 'Actualizar Cambios' : 'Registrar Edificio') }}
                </button>
                <button v-if="modoEdicion" type="button" class="btn btn-light fw-semibold text-muted border" @click="cancelarEdicion" :disabled="guardando">
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

<script setup>
import { ref, reactive, onMounted } from 'vue';
import ApiService from '@/services/ApiService.js';

// ESTADOS GLOBALES
const edificios = ref([]);
const divisiones = ref([]);
const cargandoTabla = ref(false);
const guardando = ref(false);
const modoEdicion = ref(false);
const mensaje = reactive({ tipo: '', texto: '', icono: '' });

// ESTADO DEL FORMULARIO
const formulario = reactive({
  id: null,
  nombre_edificio: '',
  division: null
});

// INICIALIZACIÓN
onMounted(() => {
  cargarDatos();
});

// FUNCIÓN 1: OBTENER DATOS (Lectura paralela para optimizar velocidad)
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

// FUNCIÓN 2: GUARDAR (Crea o Actualiza dependiendo del estado)
const guardarEdificio = async () => {
  guardando.value = true;
  ocultarMensaje();

  try {
    // Empaquetamos los datos que requiere Django
    const payload = {
      nombre_edificio: formulario.nombre_edificio,
      division: formulario.division
    };

    if (modoEdicion.value) {
      // Flujo PUT (Actualizar)
      await ApiService.actualizarEdificio(formulario.id, payload);
      mostrarMensaje('success', 'Edificio actualizado correctamente.', 'bi-check-circle-fill');
    } else {
      // Flujo POST (Crear)
      await ApiService.crearEdificio(payload);
      mostrarMensaje('success', 'Nuevo edificio registrado con éxito.', 'bi-check-circle-fill');
    }

    cancelarEdicion();
    await cargarDatos(); // Recargar tabla automáticamente
    
  } catch (error) {
    console.error("Error al guardar edificio:", error);
    const detalle = error.response?.data?.detail || error.response?.data?.nombre_edificio?.[0] || 'Revisa que los datos sean correctos.';
    mostrarMensaje('danger', `Error al guardar: ${detalle}`, 'bi-exclamation-octagon-fill');
  } finally {
    guardando.value = false;
  }
};

// FUNCIÓN 3: ELIMINAR
const eliminarEdificio = async (id) => {
  if (!confirm('ATENCIÓN: Si eliminas este edificio, las salas y reservas asociadas podrían verse afectadas. ¿Estás seguro?')) return;
  
  try {
    await ApiService.eliminarEdificio(id);
    mostrarMensaje('success', 'Edificio eliminado de la base de datos.', 'bi-trash-fill');
    
    // Si estaba editando el que acabo de borrar, limpio el formulario
    if (formulario.id === id) cancelarEdicion();
    
    await cargarDatos();
  } catch (error) {
    const status = error.response?.status;
    if (status === 403) mostrarMensaje('danger', 'No tienes permisos de superusuario para borrar este registro.', 'bi-shield-lock-fill');
    else if (status === 409 || error.response?.data?.ProtectedError) mostrarMensaje('warning', 'No se puede borrar porque existen salas asignadas a este edificio.', 'bi-exclamation-triangle-fill');
    else mostrarMensaje('danger', 'Error interno del servidor al intentar eliminar.', 'bi-bug-fill');
  }
};

// FUNCIONES DE UTILIDAD PARA LA UI
const prepararEdicion = (edificio) => {
  modoEdicion.value = true;
  formulario.id = edificio.id;
  formulario.nombre_edificio = edificio.nombre_edificio;
  
  // Extraemos el ID de la división sin importar cómo venga de Django (Objeto o Int)
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

const mostrarMensaje = (tipo, texto, icono) => {
  mensaje.tipo = tipo;
  mensaje.texto = texto;
  mensaje.icono = icono;
  setTimeout(() => ocultarMensaje(), 5000); // Autocultar a los 5 segundos
};

const ocultarMensaje = () => {
  mensaje.texto = '';
};

// Función para traducir el ID de la división al nombre real para la tabla
const obtenerNombreDivision = (divisionIdObj) => {
  if (!divisionIdObj) return 'Sin Asignar';
  
  const divId = typeof divisionIdObj === 'object' ? (divisionIdObj.id || divisionIdObj.clave_division) : divisionIdObj;
  const div = divisiones.value.find(d => String(d.id || d.clave_division) === String(divId));
  
  return div ? (div.nombre_division || div.nombre || div.clave_division) : 'División Desconocida';
};
</script>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

/* Estilos Institucionales */
.text-primary { color: #005f86 !important; }
.btn-primary { background-color: #005f86; border-color: #005f86; }
.btn-primary:hover { background-color: #004a69; border-color: #004a69; }
.border-primary { border-color: #005f86 !important; }

/* Estilos de tabla herencia de ReportesView */
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