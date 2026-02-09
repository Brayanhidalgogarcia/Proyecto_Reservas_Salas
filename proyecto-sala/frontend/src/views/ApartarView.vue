<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import ApiService from '@/services/ApiService.js';


const servicioCerrado = ref(false); 

const checkEstadoServicio = () => {
  const ahora = new Date();
  const horaActual = ahora.getHours();

  if (horaActual < 8 || horaActual >= 16) {
    servicioCerrado.value = true;
  } else {
    servicioCerrado.value = false;
  }
};

const HORARIO_APERTURA = 8;
const HORARIO_CIERRE = 16;

const currentUserId = ref(null);
const isSuperUser = ref(false);
const nombreUsuarioLogueado = ref('Cargando usuario...'); 

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


function obtenerIdDesdeToken() {
    const token = localStorage.getItem('access') || localStorage.getItem('token');
    if (!token) return null;
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''));
        return JSON.parse(jsonPayload).user_id;
    } catch (e) {
        return null;
    }
}

async function cargarIdentidad() {
    let uid = localStorage.getItem('user_id');
    let isSuper = localStorage.getItem('is_superuser');

    if (!uid) uid = obtenerIdDesdeToken();

    currentUserId.value = uid;
    
    isSuperUser.value = (String(isSuper).toLowerCase() === 'true' || String(isSuper) === '1');
}

function tengoPermisoBorrar(reserva) {
    if (isSuperUser.value) return true;
    if (!currentUserId.value || !reserva.creadoPor) return false;
    return String(currentUserId.value) === String(reserva.creadoPor);
}


async function cargarDatos() {
    cargando.value = true;
    error.value = null;

    await cargarIdentidad();

    try {
        const [resMaestros, resAsignaturas, resSalas, resReservas] = await Promise.all([
            ApiService.obtenerMaestros(),
            ApiService.obtenerAsignaturas(),
            ApiService.obtenerSalas(),
            ApiService.obtenerReservas()
        ]);

        maestros.value = resMaestros.data || resMaestros;
        asignaturas.value = resAsignaturas.data || resAsignaturas;
        salas.value = resSalas.data || resSalas;
        const dataReservas = resReservas.data || resReservas;
        
  
        if (!isSuperUser.value && currentUserId.value) {
            
           
            const maestroEncontrado = maestros.value.find(m => {
                
                let uId = m.usuario_id || m.usuario;
               
                if (typeof uId === 'object' && uId !== null) {
                    uId = uId.id;
                }
                return String(uId) === String(currentUserId.value);
            });

            if (maestroEncontrado) {
                console.log("Maestro identificado:", maestroEncontrado.nombre);
                nuevaReserva.value.maestro = maestroEncontrado.id || maestroEncontrado.matricula_m;
                nombreUsuarioLogueado.value = `${maestroEncontrado.nombre} ${maestroEncontrado.apellido_p}`;
            } else {
                nombreUsuarioLogueado.value = "Usuario sin perfil de Maestro";
                console.warn(`No se encontró un maestro vinculado al usuario ID: ${currentUserId.value}`);
                
            }
        } else if (isSuperUser.value) {
            nombreUsuarioLogueado.value = "Administrador";
        }
        
        
        reservasExistentes.value = dataReservas.map(r => {
            let sId = null;
            let sNombre = 'Sala';
            
            if (r.sala && typeof r.sala === 'object') {
                sId = r.sala.id;
                sNombre = r.sala.nombre_sala || r.sala.nombre;
            } else {
                sNombre = String(r.sala);
                const match = salas.value.find(s => s.nombre_sala === sNombre);
                if (match) sId = match.id || match.clave_sala;
            }

            return {
                id: r.id,
                salaId: sId,
                salaNombre: sNombre,
                maestro: r.maestro_nombre || r.maestro,
                inicioFmt: r.inicio ? new Date(r.inicio).toLocaleTimeString('es-MX', {hour: '2-digit', minute:'2-digit', hour12: false}) : '',
                finFmt: r.fin ? new Date(r.fin).toLocaleTimeString('es-MX', {hour: '2-digit', minute:'2-digit', hour12: false}) : '',
                fecha: r.inicio ? r.inicio.split('T')[0] : '',
                creadoPor: r.creado_por_id 
            };
        });

    } catch (e) {
        console.error(e);
        error.value = "Error al cargar datos del servidor.";
    } finally {
        cargando.value = false;
    }
}


const minFecha = computed(() => new Date().toISOString().split('T')[0]);

const obtenerOcupacionesSala = () => {
    if (!nuevaReserva.value.sala || !nuevaReserva.value.fecha) return [];
    
    const salaObj = salas.value.find(s => (s.id || s.clave_sala) == nuevaReserva.value.sala);
    const nombreObj = salaObj ? (salaObj.nombre_sala || salaObj.nombre) : '';

    return reservasExistentes.value.filter(r => {
        const mismaSala = (r.salaId == nuevaReserva.value.sala) || (r.salaNombre === nombreObj);
        return mismaSala && r.fecha === nuevaReserva.value.fecha;
    });
};

const opcionesInicio = computed(() => {
    let horas = [];
    for(let i=HORARIO_APERTURA; i<HORARIO_CIERRE; i++) {
        horas.push(`${String(i).padStart(2,'0')}:00`);
    }
    if (nuevaReserva.value.fecha === minFecha.value) {
        const horaActual = new Date().getHours();
        horas = horas.filter(h => parseInt(h.split(':')[0]) > horaActual);
    }
    if (nuevaReserva.value.sala) {
        const ocupaciones = obtenerOcupacionesSala();
        horas = horas.filter(h => {
            return !ocupaciones.some(r => h >= r.inicioFmt && h < r.finFmt);
        });
    }
    return horas;
});

const opcionesFin = computed(() => {
    if(!nuevaReserva.value.inicio) return [];
    
    let horas = [];
    for(let i=HORARIO_APERTURA + 1; i<=HORARIO_CIERRE; i++) {
        horas.push(`${String(i).padStart(2,'0')}:00`);
    }
    horas = horas.filter(h => h > nuevaReserva.value.inicio);

    if (nuevaReserva.value.sala) {
        const ocupaciones = obtenerOcupacionesSala();
        const reservasFuturas = ocupaciones
            .filter(r => r.inicioFmt >= nuevaReserva.value.inicio)
            .sort((a, b) => a.inicioFmt.localeCompare(b.inicioFmt));

        if (reservasFuturas.length > 0) {
            const siguienteInicio = reservasFuturas[0].inicioFmt;
            horas = horas.filter(h => h <= siguienteInicio);
        }
    }
    return horas;
});

const estadoSalas = computed(() => {
    const dia = nuevaReserva.value.fecha;
    if (!dia) return [];

    return salas.value.map(sala => {
        const id = sala.id || sala.clave_sala;
        const nombre = sala.nombre_sala || sala.nombre;

        const ocupaciones = reservasExistentes.value.filter(r => {
            const matchId = r.salaId && r.salaId == id;
            const matchNombre = r.salaNombre === nombre;
            return (matchId || matchNombre) && r.fecha === dia;
        });

        ocupaciones.sort((a, b) => a.inicioFmt.localeCompare(b.inicioFmt));
        const reservaParaCancelar = ocupaciones.find(r => tengoPermisoBorrar(r));

        let horasOcupadas = 0;
        ocupaciones.forEach(r => {
            const hIni = parseInt(r.inicioFmt.split(':')[0]);
            const hFin = parseInt(r.finFmt.split(':')[0]);
            horasOcupadas += (hFin - hIni);
        });

        return {
            id: id,
            nombre: nombre,
            ocupado: ocupaciones.length > 0,
            reservas: ocupaciones,
            agotada: horasOcupadas >= (HORARIO_CIERRE - HORARIO_APERTURA),
            idCancelable: reservaParaCancelar ? reservaParaCancelar.id : null,
            descCancelable: reservaParaCancelar ? `${reservaParaCancelar.inicioFmt} - ${reservaParaCancelar.finFmt}` : ''
        };
    });
});



async function crearReserva() {
    error.value = null;
    mensajeExito.value = null;
    console.log("Intentando crear reserva...", nuevaReserva.value);

    const f = nuevaReserva.value;
    const esInvalido = (v) => v === null || v === undefined || v === '';

    if (esInvalido(f.fecha)) { 
        error.value = "La FECHA es obligatoria."; 
        window.scrollTo(0,0); return; 
    }
    
    
    if (isSuperUser.value && esInvalido(f.maestro)) { 
        error.value = "Debes seleccionar un MAESTRO."; 
        window.scrollTo(0,0); return; 
    }
    
    if (esInvalido(f.sala)) { 
        error.value = "Debes seleccionar una SALA."; 
        window.scrollTo(0,0); return; 
    }
    if (esInvalido(f.asignatura)) { 
        error.value = "Debes seleccionar una ASIGNATURA."; 
        window.scrollTo(0,0); return; 
    }
    if (esInvalido(f.inicio)) { 
        error.value = "La hora de INICIO es obligatoria."; 
        window.scrollTo(0,0); return; 
    }
    if (esInvalido(f.fin)) { 
        error.value = "La hora de FIN es obligatoria."; 
        window.scrollTo(0,0); return; 
    }
    
    enviando.value = true;
    try {
        const temaLimpio = f.tema && f.tema.trim() !== '' ? f.tema : null;

        const payload = {
            ...f,
            tema: temaLimpio,
            inicio: `${f.fecha}T${f.inicio}:00`,
            fin: `${f.fecha}T${f.fin}:00`
        };

        await ApiService.crearReserva(payload);
        
        mensajeExito.value = "¡Reserva creada con éxito!";
        window.scrollTo(0,0);
        
       
        nuevaReserva.value.inicio = ''; 
        nuevaReserva.value.fin = '';
        nuevaReserva.value.tema = ''; 
        
        await cargarDatos();
    } catch(e) {
        console.error("Error completo en crearReserva:", e);
        window.scrollTo(0,0); 
        
        if (e.response && e.response.data) {
            const data = e.response.data;
            if (data.detail) {
                error.value = data.detail;
            }
            else if (data.non_field_errors) {
                error.value = data.non_field_errors[0];
            }
            else {
               
                const primerCampo = Object.keys(data)[0];
                const mensaje = Array.isArray(data[primerCampo]) ? data[primerCampo][0] : data[primerCampo];
                error.value = `${primerCampo.toUpperCase()}: ${mensaje}`;
            }
        } else {
            error.value = "Error de conexión o servidor no responde (Revise consola).";
        }
    } finally {
        enviando.value = false;
    }
}

async function cancelar(id, horarioDesc) {
    if(!confirm(`¿Estás seguro de cancelar la reserva de ${horarioDesc}?`)) return;
    
    try {
        await ApiService.eliminarReserva(id);
        mensajeExito.value = "Reserva eliminada";
        await cargarDatos();
    } catch(e) {
        const status = e.response?.status;
        if(status === 403) alert("No tienes permiso para borrar esta reserva.");
        else alert("Error del servidor al intentar borrar.");
    }
}

function seleccionar(id) { nuevaReserva.value.sala = id; }

onMounted(() => {
    checkEstadoServicio();
    cargarDatos();
    socket = new WebSocket('ws://127.0.0.1:8000/ws/reservas/');
    socket.onmessage = () => { cargarDatos(); };
});
onUnmounted(() => { if(socket) socket.close(); });
</script>

<template>
  <div class="container-fluid p-4">

    <div class="d-flex align-items-center card-header border-0 bg-white mb-3">
        <h2 class="text-dark mb-0 me-3 fw-bold">
           <i class="bi bi-calendar-check text-secondary"></i> Apartar
        </h2>
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
        <div v-if="error" class="alert alert-danger shadow-sm border-0 d-flex align-items-center">
            <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ error }}
        </div>
        <div v-if="mensajeExito" class="alert alert-success shadow-sm border-0 d-flex align-items-center">
            <i class="bi bi-check-circle-fill me-2"></i> {{ mensajeExito }}
        </div>

        <div class="row">
            <div class="col-lg-4 mb-4">
                <div class="card shadow-sm border-0 h-100">
                    
                    
                    
                    <div class="card-body">
                        <form @submit.prevent="crearReserva">
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">FECHA</label>
                                <input type="date" class="form-control" v-model="nuevaReserva.fecha" :min="minFecha" required>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">MAESTRO</label>
                                
                                <select v-if="isSuperUser" class="form-select" v-model="nuevaReserva.maestro">
                                    <option :value="null">Seleccionar...</option>
                                    <option v-for="m in maestros" :value="m.id || m.matricula_m">
                                        {{ m.nombre }} {{ m.apellido_p }}
                                    </option>
                                </select>

                                <div v-else class="input-group">
                                    <span class="input-group-text bg-light text-primary"><i class="bi bi-person-fill"></i></span>
                                    <input type="text" class="form-control bg-light" :value="nombreUsuarioLogueado" disabled readonly>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">SALA</label>
                                <select class="form-select" v-model="nuevaReserva.sala">
                                    <option :value="null">Seleccionar...</option>
                                    <option v-for="s in salas" :value="s.id || s.clave_sala">{{ s.nombre_sala }}</option>
                                </select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">ASIGNATURA</label>
                                <select class="form-select" v-model="nuevaReserva.asignatura">
                                    <option :value="null">Seleccionar...</option>
                                    <option v-for="a in asignaturas" :value="a.id || a.clave_asignatura">{{ a.nombre_asignatura }}</option>
                                </select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label small fw-bold text-muted">TEMA <span class="fw-light">(Opcional)</span></label>
                                <input type="text" class="form-control" v-model="nuevaReserva.tema" placeholder="">
                            </div>

                            <div class="row g-2">
                                <div class="col-6">
                                    <label class="form-label small fw-bold text-muted">INICIO</label>
                                    <select class="form-select" v-model="nuevaReserva.inicio">
                                        <option v-for="h in opcionesInicio" :value="h">{{ h }}</option>
                                    </select>
                                </div>
                                <div class="col-6">
                                    <label class="form-label small fw-bold text-muted">FIN</label>
                                    <select class="form-select" v-model="nuevaReserva.fin">
                                        <option v-for="h in opcionesFin" :value="h">{{ h }}</option>
                                    </select>
                                </div>
                            </div>

                            <button class="btn btn-primary w-100 mt-4 py-2 fw-bold" :disabled="enviando">
                                <span v-if="enviando" class="spinner-border spinner-border-sm me-2"></span>
                                {{ enviando ? 'Reservando...' : 'Confirmar Reserva' }}
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <div class="col-lg-8">
                <div class="row g-3">
                    <div v-for="sala in estadoSalas" :key="sala.id" class="col-md-6">
                        <div class="card h-100 shadow-sm border border-light" :class="{'bg-light': !sala.ocupado}">
                            <div class="card-body d-flex flex-column">
                                
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <h6 class="fw-bold mb-0 text-dark">{{ sala.nombre }}</h6>
                                    <span class="badge border" 
                                          :class="sala.agotada ? 'text-danger border-danger bg-danger-subtle' : (sala.ocupado ? 'text-warning border-warning bg-warning-subtle text-dark-emphasis' : 'text-success border-success bg-success-subtle')">
                                        {{ sala.agotada ? 'LLENA' : (sala.ocupado ? 'OCUPADA' : 'LIBRE') }}
                                    </span>
                                </div>

                                <div class="flex-grow-1 mb-3">
                                    <div v-if="!sala.ocupado" class="text-center text-muted py-3 small">
                                        <i class="bi bi-check2-circle d-block fs-4 mb-1 text-success opacity-50"></i>
                                        Disponible todo el día
                                    </div>
                                    <ul v-else class="list-group list-group-flush small">
                                        <li v-for="res in sala.reservas" :key="res.id" class="list-group-item bg-transparent px-0 py-1 d-flex justify-content-between align-items-center border-bottom border-light">
                                            <div class="d-flex align-items-center">
                                                <i class="bi bi-clock me-2 text-muted"></i>
                                                <span class="fw-semibold text-dark">{{ res.inicioFmt }} - {{ res.finFmt }}</span>
                                            </div>
                                            <span class="text-secondary text-truncate ms-2" style="max-width: 120px; font-size: 0.85em;">
                                                {{ res.maestro }}
                                            </span>
                                        </li>
                                    </ul>
                                </div>

                                <div class="d-flex gap-2 mt-auto pt-2 border-top border-light">
                                    <button 
                                        v-if="sala.idCancelable"
                                        @click="cancelar(sala.idCancelable, sala.descCancelable)"
                                        class="btn btn-sm btn-outline-danger flex-grow-1"
                                        title="Cancelar reserva"
                                    >
                                        <i class="bi bi-trash me-1"></i> Cancelar
                                    </button>

                                    <button 
                                        @click="seleccionar(sala.id)"
                                        class="btn btn-sm btn-outline-primary"
                                        :class="sala.idCancelable ? 'flex-grow-0' : 'flex-grow-1'"
                                        :disabled="sala.agotada"
                                    >
                                        Usar Sala
                                    </button>
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

.form-control:focus, .form-select:focus { 
    border-color: #86b7fe; 
    box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15); 
}
.card {
    transition: transform 0.2s ease-in-out, box-shadow 0.2s;
}
.card:hover {
    border-color: #dee2e6;
}
.btn-sm {
    font-size: 0.85rem;
}
.bg-success-subtle { background-color: #d1e7dd; }
.bg-warning-subtle { background-color: #fff3cd; }
.bg-danger-subtle { background-color: #f8d7da; }
</style>