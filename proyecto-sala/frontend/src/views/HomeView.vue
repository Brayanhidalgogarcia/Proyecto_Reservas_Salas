<script setup>
// Importamos las herramientas de Vue y nuestro servicio de API
import { ref, onMounted } from 'vue';
import ApiService from '@/services/ApiService.js';

// Creamos variables "reactivas". Cuando su valor cambie, la vista se actualizará sola.
const salas = ref([]);
const cargando = ref(true);
const error = ref(null);

// onMounted es una función que se ejecuta automáticamente cuando el componente está listo
onMounted(async () => {
  try {
    // Llamamos a nuestro servicio para obtener los datos del backend
    const response = await ApiService.obtenerSalas();
    salas.value = response.data; // Guardamos la lista de salas en nuestra variable
  } catch (err) {
    error.value = 'No se pudieron cargar las salas.';
    console.error(err);
  } finally {
    cargando.value = false; // Dejamos de mostrar el mensaje "Cargando..."
  }
});
</script>

<template>
  <main>
    <h1>Salas Audiovisuales</h1>
    <div v-if="cargando">Cargando lista de salas...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <ul v-if="salas.length">
      <!-- Usamos v-for para crear un elemento <li> por cada sala en nuestra lista -->
      <li v-for="sala in salas" :key="sala.clave_sala">
        <h2>{{ sala.nombre_sala }}</h2>
        <p>Clave: {{ sala.clave_sala }}</p>
        <p>División: {{ sala.division }}</p>
      </li>
    </ul>
    <div v-else-if="!cargando">
      No hay salas para mostrar.
    </div>
  </main>
</template>

<style scoped>
main {
  padding: 1rem;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}
.error {
  color: red;
}
</style>
