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
            <h6 class="mb-0 fw-bold text-dark"><i class="bi bi-door-open-fill me-2 text-primary"></i>Catálogo de Salas y Espacios</h6>
            <button class="btn btn-sm btn-outline-secondary" @click="cargarDatos" :disabled="cargandoTabla">
              <i class="bi bi-arrow-clockwise" :class="{'spin-icon': cargandoTabla}"></i> Sincronizar
            </button>
          </div>
          
          <div class="card-body p-0">
            
            <div v-if="cargandoTabla" class="text-center py-5 text-muted">
              <div class="spinner-border text-primary mb-2" role="status"></div>
              <p class="small">Cargando espacios...</p>
            </div>

            <div v-else-if="salas.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-door-closed display-4 opacity-25 mb-3 d-block"></i>
              <h6 class="fw-bold text-dark">No hay salas registradas</h6>
              <p class="small mb-0">Agrega el primer espacio físico utilizando el panel lateral.</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="custom-table-header">
                  <tr>
                    <th class="ps-4">Clave</th>
                    <th>Nombre / Identificador</th>
                    <th>Edificio Asignado</th>
                    <th class="text-end pe-4">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="sala in salas" :key="sala.clave_sala" class="border-bottom border-light-subtle">
                    <td class="ps-4 text-muted font-monospace small">{{ sala.clave_sala }}</td>
                    <td class="fw-bold text-dark">{{ sala.nombre_sala || sala.nombre }}</td>
                    <td class="text-muted small">
                      <span class="badge bg-light text-secondary border">
                        <i class="bi bi-building me-1"></i> {{ obtenerNombreEdificio(sala.edificio) }}
                      </span>
                    </td>
                    <td class="text-end pe-4">
                      <div class="btn-group gap-2">
                        <button 
                          @click="prepararEdicion(sala)" 
                          class="btn btn-sm btn-outline-primary border-0"
                          title="Editar Sala"
                        >
                          <i class="bi bi-pencil-square fs-6"></i>
                        </button>
                        <button 
                          @click="eliminarSala(sala.clave_sala)" 
                          class="btn btn-sm btn-outline-danger border-0"
                          title="Eliminar Sala"
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
              {{ modoEdicion ? 'Configurar Espacio' : 'Nueva Sala' }}
            </h6>
            
            <hr class="text-muted opacity-25 mb-4">

            <form @submit.prevent="guardarSala">
              
              <div class="mb-3">
                <label class="form-label fw-bold small text-dark-emphasis">Clave Única de la Sala</label>
                <div class="input-group">
                  <span class="input-group-text bg-white text-muted"><i class="bi bi-hash"></i></span>
                  <input 
                    type="text" 
                    class="form-control font-monospace" 
                    :class="modoEdicion ? 'bg-secondary-subtle text-muted' : 'bg-light'"
                    v-model="formulario.clave_sala" 
                    required
                    :disabled="modoEdicion"
                    placeholder="Ej. S-101"
                  >
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold small text-dark-emphasis">Nombre o Descripción</label>
                <input 
                  type="text" 
                  class="form-control bg-light border-light-subtle" 
                  v-model="formulario.nombre_sala" 
                  required
                  placeholder="Ej. Sala Audiovisual 1"
                >
              </div>

              <div class="mb-4">
                <label class="form-label fw-bold small text-dark-emphasis">Edificio de Ubicación</label>
                <select class="form-select bg-light border-light-subtle" v-model="formulario.edificio" required>
                  <option :value="null">Seleccionar Edificio...</option>
                  <option v-for="ed in edificios" :key="ed.nombre_edificio" :value="ed.nombre_edificio">
                      {{ ed.nombre_edificio }}
                  </option>
                </select>
                <div v-if="edificios.length === 0" class="form-text small text-danger mt-1">
                  <i class="bi bi-exclamation-circle"></i> Debes registrar un edificio primero.
                </div>
              </div>

              <div class="d-grid gap-2 mt-4">
                <button type="submit" class="btn fw-bold shadow-sm" :class="modoEdicion ? 'btn-warning text-dark' : 'btn-primary'" :disabled="guardando || edificios.length === 0">
                  <span v-if="guardando" class="spinner-border spinner-border-sm me-2"></span>
                  {{ guardando ? 'Guardando...' : (modoEdicion ? 'Actualizar Sala' : 'Registrar Espacio') }}
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

const salas = ref([]);
const edificios = ref([]);
const cargandoTabla = ref(false);
const guardando = ref(false);
const modoEdicion = ref(false);
const claveOriginal = ref(null); 
const mensaje = reactive({ tipo: '', texto: '', icono: '' });

const formulario = reactive({
  clave_sala: '',
  nombre_sala: '',
  edificio: null
});

onMounted(() => {
  cargarDatos();
});

const cargarDatos = async () => {
  cargandoTabla.value = true;
  try {
    // Traemos las salas y los edificios en paralelo
    const [resSalas, resEdificios] = await Promise.all([
      ApiService.obtenerSalas(),
      ApiService.obtenerEdificios()
    ]);
    
    salas.value = resSalas.data || resSalas;
    edificios.value = resEdificios.data || resEdificios;
  } catch (error) {
    console.error("Error al cargar datos:", error);
    mostrarMensaje('danger', 'Error de conexión. Verifica la consola.', 'bi-wifi-off');
  } finally {
    cargandoTabla.value = false;
  }
};

const guardarSala = async () => {
  guardando.value = true;
  ocultarMensaje();

  try {
    const payload = {
      clave_sala: formulario.clave_sala,
      nombre_sala: formulario.nombre_sala,
      edificio: formulario.edificio
    };

    if (modoEdicion.value) {
      await ApiService.actualizarSala(claveOriginal.value, payload);
      mostrarMensaje('success', 'Configuración de la sala actualizada.', 'bi-check-circle-fill');
    } else {
      await ApiService.crearSala(payload);
      mostrarMensaje('success', 'Nuevo espacio habilitado correctamente.', 'bi-check-circle-fill');
    }

    cancelarEdicion();
    await cargarDatos();
    
  } catch (error) {
    console.error("Error al guardar sala:", error);
    const detalle = error.response?.data?.detail || error.response?.data?.clave_sala?.[0] || 'Error de validación. Revisa la clave o el edificio.';
    mostrarMensaje('danger', `Error al procesar: ${detalle}`, 'bi-exclamation-octagon-fill');
  } finally {
    guardando.value = false;
  }
};

const eliminarSala = async (clave) => {
  if (!confirm(`¿Estás seguro de eliminar la sala ${clave}? Esto borrará o dejará huérfanas sus reservas.`)) return;
  
  try {
    await ApiService.eliminarSala(clave);
    mostrarMensaje('success', 'Sala retirada del sistema.', 'bi-trash-fill');
    
    if (formulario.clave_sala === clave) cancelarEdicion();
    await cargarDatos();
  } catch (error) {
    const status = error.response?.status;
    if (status === 403) mostrarMensaje('danger', 'Privilegios insuficientes.', 'bi-shield-lock-fill');
    else if (status === 409 || error.response?.data?.ProtectedError) mostrarMensaje('warning', 'La sala tiene reservas vigentes. Imposible eliminar.', 'bi-exclamation-triangle-fill');
    else mostrarMensaje('danger', 'Error interno del servidor.', 'bi-bug-fill');
  }
};

const prepararEdicion = (sala) => {
  modoEdicion.value = true;
  claveOriginal.value = sala.clave_sala; 
  formulario.clave_sala = sala.clave_sala;
  formulario.nombre_sala = sala.nombre_sala || sala.nombre;
  
  // Extraer el ID del edificio asegurando compatibilidad con el serializador de Django
  formulario.edificio = (sala.edificio && typeof sala.edificio === 'object') 
                        ? sala.edificio.id 
                        : sala.edificio;
                        
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const cancelarEdicion = () => {
  modoEdicion.value = false;
  claveOriginal.value = null;
  formulario.clave_sala = '';
  formulario.nombre_sala = '';
  formulario.edificio = null;
};

const mostrarMensaje = (tipo, texto, icono) => {
  mensaje.tipo = tipo;
  mensaje.texto = texto;
  mensaje.icono = icono;
  setTimeout(() => ocultarMensaje(), 5000);
};

const ocultarMensaje = () => { mensaje.texto = ''; };

const obtenerNombreEdificio = (edificioIdObj) => {
  if (!edificioIdObj) return 'Desconocido';
  // Soporta la llave natural en lugar del ID genérico
  const edId = typeof edificioIdObj === 'object' ? edificioIdObj.nombre_edificio : edificioIdObj;
  const ed = edificios.value.find(e => String(e.nombre_edificio) === String(edId));
  return ed ? ed.nombre_edificio : 'Edificio no encontrado';
};
</script>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

.text-primary { color: #005f86 !important; }
.btn-primary { background-color: #005f86; border-color: #005f86; }
.btn-primary:hover { background-color: #004a69; border-color: #004a69; }
.border-primary { border-color: #005f86 !important; }

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

@keyframes spin { 100% { transform: rotate(360deg); } }
.spin-icon { animation: spin 1s linear infinite; display: inline-block; }
</style>