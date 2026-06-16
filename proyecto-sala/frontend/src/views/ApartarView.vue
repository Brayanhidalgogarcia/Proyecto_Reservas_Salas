<script setup>
/**
 * @file ReservarEspacioView.vue
 * @description Módulo de operaciones para la creación y cancelación de reservas.
 * Implementa validaciones de choque de horarios, restricciones por roles (Docente/Admin),
 * y filtrado en cascada (Edificio -> Sala -> Horas Disponibles).
 */

// ==========================================
// 1. IMPORTS
// ==========================================
import { ref, computed, onMounted, watch } from 'vue';
import ApiService from '@/services/ApiService.js';
import { useWebSocket } from '@/composables/useWebSocket.js';
import HeaderInstitucional from '@/components/HeaderInstitucional.vue';

// ==========================================
// 2. CONFIGURACIÓN Y COMPOSABLES
// ==========================================
const { conectar } = useWebSocket(cargarDatos);

const HORARIO_APERTURA = 8;
const HORARIO_CIERRE = 16;

/**
 * Calcula la fecha actual basándose en la zona horaria local del cliente.
 * Resuelve el bug donde toISOString() adelanta el día por el desfase UTC.
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

const currentUserId = ref(null);
const isSuperUser = ref(false);
const nombreUsuarioLogueado = ref('Cargando usuario...'); 

const nuevaReserva = ref({
  actividad: null,      
  edificio: null,        
  maestro: null,
  asignatura: null,
  sala: null,
  tema: '', 
  requerimientos: '',    
  fecha: HOY_STR,
  inicio: '',
  fin: ''    
});

const maestros = ref([]);
const asignaturas = ref([]);
const salas = ref([]);
const edificios = ref([]);
const actividades = ref([]);
const reservasExistentes = ref([]);

const cargando = ref(false);
const enviando = ref(false);
const error = ref(null);
const mensajeExito = ref(null);

// ==========================================
// 4. PROPIEDADES COMPUTADAS
// ==========================================

const salasFiltradas = computed(() => {
    if (!nuevaReserva.value.edificio) return [];
    return salas.value.filter(s => {
        const edificioSala = typeof s.edificio === 'object' && s.edificio !== null 
            ? (s.edificio.nombre_edificio || s.edificio.nombre) 
            : s.edificio;
            
        return String(edificioSala) === String(nuevaReserva.value.edificio);
    });
});

const esClase = computed(() => {
    if (!nuevaReserva.value.actividad) return false;
    const act = actividades.value.find(a => a.id === nuevaReserva.value.actividad);
    return act && act.nombre_actividad === 'Asignatura';
});

/**
 * Detecta si el usuario intentó dejar la fecha de hoy, 
 * pero el reloj actual ya superó la hora de cierre.
 */
const horarioVencidoHoy = computed(() => {
    if (nuevaReserva.value.fecha !== HOY_STR) return false;
    const horaActual = new Date().getHours();
    return horaActual >= HORARIO_CIERRE;
});

const opcionesInicio = computed(() => {
    let horas = [];
    for(let i = HORARIO_APERTURA; i < HORARIO_CIERRE; i++) {
        horas.push(`${String(i).padStart(2,'0')}:00`);
    }
    
    if (nuevaReserva.value.fecha === HOY_STR) {
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
    for(let i = HORARIO_APERTURA + 1; i <= HORARIO_CIERRE; i++) {
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
    if (!dia || !nuevaReserva.value.edificio) return [];

    const salasAMostrar = salas.value.filter(s => {
        const edificioSala = typeof s.edificio === 'object' && s.edificio !== null 
            ? (s.edificio.nombre_edificio || s.edificio.nombre) 
            : s.edificio;
        return String(edificioSala) === String(nuevaReserva.value.edificio);
    });

    return salasAMostrar.map(sala => {
        const id = sala.id || sala.clave_sala;
        const nombre = sala.nombre_sala || sala.nombre;
        const nombreEdificio = typeof sala.edificio === 'object' && sala.edificio !== null 
            ? (sala.edificio.nombre_edificio || sala.edificio.nombre) 
            : (sala.edificio || 'Edificio no asignado');

        const ocupaciones = reservasExistentes.value.filter(r => {
            const matchId = r.salaId && String(r.salaId) === String(id);
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
            edificioNombre: nombreEdificio, 
            ocupado: ocupaciones.length > 0,
            reservas: ocupaciones,
            agotada: horasOcupadas >= (HORARIO_CIERRE - HORARIO_APERTURA),
            idCancelable: reservaParaCancelar ? reservaParaCancelar.id : null,
            descCancelable: reservaParaCancelar ? `${reservaParaCancelar.inicioFmt} - ${reservaParaCancelar.finFmt}` : ''
        };
    });
});

// ==========================================
// 5. FUNCIONES Y MÉTODOS
// ==========================================

function limpiarAsignaturaSiEsEvento() {
    if (!esClase.value) nuevaReserva.value.asignatura = null;
}

function seleccionar(id) { 
    nuevaReserva.value.sala = id; 
}

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

const obtenerOcupacionesSala = () => {
    if (!nuevaReserva.value.sala || !nuevaReserva.value.fecha) return [];
    
    const salaObj = salas.value.find(s => String(s.id || s.clave_sala) === String(nuevaReserva.value.sala));
    const nombreObj = salaObj ? (salaObj.nombre_sala || salaObj.nombre) : '';

    return reservasExistentes.value.filter(r => {
        const mismaSala = (String(r.salaId) === String(nuevaReserva.value.sala)) || (r.salaNombre === nombreObj);
        return mismaSala && r.fecha === nuevaReserva.value.fecha;
    });
};

async function cargarDatos() {
    cargando.value = true;
    error.value = null;

    await cargarIdentidad();

    try {
        const [resMaestros, resAsignaturas, resSalas, resReservas, resEdificios, resActividades] = await Promise.all([
            ApiService.obtenerMaestros(),
            ApiService.obtenerAsignaturas(),
            ApiService.obtenerSalas(),
            ApiService.obtenerReservas(), 
            ApiService.obtenerEdificios(),  
            ApiService.obtenerActividades() 
        ]);

        maestros.value = resMaestros.data || resMaestros;
        asignaturas.value = resAsignaturas.data || resAsignaturas;
        salas.value = resSalas.data || resSalas;
        edificios.value = resEdificios.data || resEdificios;
        actividades.value = resActividades.data || resActividades;
        
        const dataReservas = resReservas.data || resReservas;
        
        if (!isSuperUser.value && currentUserId.value) {
            const maestroEncontrado = maestros.value.find(m => {
                let uId = m.usuario_id || m.usuario;
                if (typeof uId === 'object' && uId !== null) uId = uId.id;
                return String(uId) === String(currentUserId.value);
            });

            if (maestroEncontrado) {
                nuevaReserva.value.maestro = maestroEncontrado.id || maestroEncontrado.matricula_m;
                nombreUsuarioLogueado.value = `${maestroEncontrado.nombre} ${maestroEncontrado.apellido_p}`;
            } else {
                nombreUsuarioLogueado.value = "Usuario sin perfil de Maestro";
            }
        } else if (isSuperUser.value) {
            nombreUsuarioLogueado.value = "Administrador";
        }
        
        const extraerFechaLocal = (isoString) => {
            if (!isoString) return '';
            const f = new Date(isoString);
            const anio = f.getFullYear();
            const mes = String(f.getMonth() + 1).padStart(2, '0');
            const dia = String(f.getDate()).padStart(2, '0');
            return `${anio}-${mes}-${dia}`;
        };

        reservasExistentes.value = dataReservas.map(r => {
            let sId = null;
            let sNombre = 'Sala';
            
            if (r.sala && typeof r.sala === 'object') {
                sId = r.sala.id || r.sala.clave_sala;
                sNombre = r.sala.nombre_sala || r.sala.nombre;
            } else {
                sNombre = String(r.sala);
                const match = salas.value.find(s => (s.nombre_sala || s.nombre) === sNombre);
                if (match) sId = match.id || match.clave_sala;
            }

            return {
                id: r.id,
                salaId: sId,
                salaNombre: sNombre,
                edificio: typeof r.edificio === 'object' && r.edificio !== null ? (r.edificio.nombre_edificio || r.edificio.nombre) : (r.edificio || 'Sin Edificio'),
                actividad: r.actividad || 'Sin Actividad',
                detalleActividad: (() => {
                    if (r.asignatura && r.tema) return `${r.asignatura} — Tema: ${r.tema}`;
                    if (r.asignatura) return r.asignatura;
                    if (r.tema) return r.tema;
                    return 'Sin tema';
                })(),
                requerimientos: r.requerimientos || null,
                maestro: r.maestro_nombre || r.maestro,
                inicioFmt: r.inicio ? new Date(r.inicio).toLocaleTimeString('es-MX', {hour: '2-digit', minute:'2-digit', hour12: false}) : '',
                finFmt: r.fin ? new Date(r.fin).toLocaleTimeString('es-MX', {hour: '2-digit', minute:'2-digit', hour12: false}) : '',
                fecha: extraerFechaLocal(r.inicio), 
                creadoPor: r.creado_por_id 
            };
        });

    } catch (e) {
        console.error("Error al cargar datos", e);
        error.value = "Error al sincronizar con el servidor.";
    } finally {
        cargando.value = false;
    }
}

async function crearReserva() {
    error.value = null;
    mensajeExito.value = null;

    const f = nuevaReserva.value;
    const esInvalido = (v) => v === null || v === undefined || v === '';

    if (esInvalido(f.fecha)) { error.value = "La FECHA es obligatoria."; window.scrollTo(0,0); return; }
    if (esInvalido(f.actividad)) { error.value = "Debes seleccionar una ACTIVIDAD."; window.scrollTo(0,0); return; }
    if (isSuperUser.value && esInvalido(f.maestro)) { error.value = "Debes seleccionar un MAESTRO."; window.scrollTo(0,0); return; }
    if (esInvalido(f.sala)) { error.value = "Debes seleccionar una SALA."; window.scrollTo(0,0); return; }
    if (esClase.value && esInvalido(f.asignatura)) { error.value = "Para esta actividad, debes seleccionar una ASIGNATURA."; window.scrollTo(0,0); return; }
    if (esInvalido(f.inicio)) { error.value = "La hora de INICIO es obligatoria."; window.scrollTo(0,0); return; }
    if (esInvalido(f.fin)) { error.value = "La hora de FIN es obligatoria."; window.scrollTo(0,0); return; }
    
    enviando.value = true;
    try {
        const temaLimpio = f.tema && f.tema.trim() !== '' ? f.tema : null;
        const reqLimpios = f.requerimientos && f.requerimientos.trim() !== '' ? f.requerimientos : null;

        const payload = {
            actividad: f.actividad,
            maestro: f.maestro,
            asignatura: esClase.value ? f.asignatura : null, 
            sala: f.sala,
            tema: temaLimpio,
            requerimientos: reqLimpios,
            inicio: `${f.fecha}T${f.inicio}:00`,
            fin: `${f.fecha}T${f.fin}:00`
        };

        await ApiService.crearReserva(payload);
        
        mensajeExito.value = "¡Reserva creada con éxito!";
        window.scrollTo(0,0);
        
        nuevaReserva.value.inicio = ''; 
        nuevaReserva.value.fin = '';
        nuevaReserva.value.tema = ''; 
        nuevaReserva.value.requerimientos = ''; 
        nuevaReserva.value.sala = null;
        
        await cargarDatos();
    } catch(e) {
        window.scrollTo(0,0); 
        if (e.response && e.response.data) {
            const data = e.response.data;
            if (data.detail) error.value = data.detail;
            else if (data.non_field_errors) error.value = data.non_field_errors[0];
            else {
                const primerCampo = Object.keys(data)[0];
                const mensaje = Array.isArray(data[primerCampo]) ? data[primerCampo][0] : data[primerCampo];
                error.value = `${primerCampo.toUpperCase()}: ${mensaje}`;
            }
        } else {
            error.value = "Error de conexión o servidor no responde.";
        }
    } finally {
        enviando.value = false;
    }
}

async function cancelar(id, horarioDesc) {
    if(!confirm(`¿Estás seguro de cancelar la reserva de ${horarioDesc}?`)) return;
    
    try {
        await ApiService.eliminarReserva(id);
        mensajeExito.value = "Reserva eliminada con éxito.";
        await cargarDatos();
    } catch(e) {
        const status = e.response?.status;
        if(status === 403) alert("No tienes permiso para borrar esta reserva.");
        else alert("Error del servidor al intentar borrar.");
    }
}

// ==========================================
// 6. CICLO DE VIDA (Hooks y Watchers)
// ==========================================

onMounted(() => {
    cargarDatos();
    conectar(); 
});

watch(() => nuevaReserva.value.fecha, () => {
    cargarDatos();
});
</script>

<template>
  <div class="container-fluid px-4 py-4">

    <HeaderInstitucional 
        titulo="Reservar Espacio" 
        subtitulo="Programa actividades y asigna recursos físicos a las asignaturas."
        icono="bi-calendar-plus"
    />

    <div v-if="error" class="alert alert-danger shadow-sm border-0 d-flex align-items-center rounded-3">
        <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ error }}
    </div>
    <div v-if="mensajeExito" class="alert alert-success shadow-sm border-0 d-flex align-items-center rounded-3">
        <i class="bi bi-check-circle-fill me-2"></i> {{ mensajeExito }}
    </div>

    <div class="row">
        <div class="col-lg-4 mb-4">
            <div class="card shadow-sm border-0 h-100 rounded-3">
                <div class="card-body p-4">
                    <form @submit.prevent="crearReserva">
                        
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-muted">FECHA</label>
                            <input type="date" class="form-control" v-model="nuevaReserva.fecha" :min="HOY_STR" @change="cargarDatos" required>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-muted">MAESTRO</label>
                            <select v-if="isSuperUser" class="form-select" v-model="nuevaReserva.maestro">
                                <option :value="null">Seleccionar...</option>
                                <option v-for="m in maestros" :key="m.id" :value="m.id || m.matricula_m">
                                    {{ m.nombre }} {{ m.apellido_p }}
                                </option>
                            </select>
                            <div v-else class="input-group">
                                <span class="input-group-text bg-light border-light text-primary"><i class="bi bi-person-fill"></i></span>
                                <input type="text" class="form-control bg-light border-light" :value="nombreUsuarioLogueado" disabled readonly>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-bold text-muted">ACTIVIDAD</label>
                            <select class="form-select" v-model="nuevaReserva.actividad" @change="limpiarAsignaturaSiEsEvento">
                                <option :value="null">Seleccionar...</option>
                                <option v-for="act in actividades" :key="act.id" :value="act.id">{{ act.nombre_actividad }}</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-bold text-muted">ASIGNATURA</label>
                            <select class="form-select" v-model="nuevaReserva.asignatura" :disabled="!esClase" :class="{'bg-light text-muted': !esClase}">
                                <option :value="null">{{ esClase ? 'Seleccionar...' : 'No aplica para esta actividad' }}</option>
                                <option v-for="a in asignaturas" :key="a.id" :value="a.id || a.clave_asignatura">{{ a.nombre_asignatura }}</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-bold text-muted">EDIFICIO</label>
                            <select class="form-select" v-model="nuevaReserva.edificio" @change="nuevaReserva.sala = null">
                                <option :value="null">Seleccionar...</option>
                                <option v-for="ed in edificios" :key="ed.nombre_edificio" :value="ed.nombre_edificio">{{ ed.nombre_edificio }}</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-bold text-muted">SALA</label>
                            <select class="form-select" v-model="nuevaReserva.sala" :disabled="!nuevaReserva.edificio" :class="{'bg-light text-muted': !nuevaReserva.edificio}">
                                <option :value="null">{{ nuevaReserva.edificio ? 'Seleccionar...' : 'Primero elige un edificio' }}</option>
                                <option v-for="s in salasFiltradas" :key="s.clave_sala" :value="s.id || s.clave_sala">{{ s.nombre_sala }}</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-bold text-muted">Nombre de la actividad <span class="fw-light">(Opc)</span></label>
                            <input type="text" class="form-control" v-model="nuevaReserva.tema" placeholder="">
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-bold text-muted">REQUERIMIENTOS ESPECIALES <span class="fw-light">(Opc)</span></label>
                            <textarea class="form-control" v-model="nuevaReserva.requerimientos" rows="2" placeholder="Ej. Proyector, micrófonos..."></textarea>
                        </div>

                        <div v-if="horarioVencidoHoy" class="alert alert-warning py-2 small d-flex align-items-center mb-3 shadow-sm border-0">
                            <i class="bi bi-clock-history me-2 fs-5"></i>
                            <span>El horario para apartar salas el día de hoy ha concluido. Por favor, elige una fecha futura.</span>
                        </div>

                        <div class="row g-2">
                            <div class="col-6">
                                <label class="form-label small fw-bold text-muted">INICIO</label>
                                <select class="form-select" v-model="nuevaReserva.inicio" :disabled="horarioVencidoHoy" :class="{'bg-light text-muted': horarioVencidoHoy}">
                                    <option v-for="h in opcionesInicio" :key="h" :value="h">{{ h }}</option>
                                </select>
                            </div>
                            <div class="col-6">
                                <label class="form-label small fw-bold text-muted">FIN</label>
                                <select class="form-select" v-model="nuevaReserva.fin" :disabled="horarioVencidoHoy" :class="{'bg-light text-muted': horarioVencidoHoy}">
                                    <option v-for="h in opcionesFin" :key="h" :value="h">{{ h }}</option>
                                </select>
                            </div>
                        </div>

                        <button class="btn btn-primary w-100 mt-4 py-2 fw-bold shadow-sm" :disabled="enviando || horarioVencidoHoy">
                            <span v-if="enviando" class="spinner-border spinner-border-sm me-2"></span>
                            {{ enviando ? 'Reservando...' : 'Confirmar Reserva' }}
                        </button>
                    </form>
                </div>
            </div>
        </div>

        <div class="col-lg-8">
            <div v-if="!nuevaReserva.edificio" class="d-flex flex-column align-items-center justify-content-center h-100 bg-white rounded-3 shadow-sm border border-dashed border-secondary p-5 text-muted">
                <i class="bi bi-building fs-1 mb-3 opacity-50"></i>
                <h5 class="fw-bold text-dark">Selecciona un Edificio</h5>
                <p class="small text-center max-w-75">El mapa de ocupación de las salas aparecerá aquí una vez que elijas una ubicación en el formulario de la izquierda.</p>
            </div>
            
            <div v-else class="row g-3">
                <div v-for="sala in estadoSalas" :key="sala.id" class="col-md-6">
                    <div class="card h-100 shadow-sm border-0 rounded-3" :class="{'bg-light': !sala.ocupado}">
                        <div class="card-body d-flex flex-column p-4">
                            
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <div>
                                    <h6 class="fw-bold mb-0 text-dark">{{ sala.nombre }}</h6>
                                </div>
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
                                    <li v-for="res in sala.reservas" :key="res.id" class="list-group-item bg-transparent px-0 py-2 d-flex flex-column border-bottom border-light">
                                        
                                        <div class="d-flex justify-content-between align-items-center mb-1">
                                            <div class="fw-semibold text-dark">
                                                <i class="bi bi-clock me-1 text-muted"></i> {{ res.inicioFmt }} - {{ res.finFmt }}
                                            </div>
                                        </div>
                                        
                                        <div class="text-secondary" style="font-size: 0.9em;">
                                            <div class="fw-bold text-dark">{{ res.maestro }}</div>
                                            <div>
                                                <span class="badge bg-secondary text-white me-1">{{ res.actividad }}</span> 
                                                <span class="fst-italic">{{ res.detalleActividad }}</span>
                                            </div>
                                        </div>

                                        <div v-if="isSuperUser && res.requerimientos" class="mt-2 p-2 bg-warning-subtle border border-warning rounded" style="font-size: 0.85em;">
                                            <span class="fw-bold text-dark-emphasis"><i class="bi bi-tools me-1"></i>Req:</span> 
                                            <span class="text-dark">{{ res.requerimientos }}</span>
                                        </div>

                                    </li>
                                </ul>
                            </div>

                            <div class="d-flex gap-2 mt-auto pt-3 border-top border-light">
                                <button 
                                    v-if="sala.idCancelable"
                                    @click="cancelar(sala.idCancelable, sala.descCancelable)"
                                    class="btn btn-sm btn-outline-danger flex-grow-1 fw-semibold shadow-sm"
                                    title="Cancelar reserva"
                                >
                                    <i class="bi bi-trash me-1"></i> Cancelar
                                </button>

                                <button 
                                    @click="seleccionar(sala.id)"
                                    class="btn btn-sm btn-outline-primary fw-semibold shadow-sm"
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
</template>

<style scoped>
.btn-sm { font-size: 0.85rem; }
.border-dashed { border-style: dashed !important; border-width: 2px !important; }
.max-w-75 { max-width: 75%; }
</style>