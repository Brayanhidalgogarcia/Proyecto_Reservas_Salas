<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router'; 
import SalaCard from '@/components/SalaCard.vue';
import ApiService from '@/services/ApiService.js';
import { useWebSocket } from '@/composables/useWebSocket.js';

const router = useRouter(); 
const { conectar } = useWebSocket(cargarDatos);
onMounted(() => {
  checkEstadoServicio(); 
  cargarDatos(); 
  conectar();
});

const HORA_APERTURA = 8; 
const HORA_CIERRE = 16;  
  
const reservaciones = ref([]);
const salas = ref([]); 
const fechaSeleccionada = ref(new Date().toISOString().slice(0, 10)); 

const cargando = ref(true);
const error = ref(null);
const servicioCerrado = ref(false); 

const isSuperUser = ref(false); 


const checkEstadoServicio = () => {
  const ahora = new Date();
  const horaActual = ahora.getHours();
  
  if (horaActual < HORA_APERTURA || horaActual >= HORA_CIERRE) {
    servicioCerrado.value = true;
  } else {
    servicioCerrado.value = false;
  }
};


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

const cargarDatos = async () => {
  if (salas.value.length === 0) cargando.value = true;
  error.value = null; 
  
  
  cargarIdentidad();
  
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
        // Obligamos a JavaScript a leer la fecha y traducirla a la zona horaria local
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
    
    
    const nombreEdificio = salaObj.edificio || 'Edificio no asignado';
    
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

  return listaCompleta;
});




</script>

<template>
  <div class="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">
            <div class="col" v-for="grupo in reservacionesPorSala" :key="grupo.nombre">
              <SalaCard :sala="grupo" :isSuperUser="isSuperUser" />
            </div>
          </div>
  </template>