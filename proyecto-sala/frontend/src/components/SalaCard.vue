<script setup>
const props = defineProps({
  sala: {
    type: Object,
    required: true
  },
  // Recibimos el rol del usuario desde el componente Padre
  isSuperUser: {
    type: Boolean,
    default: false
  }
});

// CORRECCIÓN: Motor de estado en tiempo real con validación de calendario
const obtenerEstadoReserva = (fechaReserva, inicioFmt, finFmt) => {
  const ahora = new Date();
  
  // 1. Construimos la fecha de "hoy" en formato YYYY-MM-DD para comparar de forma segura
  const anioActual = ahora.getFullYear();
  const mesActual = String(ahora.getMonth() + 1).padStart(2, '0');
  const diaActual = String(ahora.getDate()).padStart(2, '0');
  const strHoy = `${anioActual}-${mesActual}-${diaActual}`;

  // 2. Validación de Calendario (Previene el "viaje en el tiempo")
  if (fechaReserva < strHoy) {
    return { texto: 'Finalizada', clase: 'bg-secondary bg-opacity-10 text-secondary border-secondary' };
  }
  if (fechaReserva > strHoy) {
    return { texto: 'Próxima', clase: 'bg-warning bg-opacity-10 text-warning border-warning' };
  }

  // 3. Validación de Reloj (Solo llega aquí si la reserva es exactamente HOY)
  const horaActual = ahora.getHours();
  const minActual = ahora.getMinutes();
  const tiempoActual = horaActual * 60 + minActual;

  const [hIni, mIni] = inicioFmt.split(':').map(Number);
  const [hFin, mFin] = finFmt.split(':').map(Number);

  const tiempoIni = hIni * 60 + mIni;
  const tiempoFin = hFin * 60 + mFin;

  if (tiempoActual >= tiempoIni && tiempoActual < tiempoFin) {
    return { texto: 'En curso', clase: 'bg-success bg-opacity-10 text-success border-success' };
  } else if (tiempoActual < tiempoIni) {
    return { texto: 'Próxima', clase: 'bg-warning bg-opacity-10 text-warning border-warning' };
  } else {
    return { texto: 'Finalizada', clase: 'bg-secondary bg-opacity-10 text-secondary border-secondary' };
  }
};
</script>

<template>
  <div class="card h-100 shadow-sm border-0 room-card">
    
    <div class="card-header bg-white border-bottom-0 pt-3 pb-2 d-flex justify-content-between align-items-start">
      <div class="d-flex align-items-center">
        <div class="icon-box me-3 bg-light text-primary rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" style="width:40px; height:40px;">
          <i class="bi bi-easel2"></i>
        </div>
        <div>
            <h5 class="card-title mb-0 fw-bold text-dark">{{ sala.nombre }}</h5>
            
            <div class="d-flex flex-wrap align-items-center gap-2 mt-1">
                <small class="text-muted" style="font-size: 0.75rem;">
                    <i class="bi bi-geo-alt-fill text-secondary me-1"></i>{{ sala.edificio }}
                </small>
                <small v-if="sala.capacidad" class="text-muted border-start ps-2" style="font-size: 0.75rem;">Cap: {{ sala.capacidad }}</small>
            </div>
        </div>
      </div>
      
      <span v-if="sala.eventos.length === 0" class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 mt-1">Libre</span>
      <span v-else class="badge bg-warning bg-opacity-10 text-dark rounded-pill px-2 mt-1">{{ sala.eventos.length }} reservas</span>
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
          <div class="d-flex w-100 justify-content-between mb-2">
            <span class="badge bg-light text-dark border d-flex align-items-center">
              <i class="bi bi-clock me-1 text-primary"></i> 
              {{ reserva.inicio }} - {{ reserva.fin }}
            </span>
            
            <div class="d-flex gap-1 align-items-center">
                <span class="badge border border-opacity-25" :class="obtenerEstadoReserva(reserva.fecha, reserva.inicio, reserva.fin).clase" style="font-size: 0.65rem;">
                    {{ obtenerEstadoReserva(reserva.fecha, reserva.inicio, reserva.fin).texto }}
                </span>
                <span class="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-10" style="font-size: 0.65rem;">
                    {{ reserva.division }}
                </span>
            </div>
          </div>
          
          <div class="d-flex align-items-start mt-2 overflow-hidden">
            <div class="avatar-small me-2 text-white fw-bold d-flex align-items-center justify-content-center rounded-circle flex-shrink-0" style="width:32px; height:32px; background: #005f86;">
                {{ reserva.maestro.charAt(0).toUpperCase() }}
            </div>
            
            <div class="w-100 overflow-hidden">
                <h6 class="mb-0 fw-bold text-dark text-truncate">{{ reserva.maestro }}</h6>
                
                <div class="d-flex align-items-center mt-1 text-truncate">
                    <span class="badge bg-secondary me-2 py-1" style="font-size: 0.60rem;">{{ reserva.actividad }}</span>
                    <small class="text-muted fst-italic text-truncate d-inline-block w-100" style="font-size: 0.80rem;">
                        {{ reserva.detalleActividad }}
                    </small>
                </div>

                <div v-if="isSuperUser && reserva.requerimientos" class="mt-2 p-2 rounded bg-warning bg-opacity-10 border border-warning border-opacity-25">
                    <small class="d-block fw-bold text-dark-emphasis mb-1" style="font-size: 0.70rem;">
                        <i class="bi bi-tools me-1"></i>Requerimientos:
                    </small>
                    <small class="d-block text-dark lh-sm" style="font-size: 0.75rem;">
                        {{ reserva.requerimientos }}
                    </small>
                </div>
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