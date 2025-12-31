<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import ApiService from '@/services/ApiService.js';


const HORARIO_APERTURA = 8;
const HORARIO_CIERRE = 16;  


const nuevaReserva = ref({
  maestro: null,
  asignatura: null,
  sala: null,
  tema: '',
  fecha: new Date().toISOString().split('T')[0], 
  inicio: '',
  fin: ''     
});


const maestros = ref([]);
const asignaturas = ref([]);
const salas = ref([]);


const reservasExistentes = ref([]); 
const cargando = ref(false);
const enviando = ref(false);
const error = ref(null);
const mensajeExito = ref(null);


let socket = null;


async function cargarDatosIniciales() {
  cargando.value = true;
  error.value = null;
  try {
    
    const [resMaestros, resAsignaturas, resSalas] = await Promise.all([
      ApiService.obtenerMaestros(),
      ApiService.obtenerAsignaturas(),
      ApiService.obtenerSalas()
    ]);
    
    
    maestros.value = resMaestros.data || resMaestros;
    asignaturas.value = resAsignaturas.data || resAsignaturas;
    salas.value = resSalas.data || resSalas;

    
    await cargarReservasTabla();

  } catch (err) {
    console.error(err);
    error.value = 'Error al cargar datos. Verifica la conexión con el Backend.';
  } finally {
    cargando.value = false;
  }
}


async function cargarReservasTabla() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/reservas/');
        if (response.ok) {
            const data = await response.json();
            
            reservasExistentes.value = data.map(r => {
                
                const fechaStr = r.inicio ? r.inicio.split('T')[0] : '';
                
                
                const inicioStr = r.inicio ? new Date(r.inicio).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12: false}) : '';
                const finStr = r.fin ? new Date(r.fin).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12: false}) : '';

                
                let nombreSalaReal = 'Sala desconocida';
                let idSalaReal = null;

                if (r.sala && typeof r.sala === 'object') {
                    nombreSalaReal = r.sala.nombre_sala || r.sala.nombre;
                    idSalaReal = r.sala.id;
                } else {
                    nombreSalaReal = String(r.sala);
                }

                return {
                    id: r.id,
                    salaId: idSalaReal, 
                    salaNombre: nombreSalaReal,
                    fecha: fechaStr,
                    inicio: inicioStr,
                    fin: finStr,
                    raw: r,
                    maestro: r.maestro_nombre || r.maestro || 'Desconocido',
                    tema: r.tema,
                    asignatura: r.asignatura
                };
            });
        }
    } catch (e) {
        console.error("Error actualizando tabla:", e);
    }
}



const minFecha = computed(() => new Date().toISOString().split('T')[0]);


const generarHoras = () => {
    const horas = [];
    for (let i = HORARIO_APERTURA; i <= HORARIO_CIERRE; i++) {
        horas.push(`${String(i).padStart(2, '0')}:00`);
    }
    return horas;
};


const opcionesHoraInicio = computed(() => {
    let horas = generarHoras();
    
    
    if (nuevaReserva.value.fecha === minFecha.value) {
        const horaActual = new Date().getHours();
        horas = horas.filter(h => parseInt(h.split(':')[0]) > horaActual);
    }

    
    if (nuevaReserva.value.sala) {
        
        const salaObj = salas.value.find(s => (s.id || s.clave_sala) === nuevaReserva.value.sala);
        const nombreSala = salaObj ? (salaObj.nombre_sala || salaObj.nombre) : '';

        
        const ocupaciones = reservasExistentes.value.filter(r => {
            const coincideSala = (r.salaId === nuevaReserva.value.sala) || (String(r.salaNombre) === String(nombreSala));
            return coincideSala && r.fecha === nuevaReserva.value.fecha;
        });

        
        horas = horas.filter(h => {
            
            const estaOcupada = ocupaciones.some(r => h >= r.inicio && h < r.fin);
            return !estaOcupada;
        });
    }

    
    return horas.filter(h => parseInt(h.split(':')[0]) < HORARIO_CIERRE);
});



const opcionesHoraFin = computed(() => {
    let horas = generarHoras();
    if (!nuevaReserva.value.inicio) return [];
    
    
    horas = horas.filter(h => h > nuevaReserva.value.inicio);

    
    if (nuevaReserva.value.sala) {
        const salaObj = salas.value.find(s => (s.id || s.clave_sala) === nuevaReserva.value.sala);
        const nombreSala = salaObj ? (salaObj.nombre_sala || salaObj.nombre) : '';

        const ocupaciones = reservasExistentes.value.filter(r => {
            const coincideSala = (r.salaId === nuevaReserva.value.sala) || (String(r.salaNombre) === String(nombreSala));
            return coincideSala && r.fecha === nuevaReserva.value.fecha;
        });

        
        const reservasFuturas = ocupaciones.filter(r => r.inicio >= nuevaReserva.value.inicio);
        
        if (reservasFuturas.length > 0) {
            
            reservasFuturas.sort((a, b) => a.inicio.localeCompare(b.inicio));
            const siguienteReserva = reservasFuturas[0];
            
            
            horas = horas.filter(h => h <= siguienteReserva.inicio);
        }
    }

    return horas;
});


const estadoSalasDiaSeleccionado = computed(() => {
    const dia = nuevaReserva.value.fecha;
    if (!dia) return [];

    const ahora = new Date();
    const esHoy = dia === minFecha.value;
    const horaActual = esHoy ? ahora.getHours() : 0;

    return salas.value.map(sala => {
        const idSala = sala.id || sala.clave_sala;
        const nombreSala = sala.nombre_sala || sala.nombre;

        
        const ocupaciones = reservasExistentes.value.filter(r => {
            const coincideSala = (r.salaId == idSala) || (r.salaNombre === nombreSala);
            const coincideFecha = r.fecha === dia;
            
            
            const finHoraNum = parseInt(r.fin.split(':')[0]); 
            const esFutura = !esHoy || (finHoraNum > horaActual);

            
            
            return coincideSala && coincideFecha && esFutura; 
        });

        
        const todasReservasDia = reservasExistentes.value.filter(r => {
            const coincideSala = (r.salaId == idSala) || (r.salaNombre === nombreSala);
            return coincideSala && r.fecha === dia;
        });

        let horasTotalesOcupadas = 0;
        todasReservasDia.forEach(r => {
            const ini = parseInt(r.inicio.split(':')[0]);
            const fin = parseInt(r.fin.split(':')[0]);
            horasTotalesOcupadas += (fin - ini);
        });

        const turnoTotal = HORARIO_CIERRE - HORARIO_APERTURA;
        const esAgotada = horasTotalesOcupadas >= turnoTotal;

        ocupaciones.sort((a, b) => a.inicio.localeCompare(b.inicio));

        return {
            id: idSala,
            nombre: nombreSala,
            ocupado: ocupaciones.length > 0, 
            horariosOcupados: ocupaciones.map(o => `${o.inicio} - ${o.fin}`),
            agotada: esAgotada 
        };
    });
});

function seleccionarSala(idSala) {
    nuevaReserva.value.sala = idSala;
}



async function agregarReserva() {
  enviando.value = true;
  error.value = null;
  mensajeExito.value = null;

  
  if (!nuevaReserva.value.maestro || !nuevaReserva.value.asignatura || !nuevaReserva.value.sala) {
      error.value = 'Por favor selecciona Sala, Maestro y Asignatura obligatoriamente.';
      enviando.value = false;
      return;
  }

  
  if (nuevaReserva.value.fecha < minFecha.value) {
      error.value = 'No puedes reservar en el pasado.';
      enviando.value = false;
      return;
  }

 
  if (nuevaReserva.value.inicio >= nuevaReserva.value.fin) {
      error.value = 'La hora de inicio debe ser antes de la hora de fin.';
      enviando.value = false;
      return;
  }

  
  const conflicto = reservasExistentes.value.find(r => {
      const mismaSala = String(r.salaId) == String(nuevaReserva.value.sala);
      const mismaFecha = r.fecha === nuevaReserva.value.fecha;
      
      if (!mismaSala || !mismaFecha) return false;

      const hayChoque = (nuevaReserva.value.inicio < r.fin) && (nuevaReserva.value.fin > r.inicio);
      return hayChoque;
  });

  if (conflicto) {
      error.value = `¡Conflicto! La sala ya está ocupada de ${conflicto.inicio} a ${conflicto.fin}.`;
      enviando.value = false;
      return;
  }

  const inicioISO = `${nuevaReserva.value.fecha}T${nuevaReserva.value.inicio}:00`;
  const finISO = `${nuevaReserva.value.fecha}T${nuevaReserva.value.fin}:00`;

  const datosParaAPI = {
    maestro: nuevaReserva.value.maestro,
    asignatura: nuevaReserva.value.asignatura,
    sala: nuevaReserva.value.sala,
    tema: nuevaReserva.value.tema,
    inicio: inicioISO,
    fin: finISO
  };

  try {
    await ApiService.crearReserva(datosParaAPI);
    mensajeExito.value = '¡Reserva creada con éxito!';
    
    
    nuevaReserva.value = { 
        ...nuevaReserva.value, 
        maestro: null, 
        asignatura: null, 
        sala: null, 
        tema: '', 
        inicio: '', 
        fin: '' 
    };
  } catch (err) {
    const msg = err.response?.data?.non_field_errors?.[0] || err.response?.data?.detail || err.message;
    error.value = 'Error al crear la reserva: ' + msg;
  } finally {
    enviando.value = false;
  }
}


async function cancelarReserva(id) {
    if(!confirm("¿Deseas cancelar esta reserva?")) return;

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/reservas/${id}/`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
            alert("Error al cancelar.");
        }
    } catch (e) {
        console.error(e);
    }
}


const conectarWebSocket = () => {
  
  socket = new WebSocket('ws://127.0.0.1:8000/ws/reservas/');
  
  socket.onmessage = () => {
    console.log("Actualización recibida");
    cargarReservasTabla();
  };
  
  socket.onclose = () => setTimeout(conectarWebSocket, 3000);
};

onMounted(() => {
  cargarDatosIniciales();
  conectarWebSocket();
});

onUnmounted(() => {
  if (socket) socket.close();
});
</script>

<template>
  <div class="container-fluid p-4"> 
    <div class="row">
        
        <div class="col-lg-5 mb-4">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-white fw-bold py-3">
                    <i class="bi bi-pencil-square me-2 text-primary"></i>Nueva Reservación
                </div>
                <div class="card-body">
                    
                    <div v-if="cargando" class="alert alert-light text-center"><span class="spinner-border spinner-border-sm me-2"></span>Cargando datos...</div>
                    <div v-if="error" class="alert alert-danger py-2 small d-flex align-items-center">
                        <i class="bi bi-exclamation-octagon-fill me-2"></i>
                        {{ error }}
                    </div>
                    <div v-if="mensajeExito" class="alert alert-success py-2 alert-dismissible fade show small">
                        {{ mensajeExito }}
                        <button type="button" class="btn-close" @click="mensajeExito = null"></button>
                    </div>

                    <form @submit.prevent="agregarReserva">
                        
                        <div class="mb-3 p-2 bg-light rounded border">
                            <label class="form-label fw-bold text-secondary small">FECHA DE USO</label>
                            <input 
                                type="date" 
                                class="form-control fw-bold text-center" 
                                v-model="nuevaReserva.fecha" 
                                :min="minFecha"
                                required
                            >
                            <div class="form-text text-muted small text-center">Selecciona el día para ver disponibilidad</div>
                        </div>

                        
                        <div class="row g-2 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small">Maestro</label>
                                <select class="form-select form-select-sm" v-model="nuevaReserva.maestro" required>
                                    <option :value="null" disabled>Selecciona...</option>
                                    <option v-for="m in maestros" :key="m.id || m.matricula_m" :value="m.id || m.matricula_m">
                                        {{ m.nombre }} {{ m.apellido_p }}
                                    </option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small">Sala</label>
                                <select class="form-select form-select-sm" v-model="nuevaReserva.sala" required>
                                    <option :value="null" disabled>Selecciona...</option>
                                    <option v-for="s in salas" :key="s.id || s.clave_sala" :value="s.id || s.clave_sala">
                                        {{ s.nombre_sala }}
                                    </option>
                                </select>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small">Asignatura</label>
                            <select class="form-select form-select-sm" v-model="nuevaReserva.asignatura" required>
                                <option :value="null" disabled>Selecciona...</option>
                                <option v-for="a in asignaturas" :key="a.id || a.clave_asignatura" :value="a.id || a.clave_asignatura">
                                    {{ a.nombre_asignatura }}
                                </option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small">Tema (Opcional)</label>
                            <input type="text" class="form-control form-control-sm" v-model="nuevaReserva.tema" placeholder="Ej. Proyección">
                        </div>

                       
                        <div class="row mb-4">
                            <label class="form-label fw-bold text-secondary small">HORARIO (08:00 - 16:00)</label>
                            
                            <div class="col-6">
                                <label class="small text-muted">Inicio</label>
                                <select 
                                    class="form-select text-center" 
                                    v-model="nuevaReserva.inicio" 
                                    required
                                >
                                    <option value="" disabled>--:--</option>
                                    <option v-for="h in opcionesHoraInicio" :key="h" :value="h">{{ h }}</option>
                                </select>
                                <div v-if="opcionesHoraInicio.length === 0" class="text-danger x-small mt-1">Sin horarios disponibles.</div>
                            </div>
                            
                            <div class="col-6">
                                <label class="small text-muted">Fin</label>
                                <select 
                                    class="form-select text-center" 
                                    v-model="nuevaReserva.fin" 
                                    required
                                    :disabled="!nuevaReserva.inicio"
                                >
                                    <option value="" disabled>--:--</option>
                                    <option v-for="h in opcionesHoraFin" :key="h" :value="h">{{ h }}</option>
                                </select>
                            </div>
                        </div>

                        <button type="submit" class="btn btn-primary w-100 py-2" :disabled="enviando || cargando">
                            <span v-if="enviando" class="spinner-border spinner-border-sm me-2"></span>
                            {{ enviando ? 'Guardando...' : 'Confirmar Reserva' }}
                        </button>
                    </form>
                </div>
            </div>
        </div>

        
        <div class="col-lg-7">
            <div class="card shadow-sm border-0 h-100">
                <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
                    <div>
                        <span class="fw-bold text-dark">Estado de Salas</span>
                        <div class="small text-muted">Fecha: {{ nuevaReserva.fecha }}</div>
                    </div>
                    <span class="badge bg-light text-dark border">
                        <i class="bi bi-clock me-1"></i> 8am - 4pm
                    </span>
                </div>
                
                <div class="card-body p-0 bg-light">
                    <div class="list-group list-group-flush">
                        <div v-if="estadoSalasDiaSeleccionado.length === 0" class="text-center p-4 text-muted">
                            Cargando información...
                        </div>

                        <div v-for="sala in estadoSalasDiaSeleccionado" :key="sala.id" class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <div class="d-flex align-items-center">
                                
                                <div 
                                    class="rounded-circle me-3 d-flex align-items-center justify-content-center text-white fw-bold shadow-sm"
                                    :class="sala.agotada ? 'bg-danger' : (sala.ocupado ? 'bg-warning' : 'bg-success')" 
                                    style="width: 45px; height: 45px;"
                                >
                                    <i :class="sala.agotada ? 'bi bi-slash-circle' : (sala.ocupado ? 'bi bi-clock-history' : 'bi bi-check-lg')"></i>
                                </div>
                                <div>
                                    <h6 class="mb-0 fw-bold">{{ sala.nombre }}</h6>
                                    
                                    
                                    <div v-if="sala.agotada" class="text-danger small fw-bold">
                                        AGOTADA
                                    </div>
                                    <div v-else-if="!sala.ocupado" class="text-success small">
                                        Totalmente Libre
                                    </div>
                                    <div v-else class="text-muted small">
                                        <span class="text-danger fw-bold">Ocupado:</span> 
                                        {{ sala.horariosOcupados.join(', ') }}
                                    </div>
                                </div>
                            </div>
                            
                           
                            <button 
                                type="button"
                                @click="seleccionarSala(sala.id)" 
                                class="btn btn-sm"
                                :class="nuevaReserva.sala == sala.id ? 'btn-primary' : 'btn-outline-secondary'"
                                title="Seleccionar sala"
                                :disabled="sala.agotada"
                            >
                                {{ nuevaReserva.sala == sala.id ? 'Seleccionada' : 'Usar' }}
                            </button>
                        </div>
                    </div>
                </div>
                <div class="card-footer bg-white text-center small text-muted">
                    Se muestran solo ocupaciones futuras del día seleccionado.
                </div>
            </div>
        </div>

    </div>
  </div>
</template>

<style scoped>
.form-control:focus, .form-select:focus {
  border-color: #005f86;
  box-shadow: 0 0 0 0.2rem rgba(0, 95, 134, 0.25);
}
.list-group-item {
    transition: background-color 0.2s;
}
.list-group-item:hover {
    background-color: #f8f9fa;
}
.x-small {
    font-size: 0.75rem;
}
</style>
