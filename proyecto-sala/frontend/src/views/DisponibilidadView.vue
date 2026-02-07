<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router'; 
import SalaCard from '@/components/SalaCard.vue';
import ApiService from '@/services/ApiService.js';

const router = useRouter(); 


const HORA_APERTURA = 8; 
const HORA_CIERRE = 23;  

const reservaciones = ref([]);
const salas = ref([]); 
const fechaSeleccionada = ref(new Date().toISOString().slice(0, 10)); 

const cargando = ref(true);
const error = ref(null);
const servicioCerrado = ref(false); 

let socket = null;


const checkEstadoServicio = () => {
  const ahora = new Date();
  const horaActual = ahora.getHours();
  

  if (horaActual < HORA_APERTURA || horaActual >= HORA_CIERRE) {
    servicioCerrado.value = true;
  } else {
    servicioCerrado.value = false;
  }
};

const cargarDatos = async () => {
  if (salas.value.length === 0) cargando.value = true;
  error.value = null; 
  
  try {
    const [resReservas, resSalas] = await Promise.all([
        ApiService.obtenerReservas(),
        ApiService.obtenerSalas()
    ]);
    
    const dataReservas = resReservas.data;
    const dataSalas = resSalas.data;

    salas.value = dataSalas;
    
    reservaciones.value = dataReservas.map(item => {
      const formatearHora = (isoString) => {
        if (!isoString) return '--:--';
        const fecha = new Date(isoString);
        return fecha.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: false });
      };

      const extraerFecha = (isoString) => {
        if (!isoString) return '';
        return isoString.split('T')[0];
      };

      return {
        id: item.id,
        maestro: item.maestro_nombre || item.maestro || 'Desconocido',
        sala: item.sala_nombre || (typeof item.sala === 'object' ? item.sala.nombre_sala : item.sala) || 'Sala sin nombre',
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
    if (e.response && e.response.status === 401) {
        router.push('/login');
    } else if (salas.value.length === 0) {
        error.value = "No se pudo cargar la información. Verifica tu conexión con el servidor.";
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
  const [anio, mes, dia] = fechaSeleccionada.value.split('-').map(Number);
  const fecha = new Date(anio, mes - 1, dia);
  
  fecha.setDate(fecha.getDate() + dias);
  
  const nuevoAnio = fecha.getFullYear();
  const nuevoMes = String(fecha.getMonth() + 1).padStart(2, '0');
  const nuevoDia = String(fecha.getDate()).padStart(2, '0');
  
  fechaSeleccionada.value = `${nuevoAnio}-${nuevoMes}-${nuevoDia}`;
};

const reservacionesPorSala = computed(() => {
  const listaCompleta = salas.value.map(salaObj => {
    const idSala = salaObj.clave_sala || salaObj.id;
    const nombreSala = salaObj.nombre_sala || salaObj.nombre || `Sala ${idSala}`;
    
    const eventos = reservaciones.value.filter(reserva => {
        const isSameRoom = String(reserva.sala).trim() === String(nombreSala).trim();
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
  checkEstadoServicio(); 
 
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

     
      <div v-if="!servicioCerrado" class="d-flex flex-wrap gap-3 align-items-center">
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

  
    <div v-if="servicioCerrado" class="text-center py-5 mt-4 bg-white rounded shadow-sm border border-warning">
        <div class="py-5">
            <i class="bi bi-clock-history text-warning display-1"></i>
            <h2 class="mt-4 fw-bold text-dark">Servicio Cerrado</h2>
            <p class="text-muted fs-5">
                El sistema de reservas y consulta solo está disponible en horario laboral.
            </p>
            <div class="d-inline-block bg-light px-4 py-2 rounded-pill border mt-2">
                <span class="fw-bold text-primary">Horario de Atención:</span> 08:00 AM - 04:00 PM
            </div>
        </div>
    </div>

   
    <div v-else>
        
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
              <SalaCard :sala="grupo" />
            </div>
          </div>

        </div>
    </div>

  </div>
</template>

<style scoped>

.form-control:focus, .btn:focus {
  box-shadow: none;
  border-color: #005f86;
}
</style>