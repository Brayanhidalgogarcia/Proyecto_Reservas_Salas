<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';


const reservaciones = ref([]);
const salas = ref([]); 
const fechaSeleccionada = ref(new Date().toISOString().slice(0, 10)); 

const cargando = ref(true);
const error = ref(null);


let socket = null;


const cargarDatos = async () => {
  
  if (salas.value.length === 0) cargando.value = true;
  error.value = null; 
  
  try {
   
    const [resReservas, resSalas] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/v1/reservas/'),
        fetch('http://127.0.0.1:8000/api/v1/salas/')
    ]);
    
    if (!resReservas.ok || !resSalas.ok) {
      throw new Error(`Error al conectar con el servidor.`);
    }

    const dataReservas = await resReservas.json();
    const dataSalas = await resSalas.json();

    
    salas.value = dataSalas;
    
    
    reservaciones.value = dataReservas.map(item => {
      const formatearHora = (isoString) => {
        if (!isoString) return '--:--';
        const fecha = new Date(isoString);
        return fecha.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: true });
      };

      const extraerFecha = (isoString) => {
        if (!isoString) return '';
        return isoString.split('T')[0];
      };

      return {
        id: item.id,
        maestro: item.maestro || 'Desconocido',
        sala: item.sala || 'Sala sin nombre', 
        division: item.division || 'General',
        fecha: extraerFecha(item.inicio),
        inicio: formatearHora(item.inicio),
        fin: formatearHora(item.fin),
        inicioRaw: item.inicio, 
        asignatura: item.asignatura,
        tema: item.tema
      };
    });

  } catch (e) {
    console.error("Error fetching data:", e);
    if (salas.value.length === 0) {
        error.value = "No se pudo cargar la información. Verifica que el servidor Backend esté encendido.";
    }
  } finally {
    cargando.value = false;
  }
};


const conectarWebSocket = () => {
  console.log("Intentando conectar al WebSocket...");
  socket = new WebSocket('ws://127.0.0.1:8000/ws/reservas/');

  socket.onopen = () => console.log("🟢 WebSocket Conectado!");
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("📩 Actualización recibida:", data.message);
    cargarDatos(); 
  };

  socket.onclose = () => setTimeout(conectarWebSocket, 3000);
  
  socket.onerror = (err) => {
    console.error("Error en WebSocket:", err);
    socket.close();
  };
};

const cambiarDia = (dias) => {
  const fecha = new Date(fechaSeleccionada.value);
  fecha.setDate(fecha.getDate() + dias + 1);
  fechaSeleccionada.value = fecha.toISOString().slice(0, 10);
};


const reservacionesPorSala = computed(() => {
  
  
  const listaCompleta = salas.value.map(salaObj => {
    
    const nombreSala = salaObj.nombre_sala || salaObj.nombre || `Sala ${salaObj.id}`;

    
    const eventos = reservaciones.value.filter(reserva => {
        const isSameRoom = String(reserva.sala) === String(nombreSala);
        const isSameDate = reserva.fecha === fechaSeleccionada.value;
        
        return isSameRoom && isSameDate;
    });

    
    eventos.sort((a, b) => new Date(a.inicioRaw) - new Date(b.inicioRaw));

    return {
        nombre: nombreSala,
        capacidad: salaObj.capacidad, 
        eventos: eventos
    };
  });

  return listaCompleta;
});

onMounted(() => {
  cargarDatos();
  conectarWebSocket();
});

onUnmounted(() => {
  if (socket) socket.close();
});
</script>

<template>
  <div class="container-fluid p-4">
    
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
      <div class="d-flex align-items-center">
        
        <h2 class="text-dark mb-0 me-3 fw-bold">
          <i class="bi bi-calendar-check text-secondary"></i> Disponibilidad
        </h2>
      </div>

      
      <div class="d-flex flex-wrap gap-3 align-items-center">
        
        <div class="d-flex align-items-center bg-white p-1 rounded shadow-sm border">
          <button @click="cambiarDia(-1)" class="btn btn-link text-decoration-none text-dark px-2">
            <i class="bi bi-chevron-left"></i>
          </button>
          
          <input 
            type="date" 
            v-model="fechaSeleccionada" 
            class="form-control border-0 text-center fw-bold text-dark" 
            style="width: 140px; cursor: pointer;"
          />

          <button @click="cambiarDia(1)" class="btn btn-link text-decoration-none text-dark px-2">
            <i class="bi bi-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>

    
    <div v-if="cargando" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-2 text-muted">Cargando agenda...</p>
    </div>

    
    <div v-else-if="error" class="alert alert-danger shadow-sm" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ error }}
    </div>

    
    <div v-else>
      
     
      <div v-if="reservacionesPorSala.length === 0" class="text-center py-5 bg-white rounded shadow-sm">
        <div class="text-muted opacity-50">
          <i class="bi bi-building-slash display-1"></i>
          <p class="mt-3 fs-4">No se encontraron salas.</p>
        </div>
      </div>

      
      <div class="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">
        
        <div class="col" v-for="grupo in reservacionesPorSala" :key="grupo.nombre">
          <div class="card h-100 shadow-sm border-0 room-card">
            
            <div class="card-header bg-white border-bottom-0 pt-3 pb-2 d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <div class="icon-box me-2 bg-light text-primary rounded-circle d-flex align-items-center justify-content-center" style="width:40px; height:40px;">
                  <i class="bi bi-easel2"></i>
                </div>
                <div>
                    <h5 class="card-title mb-0 fw-bold text-dark">{{ grupo.nombre }}</h5>
                    <small v-if="grupo.capacidad" class="text-muted" style="font-size: 0.75rem;">Cap: {{ grupo.capacidad }}</small>
                </div>
              </div>
              
              <span v-if="grupo.eventos.length === 0" class="badge bg-success bg-opacity-10 text-success rounded-pill px-2">Libre</span>
              <span v-else class="badge bg-warning bg-opacity-10 text-dark rounded-pill px-2">{{ grupo.eventos.length }} reservas</span>
            </div>

            <div class="card-body p-0 d-flex flex-column">
             
              <div v-if="grupo.eventos.length === 0" class="flex-grow-1 d-flex flex-column align-items-center justify-content-center py-5 text-center text-success bg-light bg-opacity-25 mx-2 mb-2 rounded border border-dashed border-success border-opacity-25">
                  <i class="bi bi-check-circle-fill fs-1 mb-2 opacity-75"></i>
                  <span class="fw-bold">Disponible</span>
                  <small class="text-muted px-3">Sin actividades programadas para hoy.</small>
              </div>

              
              <div v-else class="list-group list-group-flush flex-grow-1">
                <div 
                  v-for="reserva in grupo.eventos" 
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


.form-control:focus, .btn:focus {
  box-shadow: none;
  border-color: #005f86;
}
</style>