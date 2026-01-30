<script setup>

defineProps({
  sala: {
    type: Object,
    required: true
    
  }
});
</script>

<template>
  <div class="card h-100 shadow-sm border-0 room-card">
    
   
    <div class="card-header bg-white border-bottom-0 pt-3 pb-2 d-flex justify-content-between align-items-center">
      <div class="d-flex align-items-center">
        <div class="icon-box me-2 bg-light text-primary rounded-circle d-flex align-items-center justify-content-center" style="width:40px; height:40px;">
          <i class="bi bi-easel2"></i>
        </div>
        <div>
            <h5 class="card-title mb-0 fw-bold text-dark">{{ sala.nombre }}</h5>
            <small v-if="sala.capacidad" class="text-muted" style="font-size: 0.75rem;">Cap: {{ sala.capacidad }}</small>
        </div>
      </div>
      
     
      <span v-if="sala.eventos.length === 0" class="badge bg-success bg-opacity-10 text-success rounded-pill px-2">Libre</span>
      <span v-else class="badge bg-warning bg-opacity-10 text-dark rounded-pill px-2">{{ sala.eventos.length }} reservas</span>
    </div>

   
    <div class="card-body p-0 d-flex flex-column">
      
      
      <div v-if="sala.eventos.length === 0" class="flex-grow-1 d-flex flex-column align-items-center justify-content-center py-5 text-center text-success bg-light bg-opacity-25 mx-2 mb-2 rounded border border-dashed border-success border-opacity-25">
          <i class="bi bi-check-circle-fill fs-1 mb-2 opacity-75"></i>
          <span class="fw-bold">Disponible</span>
          <small class="text-muted px-3">Sin actividades programadas para hoy.</small>
      </div>

    
      <div v-else class="list-group list-group-flush flex-grow-1">
        <div 
          v-for="reserva in sala.eventos" 
          :key="reserva.id" 
          class="list-group-item border-0 py-3 px-3 event-item"
        >
          <div class="d-flex w-100 justify-content-between mb-1">
            <span class="badge bg-light text-dark border d-flex align-items-center">
              <i class="bi bi-clock me-1 text-primary"></i> 
              {{ reserva.inicio }} - {{ reserva.fin }}
            </span>
            <span class="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-10" style="font-size: 0.7rem;">
                {{ reserva.division }}
            </span>
          </div>
          
          <div class="d-flex align-items-start mt-2">
            <div class="avatar-small me-2 text-white fw-bold d-flex align-items-center justify-content-center rounded-circle" style="width:32px; height:32px; background: #005f86;">
                {{ reserva.maestro.charAt(0).toUpperCase() }}
            </div>
            <div>
                <h6 class="mb-0 fw-bold text-dark text-truncate" style="max-width: 180px;">{{ reserva.maestro }}</h6>
                <small class="text-muted fst-italic d-block text-truncate" style="max-width: 180px;">{{ reserva.asignatura || reserva.tema || 'Actividad General' }}</small>
            </div>
          </div>
        </div>
      </div>
    </div>
    
  </div>
</template>

<style scoped>

.room-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.room-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.1) !important;
}

.event-item {
  border-left: 3px solid transparent;
  transition: background-color 0.2s;
}

.event-item:hover {
  background-color: #f8f9fa;
  border-left: 3px solid #005f86;
}

.border-dashed {
    border-style: dashed !important;
}
</style>