<script setup>
import { ref, onMounted, computed } from 'vue';
import ApiService from '@/services/ApiService.js'; 
import ReportesService from '@/services/ReporteServices.js';

import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Bar, Pie } from 'vue-chartjs';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const vistaActual = ref('historial'); 
const historial = ref([]);
const cargandoHistorial = ref(false);
const filtrosHistorial = ref({ tipo: '', anio: new Date().getFullYear() });

const reservas = ref([]);
const salas = ref([]);
const cargando = ref(false);
const cargandoAccion = ref(false); 
const error = ref(null);
const mensajeExito = ref(null);

const fechaInicio = ref('');
const fechaFin = ref('');
const salaSeleccionada = ref('');
const tipoReporteGenerado = ref('GENERAL'); 

const stats = ref({
    salaTop: 'N/A',
    maestroTop: 'N/A',
    materiaTop: 'N/A',
    tasaOcupacion: 0,
    horasTotales: 0,
    diaPico: 'N/A'
});

const chartDataSalas = ref({ labels: [], datasets: [] });
const chartDataDias = ref({ labels: [], datasets: [] });
const chartOptions = { responsive: true, maintainAspectRatio: false };

onMounted(async () => {
  await cargarHistorial();
  try {
    const res = await ApiService.obtenerSalas();
    salas.value = res.data || res;
    configurarFechasDefault();
  } catch (err) {
    console.error("Error al cargar salas:", err);
  }
});

function configurarFechasDefault() {
    const hoy = new Date();
    const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
    const ultimoDia = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0);
    const offset = primerDia.getTimezoneOffset() * 60000;
    fechaInicio.value = new Date(primerDia - offset).toISOString().split('T')[0];
    fechaFin.value = new Date(ultimoDia - offset).toISOString().split('T')[0];
}

async function cargarHistorial() {
    cargandoHistorial.value = true;
    try {
        const res = await ReportesService.obtenerReportes(filtrosHistorial.value);
        historial.value = res.data;
    } catch (e) {
        console.error("Error cargando historial:", e);
    } finally {
        cargandoHistorial.value = false;
    }
}

async function eliminarDelHistorial(id) {
    if(!confirm('¿Estás seguro de eliminar este reporte permanentemente?')) return;
    try {
        await ReportesService.eliminarReporte(id);
        await cargarHistorial();
    } catch (e) {
        alert("Error al eliminar");
    }
}

function descargarArchivo(url) {
    if(url) window.open(url, '_blank');
}

async function generarAnalisisEnVivo() {
  cargando.value = true;
  error.value = null;
  reservas.value = [];

  try {
    const response = await ApiService.obtenerReservas();
    const todosLosDatos = response.data || response;

    if (!Array.isArray(todosLosDatos)) throw new Error("Datos inválidos");

    const fInicio = fechaInicio.value; 
    const fFin = fechaFin.value;

    reservas.value = todosLosDatos.filter(r => {
        const fechaReserva = r.inicio ? r.inicio.split('T')[0] : '';
        const enRango = fechaReserva >= fInicio && fechaReserva <= fFin;
        
        let coincideSala = true;
        if (salaSeleccionada.value) {
            const idSalaReserva = (typeof r.sala === 'object') ? r.sala.id : r.sala;
            const claveSalaReserva = (typeof r.sala === 'object') ? r.sala.clave_sala : null;
            
            coincideSala = String(idSalaReserva) === String(salaSeleccionada.value) || 
                           String(claveSalaReserva) === String(salaSeleccionada.value);
        }
        return enRango && coincideSala;
    });
    
    calcularEstadisticas();
    prepararGraficos();

  } catch (err) {
    error.value = 'Error al analizar datos.';
    console.error(err);
  } finally {
    cargando.value = false;
  }
}

function calcularEstadisticas() {
    if (reservas.value.length === 0) { resetStats(); return; }
    const conteoSalas = {};
    let totalHoras = 0;
    reservas.value.forEach(r => {
        const s = (typeof r.sala === 'object') ? (r.sala.nombre_sala || r.sala.nombre) : (r.sala || 'Desconocido');
        conteoSalas[s] = (conteoSalas[s] || 0) + 1;
        const inicio = new Date(r.inicio);
        const fin = new Date(r.fin);
        const duracion = (fin - inicio) / (1000 * 60 * 60); 
        if (!isNaN(duracion)) totalHoras += duracion;
    });
    stats.value.salaTop = getKeyWithMaxVal(conteoSalas);
    stats.value.horasTotales = totalHoras.toFixed(1);
}

function getKeyWithMaxVal(obj) {
    const keys = Object.keys(obj);
    if (keys.length === 0) return 'N/A';
    return keys.reduce((a, b) => obj[a] > obj[b] ? a : b);
}

function resetStats() {
    stats.value = { salaTop: 'N/A', maestroTop: 'N/A', materiaTop: 'N/A', tasaOcupacion: '0%', horasTotales: 0, diaPico: 'N/A' };
    chartDataSalas.value = { labels: [], datasets: [] };
    chartDataDias.value = { labels: [], datasets: [] };
}

function prepararGraficos() {
    if (reservas.value.length === 0) return;
    const conteoSalas = {};
    reservas.value.forEach(r => {
        const s = (typeof r.sala === 'object') ? (r.sala.nombre_sala || r.sala.nombre) : (r.sala || 'Desconocido');
        conteoSalas[s] = (conteoSalas[s] || 0) + 1;
    });
    chartDataSalas.value = {
        labels: Object.keys(conteoSalas),
        datasets: [{ label: 'Reservas', backgroundColor: '#005f86', data: Object.values(conteoSalas) }]
    };
    chartDataDias.value = { labels: [], datasets: [] }; 
}


const reporteOcupacion = computed(() => {
    const agrupado = {};
    reservas.value.forEach(r => {
        const nombreSala = (typeof r.sala === 'object') ? (r.sala.nombre_sala || r.sala.nombre) : (r.sala || 'Desconocido');
        
        if (!agrupado[nombreSala]) {
            agrupado[nombreSala] = { nombre: nombreSala, reservas: 0, horas: 0 };
        }
        
        agrupado[nombreSala].reservas += 1;
        
        const ini = new Date(r.inicio);
        const fin = new Date(r.fin);
        const diff = (fin - ini) / (1000 * 60 * 60); // Horas
        if (!isNaN(diff)) agrupado[nombreSala].horas += diff;
    });
    
    
    return Object.values(agrupado).sort((a, b) => b.horas - a.horas);
});

const reporteDocente = computed(() => {
    const agrupado = {};
    reservas.value.forEach(r => {
        const nombreMaestro = r.maestro_nombre || r.maestro || 'Desconocido';
        const materia = (typeof r.asignatura === 'object') ? r.asignatura.nombre_asignatura : r.asignatura;
        
        if (!agrupado[nombreMaestro]) {
            agrupado[nombreMaestro] = { nombre: nombreMaestro, materias: new Set(), horas: 0, reservas: 0 };
        }
        
        agrupado[nombreMaestro].reservas += 1;
        if (materia) agrupado[nombreMaestro].materias.add(materia);
        
        const ini = new Date(r.inicio);
        const fin = new Date(r.fin);
        const diff = (fin - ini) / (1000 * 60 * 60);
        if (!isNaN(diff)) agrupado[nombreMaestro].horas += diff;
    });
    
    
    return Object.values(agrupado)
        .map(item => ({
            ...item,
            materiasStr: Array.from(item.materias).join(', ') || 'Varias'
        }))
        .sort((a, b) => b.reservas - a.reservas);
});

const generarBlobPDF = async () => {
    const elemento = document.getElementById('reporte-imprimible');
    if (!elemento) return null;
    
    const canvas = await html2canvas(elemento, { scale: 2, useCORS: true });
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
    
    pdf.addImage(imgData, 'PNG', 0, 10, pdfWidth, pdfHeight);
    return pdf.output('blob'); 
};

async function guardarReporteEnSistema() {
    if (reservas.value.length === 0) return;
    if (!confirm("¿Deseas guardar este reporte en el historial del sistema?")) return;

    cargandoAccion.value = true;
    try {
        const pdfBlob = await generarBlobPDF();
        const archivoFile = new File([pdfBlob], `Reporte_${Date.now()}.pdf`, { type: "application/pdf" });
        
        const payload = {
            titulo: `Reporte ${fechaInicio.value} al ${fechaFin.value}`,
            tipo: tipoReporteGenerado.value, 
            fecha_inicio_datos: fechaInicio.value,
            fecha_fin_datos: fechaFin.value,
            archivo: archivoFile
        };
        
        await ReportesService.crearReporte(payload);
        mensajeExito.value = "Reporte guardado exitosamente en la base de datos.";
        
        setTimeout(() => {
            mensajeExito.value = null;
            vistaActual.value = 'historial';
            cargarHistorial();
        }, 2000);

    } catch (err) {
        console.error(err);
        alert("Error al guardar el reporte en el servidor.");
    } finally {
        cargandoAccion.value = false;
    }
}

const descargarPDFLocal = async () => {
    cargandoAccion.value = true;
    try {
        const blob = await generarBlobPDF();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Reporte_Local_${Date.now()}.pdf`;
        a.click();
    } finally {
        cargandoAccion.value = false;
    }
};

function formatDateTime(dateTimeString) {
  if (!dateTimeString) return 'N/A';
  const dt = new Date(dateTimeString);
  return dt.toLocaleDateString('es-MX') + ' ' + dt.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
}
</script>

<template>
  <div class="container-fluid p-4">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2 class="text-dark fw-bold mb-0">
                <i class="bi bi-folder2-open text-primary me-2"></i>Gestión de Reportes
            </h2>
        </div>
        
        <div class="btn-group">
            <button 
                @click="vistaActual = 'historial'" 
                class="btn" 
                :class="vistaActual === 'historial' ? 'btn-primary' : 'btn-outline-primary'">
                <i class="bi bi-clock-history me-1"></i> Historial
            </button>
            <button 
                @click="vistaActual = 'nuevo'" 
                class="btn" 
                :class="vistaActual === 'nuevo' ? 'btn-primary' : 'btn-outline-primary'">
                <i class="bi bi-plus-circle me-1"></i> Nuevo Análisis
            </button>
        </div>
    </div>

    <div v-if="vistaActual === 'historial'">
        
        <div class="card shadow-sm border-0 mb-4">
            <div class="card-body bg-light rounded d-flex gap-3 align-items-end">
                <div class="flex-grow-1">
                    <label class="form-label small fw-bold text-muted">Filtrar por Tipo</label>
                    <select class="form-select" v-model="filtrosHistorial.tipo" @change="cargarHistorial">
                        <option value="">Todos</option>
                        <option value="GENERAL">General Mensual</option>
                        <option value="OCUPACION">Ocupación</option>
                        <option value="DOCENTE">Actividad Docente</option>
                    </select>
                </div>
                <div class="flex-grow-1">
                    <label class="form-label small fw-bold text-muted">Filtrar por Año</label>
                    <input type="number" class="form-control" v-model="filtrosHistorial.anio" @change="cargarHistorial">
                </div>
                <button class="btn btn-secondary" @click="cargarHistorial">
                    <i class="bi bi-arrow-clockwise"></i> Actualizar
                </button>
            </div>
        </div>

        <div class="card shadow-sm border-0">
            <div v-if="cargandoHistorial" class="p-5 text-center">
                <div class="spinner-border text-primary"></div>
            </div>

            <div v-else-if="historial.length === 0" class="p-5 text-center text-muted">
                <i class="bi bi-inbox fs-1"></i>
                <p class="mt-2">No hay reportes generados aún.</p>
            </div>

            <div v-else class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Título</th>
                            <th>Tipo</th>
                            <th>División</th>
                            <th>Generado Por</th>
                            <th>Fecha</th>
                            <th class="text-end">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="rep in historial" :key="rep.id">
                            <td class="fw-bold">{{ rep.titulo }}</td>
                            <td>
                                <span class="badge bg-info text-dark">{{ rep.tipo_legible }}</span>
                            </td>
                            <td>{{ rep.division_nombre }}</td>
                            <td>{{ rep.creado_por }}</td>
                            <td>{{ new Date(rep.fecha_generacion).toLocaleDateString() }}</td>
                            
                            <td class="text-end">
                                <div class="d-flex justify-content-end gap-2">
                                    <a 
                                        v-if="rep.archivo" 
                                        :href="rep.archivo" 
                                        target="_blank"
                                        class="btn btn-outline-primary d-flex align-items-center gap-2"
                                        title="Descargar PDF"
                                    >
                                        <i class="bi bi-file-earmark-pdf-fill fs-5"></i>
                                        <span class="d-none d-md-inline fw-semibold">PDF</span>
                                    </a>

                                    <button 
                                        @click="eliminarDelHistorial(rep.id)" 
                                        class="btn btn-outline-danger d-flex align-items-center gap-2"
                                        title="Eliminar del historial"
                                    >
                                        <i class="bi bi-trash3-fill fs-5"></i>
                                        <span class="d-none d-md-inline fw-semibold">Eliminar</span>
                                    </button>
                                </div>
                            </td>
                            </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div v-else>
        
        <div v-if="mensajeExito" class="alert alert-success">{{ mensajeExito }}</div>

        <div class="card mb-4 shadow-sm border-0">
            <div class="card-body bg-light rounded">
                <div class="row g-3 align-items-end">
                    <div class="col-md-3">
                        <label class="form-label small fw-bold text-muted">Rango Inicio</label>
                        <input type="date" v-model="fechaInicio" class="form-control">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small fw-bold text-muted">Rango Fin</label>
                        <input type="date" v-model="fechaFin" class="form-control">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small fw-bold text-muted">Categoría de Reporte</label>
                        <select v-model="tipoReporteGenerado" class="form-select border-primary fw-bold text-muted">
                            <option value="GENERAL">General (Bitácora)</option>
                            <option value="OCUPACION">Ocupación (Por Sala)</option>
                            <option value="DOCENTE">Productividad Docente</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <button @click="generarAnalisisEnVivo" class="btn btn-primary w-100" :disabled="cargando">
                            <span v-if="cargando" class="spinner-border spinner-border-sm me-2"></span>
                            {{ cargando ? 'Procesando...' : 'Analizar Datos' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-if="reservas.length > 0" class="fade-in">
            
            <div class="d-flex justify-content-end gap-2 mb-3">
                <button @click="descargarPDFLocal" class="btn btn-outline-secondary btn-sm" :disabled="cargandoAccion">
                    <i class="bi bi-eye"></i> Solo Descargar PDF
                </button>
                <button @click="guardarReporteEnSistema" class="btn btn-success" :disabled="cargandoAccion">
                    <span v-if="cargandoAccion" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-cloud-upload me-1"></i> Guardar en Historial
                </button>
            </div>

            <div id="reporte-imprimible" class="bg-white p-4 rounded border">
                
                <div class="text-center mb-4">
                    <h4 class="fw-bold text-uppercase">
                        {{ tipoReporteGenerado === 'GENERAL' ? 'Reporte General de Actividad' : (tipoReporteGenerado === 'OCUPACION' ? 'Reporte de Ocupación de Salas' : 'Reporte de Productividad Docente') }}
                    </h4>
                    <p class="text-muted">Período: {{ fechaInicio }} al {{ fechaFin }}</p>
                </div>

                <div class="row g-4 mb-4">
                    <div class="col-md-3">
                        <div class="card h-100 border-start border-4 border-primary shadow-sm">
                            <div class="card-body">
                                <small class="text-muted text-uppercase">Sala Más Usada</small>
                                <h4 class="fw-bold text-primary">{{ stats.salaTop }}</h4>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card h-100 border-start border-4 border-info shadow-sm">
                            <div class="card-body">
                                <small class="text-muted text-uppercase">Horas Totales</small>
                                <h4 class="fw-bold text-info">{{ stats.horasTotales }} hrs</h4>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 d-flex align-items-center justify-content-end text-muted small">
                        Generado el: {{ new Date().toLocaleDateString() }}
                    </div>
                </div>

                <div class="row mb-5">
                    <div class="col-12">
                        <div class="card border-0">
                            <div class="card-body" style="height: 250px;">
                                <Bar :data="chartDataSalas" :options="chartOptions" />
                            </div>
                        </div>
                    </div>
                </div>
                
                <div v-if="tipoReporteGenerado === 'GENERAL'">
                    <h5 class="fw-bold border-bottom pb-2 mb-3">Bitácora de Reservas</h5>
                    <table class="table table-sm table-striped small">
                        <thead class="table-dark">
                            <tr><th>Fecha</th><th>Sala</th><th>Maestro</th><th>Horario</th></tr>
                        </thead>
                        <tbody>
                            <tr v-for="r in reservas.slice(0, 50)" :key="r.id">
                                <td>{{ new Date(r.inicio).toLocaleDateString() }}</td>
                                <td>{{ (typeof r.sala === 'object') ? r.sala.nombre_sala : r.sala }}</td>
                                <td>{{ r.maestro_nombre || r.maestro }}</td>
                                <td>{{ new Date(r.inicio).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }} - {{ new Date(r.fin).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</td>
                            </tr>
                        </tbody>
                    </table>
                    <p v-if="reservas.length > 50" class="text-center text-muted fst-italic mt-2">
                        ... visualizando los primeros 50 de {{ reservas.length }} registros.
                    </p>
                </div>

                <div v-else-if="tipoReporteGenerado === 'OCUPACION'">
                    <h5 class="fw-bold border-bottom pb-2 mb-3">Detalle de Uso por Sala</h5>
                    <table class="table table-striped table-hover align-middle">
                        <thead class="table-dark">
                            <tr>
                                <th>Sala</th>
                                <th class="text-center">Reservas Totales</th>
                                <th class="text-center">Horas Acumuladas</th>
                                <th class="text-center">Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in reporteOcupacion" :key="item.nombre">
                                <td class="fw-bold">{{ item.nombre }}</td>
                                <td class="text-center">{{ item.reservas }}</td>
                                <td class="text-center fw-bold text-primary">{{ item.horas.toFixed(1) }} h</td>
                                <td class="text-center">
                                    <span v-if="item.horas > 20" class="badge bg-success">Alto Uso</span>
                                    <span v-else-if="item.horas > 5" class="badge bg-warning text-dark">Medio</span>
                                    <span v-else class="badge bg-secondary">Bajo</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div v-else-if="tipoReporteGenerado === 'DOCENTE'">
                    <h5 class="fw-bold border-bottom pb-2 mb-3">Productividad por Docente</h5>
                    <table class="table table-striped table-hover align-middle">
                        <thead class="table-dark">
                            <tr>
                                <th>Docente</th>
                                <th>Asignaturas Impartidas</th>
                                <th class="text-center">Sesiones</th>
                                <th class="text-center">Horas Totales</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in reporteDocente" :key="item.nombre">
                                <td class="fw-bold text-primary">{{ item.nombre }}</td>
                                <td class="small text-muted">{{ item.materiasStr }}</td>
                                <td class="text-center">{{ item.reservas }}</td>
                                <td class="text-center fw-bold">{{ item.horas.toFixed(1) }} h</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.fade-in { animation: fadeIn 0.5s; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>