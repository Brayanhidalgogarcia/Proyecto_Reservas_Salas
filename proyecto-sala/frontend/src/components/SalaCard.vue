<script setup>
/**
 * @file SalaCard.vue
 * @description Componente visual tipo tarjeta que representa un espacio físico (Sala o Laboratorio).
 * Muestra la infraestructura disponible y el listado cronológico de las reservas.
 * Incluye un motor de evaluación de tiempo real para indicar el estado de cada evento.
 */

// ==========================================
// 1. PROPIEDADES (PROPS)
// ==========================================
defineProps({
  /**
   * Objeto con toda la información estructural de la sala y su arreglo de eventos.
   * @type {Object}
   */
  sala: {
    type: Object,
    required: true
  },
  /**
   * Bandera inyectada desde la vista padre para revelar datos sensibles (ej. requerimientos).
   * @type {Boolean}
   */
  isSuperUser: {
    type: Boolean,
    default: false
  }
});

// ==========================================
// 2. FUNCIONES Y MÉTODOS
// ==========================================

/**
 * Motor de estado en tiempo real con validación de calendario local.
 * Cruza la hora y fecha del dispositivo con el horario de la reserva
 * para devolver el estado actual y sus clases CSS correspondientes.
 * * @param {string} fechaReserva - Formato 'YYYY-MM-DD'
 * @param {string} inicioFmt - Hora de inicio 'HH:MM'
 * @param {string} finFmt - Hora de fin 'HH:MM'
 * @returns {Object} { texto: string, clase: string }
 */
const obtenerEstadoReserva = (fechaReserva, inicioFmt, finFmt) => {
  const ahora = new Date();
  
  // 1. Construcción segura de "hoy" (Zona Horaria Local)
  const anioActual = ahora.getFullYear();
  const mesActual = String(ahora.getMonth() + 1).padStart(2, '0');
  const diaActual = String(ahora.getDate()).padStart(2, '0');
  const strHoy = `${anioActual}-${mesActual}-${diaActual}`;

  // 2. Validación a Nivel Calendario
  if (fechaReserva < strHoy) {
    return { texto: 'Finalizada', clase: 'bg-secondary bg-opacity-10 text-secondary border-secondary' };
  }
  if (fechaReserva > strHoy) {
    return { texto: 'Próxima', clase: 'bg-warning bg-opacity-10 text-warning-emphasis border-warning' };
  }

  // 3. Validación a Nivel Reloj (Solo si el evento es HOY)
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
    return { texto: 'Próxima', clase: 'bg-warning bg-opacity-10 text-warning-emphasis border-warning' };
  } else {
    return { texto: 'Finalizada', clase: 'bg-secondary bg-opacity-10 text-secondary border-secondary' };
  }
};
</script>

<template>
  <div class="card h-100 shadow-sm border-0 room-card rounded-3">
    
    <div class="card-header bg-white border-bottom-0 pt-4 pb-2 d-flex justify-content-between align-items-start">
      <div class="d-flex align-items-center">
        <div class="icon-box-lg me-3 bg-light text-primary-custom rounded-circle d-flex align-items-center justify-content-center flex-shrink-0">
          <i class="bi bi-easel2 fs-5"></i>
        </div>
        <div>
            <h5 class="card-title mb-0 fw-bold text-dark">{{ sala.nombre }}</h5>
            
            <div class="d-flex flex-wrap align-items-center gap-2 mt-1">
                <small class="text-muted detalle-sala">
                    <i class="bi bi-geo-alt-fill text-secondary me-1"></i>{{ sala.edificio }}
                </small>
                <small v-if="sala.capacidad" class="text-muted border-start ps-2 detalle-sala">
                    Capacidad: {{ sala.capacidad }}
                </small>
            </div>
        </div>
      </div>
      
      <span v-if="sala.eventos.length === 0" class="badge bg-success bg-opacity-10 text-success rounded-pill px-3 py-2 mt-1 border border-success border-opacity-25 shadow-sm">Libre</span>
      <span v-else class="badge bg-warning bg-opacity-10 text-dark-emphasis rounded-pill px-3 py-2 mt-1 border border-warning border-opacity-25 shadow-sm">{{ sala.eventos.length }} reservas</span>
    </div>

    <div class="card-body p-0 d-flex flex-column">
      
      <div v-if="sala.eventos.length === 0" class="flex-grow-1 d-flex flex-column align-items-center justify-content-center py-5 text-center text-success bg-light bg-opacity-25 mx-3 mb-3 mt-2 rounded border border-dashed border-success border-opacity-25">
          <i class="bi bi-check-circle-fill fs-1 mb-2 opacity-50"></i>
          <span class="fw-bold">Sala Disponible</span>
          <small class="text-muted px-3 mt-1">Sin actividades académicas programadas para el día de hoy.</small>
      </div>

      <div v-else class="list-group list-group-flush flex-grow-1 mx-2 mb-2">
        <div 
          v-for="reserva in sala.eventos" 
          :key="reserva.id" 
          class="list-group-item border-0 py-3 px-3 event-item rounded-3 mb-1"
        >
          <div class="d-flex w-100 justify-content-between mb-2">
            <span class="badge bg-light text-dark border d-flex align-items-center shadow-sm">
              <i class="bi bi-clock me-1 text-primary-custom"></i> 
              {{ reserva.inicio }} - {{ reserva.fin }}
            </span>
            
            <div class="d-flex gap-1 align-items-center">
                <span class="badge border border-opacity-25 font-micro" :class="obtenerEstadoReserva(reserva.fecha, reserva.inicio, reserva.fin).clase">
                    {{ obtenerEstadoReserva(reserva.fecha, reserva.inicio, reserva.fin).texto }}
                </span>
                <span class="badge bg-primary bg-opacity-10 text-primary-custom border border-primary border-opacity-10 font-micro">
                    {{ reserva.division }}
                </span>
            </div>
          </div>
          
          <div class="d-flex align-items-start mt-3 overflow-hidden">
            
            <div class="avatar-maestro me-3 text-white fw-bold d-flex align-items-center justify-content-center rounded-circle flex-shrink-0 shadow-sm">
                {{ reserva.maestro.charAt(0).toUpperCase() }}
            </div>
            
            <div class="w-100 overflow-hidden">
                <h6 class="mb-0 fw-bold text-dark text-truncate">{{ reserva.maestro }}</h6>
                
                <div class="d-flex align-items-center mt-1 text-truncate">
                    <span class="badge bg-secondary me-2 py-1 font-nano">{{ reserva.actividad }}</span>
                    <small class="text-muted fst-italic text-truncate d-inline-block w-100 detalle-actividad">
                        {{ reserva.detalleActividad }}
                    </small>
                </div>

                <div v-if="isSuperUser && reserva.requerimientos" class="mt-3 p-2 rounded bg-warning bg-opacity-10 border border-warning border-opacity-25">
                    <small class="d-block fw-bold text-dark-emphasis mb-1" style="font-size: 0.70rem;">
                        <i class="bi bi-tools me-1"></i>Requerimientos Técnicos:
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
/* Colores Institucionales */
.text-primary-custom {
    color: #005f86 !important;
}

/* Tipografía de Detalles */
.detalle-sala {
    font-size: 0.75rem;
}
.detalle-actividad {
    font-size: 0.80rem;
}
.font-micro {
    font-size: 0.65rem;
}
.font-nano {
    font-size: 0.60rem;
}

/* Contenedores de Iconos y Avatares */
.icon-box-lg {
    width: 45px; 
    height: 45px;
}
.avatar-maestro {
    width: 35px; 
    height: 35px; 
    background-color: #005f86;
}

/* Interacción de la Tarjeta Base */
.room-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.room-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 .5rem 1.5rem rgba(0,0,0,.1) !important;
}

/* Interacción de la Lista de Eventos */
.event-item {
  border-left: 4px solid transparent !important;
  transition: all 0.2s ease;
}
.event-item:hover {
  background-color: #f8f9fa;
  border-left: 4px solid #005f86 !important;
}

.border-dashed {
    border-style: dashed !important;
    border-width: 2px !important;
}
</style>