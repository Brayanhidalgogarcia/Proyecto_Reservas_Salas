<script setup>
import { ref, onMounted } from 'vue';
import ApiService from '@/services/ApiService.js';


const reservas = ref([]);
const cargando = ref(true);
const error = ref(null);


onMounted(async () => {
  try {
   
    const response = await ApiService.obtenerReservas();
    reservas.value = response.data;
  } catch (err) {
    error.value = 'No se pudieron cargar las reservas.';
    console.error(err);
  } finally {
    cargando.value = false;
  }
});


function formatDateTime(dateTimeString) {
  if (!dateTimeString) return 'N/A';
  try {
    const dt = new Date(dateTimeString);
    return dt.toLocaleDateString('es-MX') + ' ' + dt.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    return 'Fecha inválida';
  }
}
</script>

<template>
 
  <div id="disponibilidad-view">
    <h3>Consultar Disponibilidad</h3>

   
    <div v-if="cargando" class="alert alert-info mt-3">Cargando información...</div>
    <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>

   
    <table v-if="!cargando && !error" class="table table-bordered mt-3">
      <thead>
        <tr>
          <th>Nombre del maestro</th>
          <th>Fecha de Apartado</th>
          <th>Sala Apartada</th>
          <th>Horario de Inicio</th>
          <th>Horario de Finalización</th>
          <th>División</th>
        </tr>
      </thead>
      <tbody>
      
        <tr v-if="reservas.length === 0">
          <td colspan="6" class="text-center">No hay reservas registradas.</td>
        </tr>

      
        <tr v-else v-for="(reserva, index) in reservas" :key="reserva.id || index">
          <td>{{ reserva.maestro }}</td>
          <td>{{ formatDateTime(reserva.fecha_apartado) }}</td>
          <td>{{ reserva.sala }}</td>
          <td>{{ formatDateTime(reserva.inicio) }}</td>
          <td>{{ formatDateTime(reserva.fin) }}</td>
          
          <td>{{ reserva.division || 'N/A' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
  
  #disponibilidad-view { 
    padding: 20px; 
    background-color: #f8f9fa; 
    border-radius: 8px;
  }
  
 
  table {
    background-color: #ffffff;
  }
  
   .error {
    color: #721c24;
  }
</style>