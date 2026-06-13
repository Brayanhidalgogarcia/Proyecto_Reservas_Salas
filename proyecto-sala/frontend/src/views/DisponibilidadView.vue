<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'; // Añadimos watch
import { useRouter } from 'vue-router'; 
import SalaCard from '@/components/SalaCard.vue';
import ApiService from '@/services/ApiService.js';
import { useWebSocket } from '@/composables/useWebSocket.js';

let intervaloVigia;

const router = useRouter(); 
const { conectar } = useWebSocket(cargarDatos);

onMounted(() => {
  checkEstadoServicio(); 
  cargarDatos(); 
  conectar();

  intervaloVigia = setInterval(() => {
    checkEstadoServicio();
  }, 60000);
});

onUnmounted(() => {
  clearInterval(intervaloVigia);
});

const HORA_APERTURA = 8; 
const HORA_CIERRE = 16;  // Sintonizado a las 16 hrs (04:00 PM) como dice tu cartel
  
const reservaciones = ref([]);
const salas = ref([]); 
const fechaSeleccionada = ref(new Date().toISOString().slice(0, 10)); 

const cargando = ref(true);
const error = ref(null);
const servicioCerrado = ref(false); 

const isSuperUser = ref(false); 

// CORRECCIÓN: El candado de hora solo se activa si el día consultado es HOY
const checkEstadoServicio = () => {
  const ahora = new Date();
  const horaActual = ahora.getHours();
  
  // Obtenemos la fecha de hoy en formato local YYYY-MM-DD
  const anio = ahora.getFullYear();
  const mes = String(ahora.getMonth() + 1).padStart(2, '0');
  const dia = String(ahora.getDate()).padStart(2, '0');
  const hoyStr = `${anio}-${mes}-${dia}`;
  
  if (fechaSeleccionada.value === hoyStr && (horaActual < HORA_APERTURA || horaActual >= HORA_CIERRE)) {
    servicioCerrado.value = true;
  } else {
    servicioCerrado.value = false;
  }
};

// Monitoreamos la fecha seleccionada para recalcular si se debe abrir o cerrar la vista
watch(fechaSeleccionada, () => {
  checkEstadoServicio();
});

const cargarIdentidad = () => {
  try {
    const userString = localStorage.getItem('usuario_info');
    if (userString) {
      const user = JSON.parse(userString);
      isSuperUser.value = user.is_superuser || false;
    }
  } catch (error) {
    console.warn("No se pudo leer la identidad del usuario:", error);
    isSuperUser.value = false;
  }
};

async function cargarDatos() {
  if (salas.value.length === 0) cargando.value = true;
  error.value = null; 
  
  cargarIdentidad();
  
  try {
    const [resReservas, resSalas] = await Promise.all([
        ApiService.obtenerReservas(),
        ApiService.obtenerSalas()
    ]);
    
    const dataReservas = resReservas.data || resReservas;
    const dataSalas = resSalas.data || resSalas;

    salas.value = dataSalas;
    
    reservaciones.value = dataReservas.map(item => {
      const formatearHora = (isoString) => {
        if (!isoString) return '--:--';
        const fecha = new Date(isoString);
        return fecha.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: false });
      };

      const extraerFecha = (isoString) => {
        if (!isoString) return '';
        const fecha = new Date(isoString);
        const anio = fecha.getFullYear();
        const mes = String(fecha.getMonth() + 1).padStart(2, '0');
        const dia = String(fecha.getDate()).padStart(2, '0');
        
        return `${anio}-${mes}-${dia}`;
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
        actividad: item.actividad || 'Actividad',
        detalleActividad: item.asignatura || item.tema || 'Sin descripción',
        requerimientos: item.requerimientos || null
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
}

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
  return salas.value.map(salaObj => {
    const idSala = salaObj.clave_sala || salaObj.id;
    const nombreSala = salaObj.nombre_sala || salaObj.nombre || `Sala ${idSala}`;
    
    // CORRECCIÓN: Extracción segura si el edificio viene serializado como objeto relacional
    const nombreEdificio = typeof salaObj.edificio === 'object' && salaObj.edificio !== null
      ? (salaObj.edificio.nombre_edificio || salaObj.edificio.nombre)
      : (salaObj.edificio || 'Edificio no asignado');
    
    const eventos = reservaciones.value.filter(reserva => {
        const isSameRoom = String(reserva.sala).trim() === String(nombreSala).trim();
        const isSameDate = reserva.fecha === fechaSeleccionada.value;
        return isSameRoom && isSameDate;
    });

    eventos.sort((a, b) => new Date(a.inicioRaw) - new Date(b.inicioRaw));

    return {
        nombre: nombreSala,
        edificio: nombreEdificio, 
        capacidad: salaObj.capacidad, 
        eventos: eventos
    };
  });
});
</script>

<template>
  <div class="container-fluid p-4">

    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center card-header border-0 bg-white mb-4 p-3 rounded shadow-sm">
        <h2 class="text-dark mb-0 fw-bold d-flex align-items-center">
           <i class="bi bi-calendar-check text-secondary me-2"></i> Disponibilidad
        </h2>
        
        <div class="d-flex align-items-center gap-2 mt-3 mt-sm-0">
          <button class="btn btn-outline-secondary btn-sm fw-semibold" @click="cambiarDia(-1)">
            <i class="bi bi-chevron-left"></i> Anterior
          </button>
          <input 
            type="date" 
            class="form-control form-control-sm text-center fw-bold font-monospace bg-light" 
            v-model="fechaSeleccionada"
            style="max-width: 170px;"
          >
          <button class="btn btn-outline-secondary btn-sm fw-semibold" @click="cambiarDia(1)">
            Siguiente <i class="bi bi-chevron-right"></i>
          </button>
        </div>
    </div>

    <div>
      <div v-if="cargando" class="text-center py-5 text-muted">
        <div class="spinner-border text-primary mb-2" role="status"></div>
        <p class="small">Sincronizando itinerarios...</p>
      </div>

      <div v-else-if="servicioCerrado" class="text-center py-5 mt-4 bg-white rounded shadow-sm border border-warning">
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

      <div v-else class="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">
        <div class="col" v-for="grupo in reservacionesPorSala" :key="grupo.nombre">
          <SalaCard :sala="grupo" :isSuperUser="isSuperUser" />
        </div>
      </div>
    </div>

  </div>
</template>