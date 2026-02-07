<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const nombreUsuario = ref('Bienvenido');

onMounted(() => {
   
    const nombre = localStorage.getItem('nombre_usuario') || localStorage.getItem('user'); 
    if (nombre) nombreUsuario.value = `Hola, ${nombre}`;
});

const irA = (ruta) => {
    router.push(ruta);
};
</script>

<template>
  <div class="container-fluid p-4">
    
    <div class="p-5 mb-4 bg-light rounded-3 shadow-sm border">
      <div class="container-fluid py-3">
        <h1 class="display-5 fw-bold text-primary">Sistema de Gestión de Salas</h1>
        <p class="col-md-8 fs-4 text-muted">
            Administra, consulta y reserva espacios académicos de manera eficiente y ordenada.
        </p>
        <hr class="my-4">
        <p class="text-secondary">Selecciona una acción rápida para comenzar:</p>
      </div>
    </div>

    <div class="row align-items-md-stretch">
      
      <div class="col-md-4 mb-3">
        <div class="card h-100 shadow-sm border-0 hover-card" @click="irA('/reservar')" style="cursor: pointer;">
          <div class="card-body text-center p-5">
            <div class="mb-3 text-success">
                <i class="bi bi-calendar-plus display-1"></i>
            </div>
            <h2 class="h4 fw-bold">Nueva Reserva</h2>
            <p class="text-muted">Apartar una sala o laboratorio para una clase.</p>
            <button class="btn btn-outline-success mt-3">Ir a Reservar</button>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-3">
        <div class="card h-100 shadow-sm border-0 hover-card" @click="irA('/disponibilidad')" style="cursor: pointer;">
          <div class="card-body text-center p-5">
            <div class="mb-3 text-primary">
                <i class="bi bi-calendar-check display-1"></i>
            </div>
            <h2 class="h4 fw-bold">Ver Disponibilidad</h2>
            <p class="text-muted">Consulta la agenda y ocupación en tiempo real.</p>
            <button class="btn btn-outline-primary mt-3">Consultar Agenda</button>
          </div>
        </div>
      </div>

      <div class="col-md-4 mb-3">
        <div class="card h-100 shadow-sm border-0 hover-card" @click="irA('/reportes')" style="cursor: pointer;">
          <div class="card-body text-center p-5">
            <div class="mb-3 text-warning">
                <i class="bi bi-bar-chart-line display-1"></i>
            </div>
            <h2 class="h4 fw-bold">Historial y Reportes</h2>
            <p class="text-muted">Genera análisis de ocupación y bitácoras.</p>
            <button class="btn btn-outline-warning text-dark mt-3">Ver Estadísticas</button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>

.hover-card {
    transition: transform 0.2s, box-shadow 0.2s;
}
.hover-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
    background-color: #f8f9fa;
}
</style>