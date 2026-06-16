<script setup>
/**
 * @file DisponibilidadView.vue
 * @description Vista principal para la consulta de ocupación de salas.
 * Permite a los usuarios navegar por fechas y visualizar qué actividades
 * están programadas. Incluye restricciones de viaje en el tiempo para
 * usuarios estándar y sincronización en tiempo real vía WebSockets.
 */

// ==========================================
// 1. IMPORTS
// ==========================================
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router'; 
import SalaCard from '@/components/SalaCard.vue';
import ApiService from '@/services/ApiService.js';
import { useWebSocket } from '@/composables/useWebSocket.js';
import HeaderInstitucional from '@/components/HeaderInstitucional.vue';

// ==========================================
// 2. CONFIGURACIÓN Y COMPOSABLES
// ==========================================
const router = useRouter(); 
const { conectar } = useWebSocket(cargarDatos);

/**
 * Calcula la fecha actual basándose en la zona horaria local del cliente.
 * Evita el problema del desfase UTC de JavaScript.
 * @returns {string} Fecha en formato 'YYYY-MM-DD'
 */
const obtenerFechaHoy = () => {
  const ahora = new Date();
  const anio = ahora.getFullYear();
  const mes = String(ahora.getMonth() + 1).padStart(2, '0');
  const dia = String(ahora.getDate()).padStart(2, '0');
  return `${anio}-${mes}-${dia}`;
};

const HOY_STR = obtenerFechaHoy();

// ==========================================
// 3. ESTADO REACTIVO (Variables)
// ==========================================
const reservaciones = ref([]);
const salas = ref([]); 
const fechaSeleccionada = ref(HOY_STR); 
const cargando = ref(true);
const error = ref(null);
const isSuperUser = ref(false); 

// ==========================================
// 4. PROPIEDADES COMPUTADAS
// ==========================================

/**
 * Determina si la fecha que el usuario está viendo en el calendario
 * es anterior al día de hoy.
 * @type {ComputedRef<boolean>}
 */
const esFechaPasada = computed(() => {
  return fechaSeleccionada.value < HOY_STR;
});

/**
 * Regla de negocio: Deshabilita el botón de retroceso ("Anterior") 
 * si el usuario es docente y está intentando ver el pasado.
 * @type {ComputedRef<boolean>}
 */
const deshabilitarAnterior = computed(() => {
  return !isSuperUser.value && fechaSeleccionada.value <= HOY_STR;
});

/**
 * Núcleo del renderizado: Cruza el catálogo de salas con el array de reservas.
 * Agrupa y ordena cronológicamente los eventos pertenecientes a la fecha 
 * seleccionada para inyectarlos limpiamente en los componentes <SalaCard>.
 * @type {ComputedRef<Array>}
 */
const reservacionesPorSala = computed(() => {
  return salas.value.map(salaObj => {
    // 1. Estandarización de nombres de sala y edificio
    const idSala = salaObj.clave_sala || salaObj.id;
    const nombreSala = salaObj.nombre_sala || salaObj.nombre || `Sala ${idSala}`;
    
    const nombreEdificio = typeof salaObj.edificio === 'object' && salaObj.edificio !== null
      ? (salaObj.edificio.nombre_edificio || salaObj.edificio.nombre)
      : (salaObj.edificio || 'Edificio no asignado');
    
    // 2. Filtrado de eventos correspondientes a esta sala y a la fecha actual
    const eventos = reservaciones.value.filter(reserva => {
        const isSameRoom = String(reserva.sala).trim() === String(nombreSala).trim();
        const isSameDate = reserva.fecha === fechaSeleccionada.value;
        return isSameRoom && isSameDate;
    });

    // 3. Ordenamiento cronológico de los eventos del día
    eventos.sort((a, b) => new Date(a.inicioRaw) - new Date(b.inicioRaw));

    return {
        nombre: nombreSala,
        edificio: nombreEdificio, 
        capacidad: salaObj.capacidad, 
        eventos: eventos
    };
  });
});

// ==========================================
// 5. FUNCIONES Y MÉTODOS
// ==========================================

/**
 * Extrae el nivel de privilegios del usuario desde el almacenamiento local
 * para adaptar los controles de la interfaz (ej. habilitar viaje al pasado).
 */
const cargarIdentidad = () => {
  try {
    const isSuper = localStorage.getItem('is_superuser');
    isSuperUser.value = (String(isSuper).toLowerCase() === 'true' || String(isSuper) === '1');
  } catch (error) {
    console.warn("No se pudo leer la identidad del usuario:", error);
    isSuperUser.value = false;
  }
};

/**
 * Modifica la fecha actual de consulta sumando o restando días.
 * Maneja internamente los saltos de mes y años bisiestos.
 * @param {number} dias - Cantidad de días a desplazar (ej. -1 o 1)
 */
const cambiarDia = (dias) => {
  if (dias < 0 && deshabilitarAnterior.value) return; // Protección adicional

  const [anio, mes, dia] = fechaSeleccionada.value.split('-').map(Number);
  const fecha = new Date(anio, mes - 1, dia);
  
  fecha.setDate(fecha.getDate() + dias);
  
  const nuevoAnio = fecha.getFullYear();
  const nuevoMes = String(fecha.getMonth() + 1).padStart(2, '0');
  const nuevoDia = String(fecha.getDate()).padStart(2, '0');
  
  fechaSeleccionada.value = `${nuevoAnio}-${nuevoMes}-${nuevoDia}`;
};

/**
 * Función principal de inicialización. Descarga concurrentemente el 
 * catálogo de salas y las reservaciones activas desde el backend, 
 * y aplica un formateo exhaustivo de fechas y textos para la UI.
 */
async function cargarDatos() {
  if (salas.value.length === 0) cargando.value = true;
  error.value = null; 
  
  cargarIdentidad();
  
  try {
    // Peticiones concurrentes para mayor velocidad de carga
    const [resReservas, resSalas] = await Promise.all([
        ApiService.obtenerReservas(),
        ApiService.obtenerSalas()
    ]);
    
    const dataReservas = resReservas.data || resReservas;
    const dataSalas = resSalas.data || resSalas;

    salas.value = dataSalas;
    
    // Mapeo exhaustivo para estandarizar la estructura de datos que requiere el frontend
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
        
        // Función autoejecutable para construir dinámicamente la descripción de la actividad
        detalleActividad: (() => {
            if (item.asignatura && item.tema) return `${item.asignatura} — Tema: ${item.tema}`;
            if (item.asignatura) return item.asignatura;
            if (item.tema) return item.tema;
            return 'Sin descripción';
        })(),
        
        requerimientos: item.requerimientos || null
      };
    });

  } catch (e) {
    console.error("Error fetching data:", e);
    // Redirección forzada si el token de sesión ha expirado
    if (e.response && e.response.status === 401) {
        router.push('/login');
    } else if (salas.value.length === 0) {
        error.value = "No se pudo cargar la información. Verifica tu conexión con el servidor.";
    }
  } finally {
    cargando.value = false;
  }
}

// ==========================================
// 6. CICLO DE VIDA (Hooks)
// ==========================================
onMounted(() => {
  cargarDatos(); 
  conectar();
});
</script>

<template>
  <div class="container-fluid px-4 py-4">

    <HeaderInstitucional 
        titulo="Disponibilidad" 
        subtitulo="Consulta rápida de ocupación y horarios de espacios físicos."
        icono="bi-calendar-check"
    >
        <template #acciones>
            <span v-if="esFechaPasada && isSuperUser" class="badge bg-warning text-dark border border-warning me-2 d-flex align-items-center opacity-75">
                <i class="bi bi-clock-history me-1"></i> Historial
            </span>

            <button 
                class="btn btn-outline-secondary btn-sm fw-semibold shadow-sm" 
                @click="cambiarDia(-1)"
                :disabled="deshabilitarAnterior"
            >
                <i class="bi bi-chevron-left"></i> Anterior
            </button>
            <input 
                type="date" 
                class="form-control form-control-sm text-center fw-bold font-monospace bg-light shadow-sm" 
                v-model="fechaSeleccionada"
                :min="!isSuperUser ? HOY_STR : null"
                style="max-width: 170px;"
            >
            <button class="btn btn-outline-secondary btn-sm fw-semibold shadow-sm" @click="cambiarDia(1)">
                Siguiente <i class="bi bi-chevron-right"></i>
            </button>
        </template>
    </HeaderInstitucional>

    <div>
      <div v-if="cargando" class="text-center py-5 text-muted">
        <div class="spinner-border text-primary mb-2" role="status"></div>
        <p class="small">Sincronizando itinerarios...</p>
      </div>

      <div v-else class="row row-cols-1 row-cols-md-2 row-cols-xl-3 g-4">
        <div class="col" v-for="grupo in reservacionesPorSala" :key="grupo.nombre">
          <SalaCard :sala="grupo" :isSuperUser="isSuperUser" />
        </div>
      </div>
    </div>

  </div>
</template>