<script setup>
import { ref, onMounted } from 'vue';
import ApiService from '@/services/ApiService.js';

const nuevaReserva = ref({
  maestro: null,
  asignatura: null,
  sala: null,
  tema: '',
  inicio: '',
  fin: ''     
});
const reservasExistentes = ref([]);
const cargando = ref(false);
const error = ref(null);
const mensajeExito = ref(null);

const maestros = ref([]);
const asignaturas = ref([]);
const salas = ref([]);

async function cargarDatosIniciales() {
  cargando.value = true;
  error.value = null;
  try {
    const [resReservas, resMaestros, resAsignaturas, resSalas] = await Promise.all([
      ApiService.obtenerReservas(),
      ApiService.obtenerMaestros(),
      ApiService.obtenerAsignaturas(),
      ApiService.obtenerSalas()
    ]);
    reservasExistentes.value = resReservas.data;
    maestros.value = resMaestros.data;
    asignaturas.value = resAsignaturas.data;
    salas.value = resSalas.data;
  } catch (err) {
    error.value = 'Error al cargar datos iniciales. ' + (err.response?.data?.detail || err.message);
    console.error(err);
  } finally {
    cargando.value = false;
  }
}

async function agregarReserva() {
  cargando.value = true;
  error.value = null;
  mensajeExito.value = null;

  const datosParaAPI = {
    maestro: nuevaReserva.value.maestro,
    asignatura: nuevaReserva.value.asignatura,
    sala: nuevaReserva.value.sala,
    tema: nuevaReserva.value.tema,
    inicio: nuevaReserva.value.inicio,
    fin: nuevaReserva.value.fin
  };

  try {
    await ApiService.crearReserva(datosParaAPI);
    mensajeExito.value = '¡Reserva creada con éxito!';
    
    nuevaReserva.value = { maestro: null, asignatura: null, sala: null, tema: '', inicio: '', fin: '' };
    
    await cargarDatosIniciales(); 

  } catch (err) {
    error.value = 'Error al crear la reserva. ' + (err.response?.data?.detail || JSON.stringify(err.response?.data) || err.message);
    console.error(err);
  } finally {
    cargando.value = false;
  }
}


onMounted(cargarDatosIniciales);

</script>

<template>
  <div class="container"> 
    <div class="form-section">
      <h3>Apartar Sala Audiovisual</h3>
      
      <div v-if="cargando" class="alert alert-info">Procesando...</div>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="mensajeExito" class="alert alert-success">{{ mensajeExito }}</div>

      <form @submit.prevent="agregarReserva">
        <div class="row mb-3">
          <div class="col-md-6">
            <label for="maestroSelect" class="form-label">Maestro</label>
            <select id="maestroSelect" class="form-select" v-model="nuevaReserva.maestro" required>
              <option disabled :value="null">Selecciona un maestro</option>
              <option v-for="m in maestros" :key="m.matricula_m" :value="m.matricula_m">
                {{ m.nombre }} {{ m.apellido_p }} ({{ m.matricula_m }})
              </option>
            </select>
          </div>
          <div class="col-md-6">
            <label for="asignaturaSelect" class="form-label">Asignatura</label>
            <select id="asignaturaSelect" class="form-select" v-model="nuevaReserva.asignatura" required>
              <option disabled :value="null">Selecciona una asignatura</option>
              <option v-for="a in asignaturas" :key="a.clave_asignatura" :value="a.clave_asignatura">
                {{ a.nombre_asignatura }}
              </option>
            </select>
          </div>
        </div>

        <div class="row mb-3">
          <div class="col-md-6">
            <label for="salaSelect" class="form-label">Sala</label>
            <select id="salaSelect" class="form-select" v-model="nuevaReserva.sala" required>
              <option disabled :value="null">Selecciona una sala</option>
              <option v-for="s in salas" :key="s.clave_sala" :value="s.clave_sala">
                {{ s.nombre_sala }} ({{ s.clave_sala }})
              </option>
            </select>
          </div>
           <div class="col-md-6">
             <label for="temaInput" class="form-label">Tema (Opcional)</label>
             <input id="temaInput" type="text" class="form-control" v-model="nuevaReserva.tema">
           </div>
        </div>

        <div class="row mb-3">
          <div class="col-md-6">
            <label for="inicioInput" class="form-label">Inicio</label>
            <input id="inicioInput" type="datetime-local" class="form-control" v-model="nuevaReserva.inicio" required>
          </div>
          <div class="col-md-6">
            <label for="finInput" class="form-label">Fin</label>
            <input id="finInput" type="datetime-local" class="form-control" v-model="nuevaReserva.fin" required>
          </div>
        </div>

        <button type="submit" class="btn btn-success" :disabled="cargando">
          {{ cargando ? 'Agregando...' : 'Agregar Reserva' }}
        </button>
      </form>
    </div>

    <h4 class="mt-4">Reservas existentes</h4>
    <table class="table table-bordered mt-2">
      <thead class="table-light">
        <tr>
          <th>Maestro</th><th>Asignatura</th><th>Sala</th><th>Inicio</th><th>Fin</th><th>Tema</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="reservasExistentes.length === 0 && !cargando">
          <td colspan="6" class="text-center">No hay reservas existentes.</td>
        </tr>
        <tr v-else v-for="reserva in reservasExistentes" :key="reserva.id">
          <td>{{ reserva.maestro }}</td>
          <td>{{ reserva.asignatura }}</td>
          <td>{{ reserva.sala }}</td>
          <td>{{ reserva.inicio ? new Date(reserva.inicio).toLocaleString('es-MX') : 'N/A' }}</td>
          <td>{{ reserva.fin ? new Date(reserva.fin).toLocaleString('es-MX') : 'N/A' }}</td>
          <td>{{ reserva.tema || 'N/A' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
  .form-section {
    background: #ffffff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
  }
  h3, h4 {
    margin-bottom: 20px;
  }
  table {
    background: #ffffff;
  }
 
  .alert { margin-top: 1rem; }
</style>
