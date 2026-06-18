<script setup>
/**
 * @file ReportesView.vue
 * @description Módulo de Inteligencia de Negocios (BI) y Auditoría.
 * Permite el minado de datos de las reservas para calcular KPIs de infraestructura,
 * renderizar gráficas interactivas y exportar bitácoras formales en formato PDF.
 */

// ==========================================
// 1. IMPORTS
// ==========================================
import { ref, onMounted, computed } from 'vue';
import ApiService from '@/services/ApiService.js'; 
import ReportesService from '@/services/ReporteServices.js';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable'; 
import HeaderInstitucional from '@/components/HeaderInstitucional.vue';

// Dependencias de Gráficos (Chart.js)
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Pie } from 'vue-chartjs';

// ==========================================
// 2. CONFIGURACIÓN Y COMPOSABLES
// ==========================================
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const HORARIO_APERTURA = 8;
const HORARIO_CIERRE = 16;

const chartOptions = { 
    responsive: true, 
    maintainAspectRatio: false,
    devicePixelRatio: 4 // Fuerza renderizado en Ultra Alta Resolución para el PDF
};

// ==========================================
// 3. ESTADO REACTIVO (Variables)
// ==========================================

// Estado General de la Vista
const vistaActual = ref('historial'); // 'historial' o 'nuevo'
const cargando = ref(false);
const cargandoAccion = ref(false); 
const error = ref(null);
const mensajeExito = ref(null);

// Datos del Historial (Backend)
const historial = ref([]);
const cargandoHistorial = ref(false);
const filtrosHistorial = ref({ tipo: '', anio: new Date().getFullYear() });

// Datos del Análisis en Vivo
const reservas = ref([]);
const salas = ref([]);
const fechaInicio = ref('');
const fechaFin = ref('');
const salaSeleccionada = ref('');
const tipoReporteGenerado = ref('GENERAL'); 

// Indicadores Clave de Rendimiento (KPIs)
const stats = ref({
    salaTop: 'N/A',
    maestroTop: 'N/A',
    totalReservas: 0,
    horasTotales: 0,
    aprovechamiento: '0%' 
});

// Referencias del DOM para exportación PDF
const barChartRef = ref(null);
const pieChartRef = ref(null);
const picoChartRef = ref(null);
const equipChartRef = ref(null);

// Modelos de Datos para Chart.js
const chartDataSalas = ref({ labels: [], datasets: [] });
const chartDataActividades = ref({ labels: [], datasets: [] });
const chartDataHorasPico = ref({ labels: [], datasets: [] }); 
const chartDataEquipamiento = ref({ labels: [], datasets: [] }); 

// ==========================================
// 4. PROPIEDADES COMPUTADAS
// ==========================================

/**
 * Agrupa y suma el tiempo de uso por cada espacio físico para el reporte de ocupación.
 */
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
        const diff = (fin - ini) / (1000 * 60 * 60);
        if (!isNaN(diff)) agrupado[nombreSala].horas += diff;
    });
    return Object.values(agrupado).sort((a, b) => b.horas - a.horas);
});

/**
 * Agrupa la carga horaria y materias vinculadas a cada catedrático.
 */
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

// ==========================================
// 5. FUNCIONES Y MÉTODOS
// ==========================================

/**
 * Establece el rango de fechas predeterminado al mes en curso (Día 1 al Último Día).
 */
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

function getKeyWithMaxVal(obj) {
    const keys = Object.keys(obj);
    if (keys.length === 0) return 'N/A';
    return keys.reduce((a, b) => obj[a] > obj[b] ? a : b);
}

function resetStats() {
    stats.value = { salaTop: 'N/A', maestroTop: 'N/A', totalReservas: 0, horasTotales: 0, aprovechamiento: '0%' };
    chartDataSalas.value = { labels: [], datasets: [] };
    chartDataActividades.value = { labels: [], datasets: [] };
    chartDataHorasPico.value = { labels: [], datasets: [] };
    chartDataEquipamiento.value = { labels: [], datasets: [] };
}

/**
 * Extrae y procesa los datos puros para calcular los 5 KPIs estratégicos
 * incluyendo la fórmula de optimización de infraestructura.
 */
function calcularEstadisticas() {
    if (reservas.value.length === 0) { resetStats(); return; }
    
    const conteoSalas = {};
    const conteoMaestros = {};
    let totalHoras = 0;
    
    reservas.value.forEach(r => {
        const s = (typeof r.sala === 'object') ? (r.sala.nombre_sala || r.sala.nombre) : (r.sala || 'Desconocido');
        conteoSalas[s] = (conteoSalas[s] || 0) + 1;
        
        const m = r.maestro_nombre || r.maestro || 'Desconocido';
        conteoMaestros[m] = (conteoMaestros[m] || 0) + 1;
        
        const inicio = new Date(r.inicio);
        const fin = new Date(r.fin);
        const duracion = (fin - inicio) / (1000 * 60 * 60); 
        if (!isNaN(duracion)) totalHoras += duracion;
    });
    
    stats.value.salaTop = getKeyWithMaxVal(conteoSalas);
    stats.value.maestroTop = getKeyWithMaxVal(conteoMaestros);
    stats.value.totalReservas = reservas.value.length;
    stats.value.horasTotales = totalHoras.toFixed(1);

    // Matemáticas de optimización de infraestructura
    const iniRango = new Date(fechaInicio.value);
    const finRango = new Date(fechaFin.value);
    const dias = Math.max(1, Math.ceil((finRango - iniRango) / (1000 * 60 * 60 * 24)));
    const salasTotales = salas.value.length > 0 ? salas.value.length : Object.keys(conteoSalas).length;
    
    const horasPosibles = dias * (HORARIO_CIERRE - HORARIO_APERTURA) * salasTotales; 
    const porcentaje = horasPosibles > 0 ? ((totalHoras / horasPosibles) * 100).toFixed(1) : 0;
    stats.value.aprovechamiento = `${porcentaje}%`;
}

/**
 * Alimenta los modelos reactivos de Chart.js mediante conteos de frecuencia
 * y análisis de texto (Minería de datos en "Requerimientos Especiales").
 */
function prepararGraficos() {
    if (reservas.value.length === 0) return;
    
    const conteoSalas = {};
    const conteoActividades = {};
    const conteoHoras = {};
    
    const palabrasClaveEquipos = ['proyector', 'bocina', 'audio', 'hdmi', 'micrófono', 'microfono', 'extensión', 'internet', 'clima'];
    const conteoEquipos = {};
    
    reservas.value.forEach(r => {
        const s = (typeof r.sala === 'object') ? (r.sala.nombre_sala || r.sala.nombre) : (r.sala || 'Desconocido');
        conteoSalas[s] = (conteoSalas[s] || 0) + 1;
        
        const act = r.actividad || 'Actividad General';
        conteoActividades[act] = (conteoActividades[act] || 0) + 1;

        // Minería: Extracción de Horas Pico
        const hora = new Date(r.inicio).getHours();
        const etiquetaHora = `${String(hora).padStart(2, '0')}:00`;
        conteoHoras[etiquetaHora] = (conteoHoras[etiquetaHora] || 0) + 1;

        // Minería: Búsqueda de Requerimientos
        if (r.requerimientos && typeof r.requerimientos === 'string') {
            const reqTexto = r.requerimientos.toLowerCase();
            palabrasClaveEquipos.forEach(equipo => {
                if (reqTexto.includes(equipo)) {
                    const nombreLimpio = equipo === 'microfono' ? 'micrófono' : equipo;
                    conteoEquipos[nombreLimpio] = (conteoEquipos[nombreLimpio] || 0) + 1;
                }
            });
        }
    });
    
    const horasOrdenadas = Object.keys(conteoHoras).sort();
    
    chartDataSalas.value = {
        labels: Object.keys(conteoSalas),
        datasets: [{ label: 'Horas de Uso por Sala', backgroundColor: '#005f86', borderRadius: 6, data: Object.values(conteoSalas) }]
    };
    
    chartDataActividades.value = {
        labels: Object.keys(conteoActividades),
        datasets: [{ backgroundColor: ['#005f86', '#2ca02c', '#ff7f0e', '#d62728'], borderWidth: 2, data: Object.values(conteoActividades) }]
    };

    chartDataHorasPico.value = {
        labels: horasOrdenadas,
        datasets: [{ label: 'Reservas Iniciadas', backgroundColor: '#ff7f0e', borderRadius: 4, data: horasOrdenadas.map(h => conteoHoras[h]) }]
    };

    const equiposOrdenados = Object.keys(conteoEquipos).sort((a, b) => conteoEquipos[b] - conteoEquipos[a]);
    chartDataEquipamiento.value = {
        labels: equiposOrdenados.map(e => e.charAt(0).toUpperCase() + e.slice(1)), 
        datasets: [{ label: 'Veces Solicitado', backgroundColor: '#2ca02c', borderRadius: 4, data: equiposOrdenados.map(e => conteoEquipos[e]) }]
    };
}

/**
 * Descarga las reservas masivas del backend y ejecuta el motor de 
 * filtrado local basado en el rango de fechas seleccionado.
 */
async function generarAnalisisEnVivo() {
  cargando.value = true;
  error.value = null;
  reservas.value = [];

  try {
    const response = await ApiService.obtenerReservas();
    const datosCrudos = response.data || response;

    if (!Array.isArray(datosCrudos)) throw new Error("Datos inválidos devueltos por el servidor.");

    const inicioRango = new Date(fechaInicio.value + "T00:00:00");
    const finRango = new Date(fechaFin.value + "T23:59:59");

    const datosFiltrados = datosCrudos.filter(r => {
        if (!r.inicio) return false;
        const fechaReserva = new Date(r.inicio);
        let entraEnFecha = fechaReserva >= inicioRango && fechaReserva <= finRango;
        
        let entraEnSala = true;
        if (salaSeleccionada.value) {
            const sNombre = typeof r.sala === 'object' ? (r.sala.nombre_sala || r.sala.nombre) : r.sala;
            entraEnSala = String(sNombre) === String(salaSeleccionada.value);
        }
        return entraEnFecha && entraEnSala;
    });

    if (datosFiltrados.length === 0) {
        error.value = "No se encontraron actividades registradas en este rango de fechas.";
        resetStats();
        return;
    }

    reservas.value = datosFiltrados;
    calcularEstadisticas();
    prepararGraficos();

  } catch (err) {
    error.value = 'Error al procesar el análisis de datos. Verifique la conexión.';
    console.error(err);
  } finally {
    cargando.value = false;
  }
}

/**
 * Ensambla el documento PDF oficial. Dibuja texto, extrae imágenes Base64 
 * de los canvas de Chart.js y genera la tabla vectorial auto-paginable.
 */
const generarBlobPDF = async () => {
    const doc = new jsPDF('p', 'mm', 'a4');
    const colorPrimario = [0, 95, 134]; 
    let posY = 20; 

    // Encabezados
    doc.setFontSize(16);
    doc.setTextColor(...colorPrimario);
    doc.setFont('helvetica', 'bold');
    
    const tituloReporte = tipoReporteGenerado.value === 'GENERAL' ? 'REPORTE GENERAL DE ACTIVIDAD' : 
                          (tipoReporteGenerado.value === 'OCUPACION' ? 'REPORTE DE OCUPACIÓN DE SALAS' : 'REPORTE DE PRODUCTIVIDAD DOCENTE');
    doc.text(tituloReporte, 14, posY);
    
    posY += 8;
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.setFont('helvetica', 'normal');
    doc.text(`Período analizado: ${fechaInicio.value} al ${fechaFin.value}`, 14, posY);
    doc.text(`Fecha de emisión: ${new Date().toLocaleDateString('es-MX')}`, 140, posY);
    
    posY += 15;

    // Inyección de KPIs
    doc.setFontSize(11);
    doc.setTextColor(0, 0, 0);
    doc.text(`Total de Reservas: ${stats.value.totalReservas}`, 14, posY);
    doc.text(`Horas de Uso: ${stats.value.horasTotales} hrs`, 70, posY);
    doc.text(`Sala Top: ${stats.value.salaTop}`, 125, posY);
    
    posY += 8; 
    doc.text(`Docente Top: ${stats.value.maestroTop}`, 14, posY);
    doc.text(`Aprovechamiento Global: ${stats.value.aprovechamiento}`, 125, posY);
    
    posY += 15; 

    // Extracción e inyección de Gráficas HD
    if (barChartRef.value && barChartRef.value.chart && pieChartRef.value && pieChartRef.value.chart) {
        const barImgBase64 = barChartRef.value.chart.toBase64Image();
        const pieImgBase64 = pieChartRef.value.chart.toBase64Image();
        
        doc.addImage(barImgBase64, 'PNG', 14, posY, 110, 60);
        doc.addImage(pieImgBase64, 'PNG', 135, posY, 60, 60);
        
        if (picoChartRef.value && picoChartRef.value.chart && equipChartRef.value && equipChartRef.value.chart) {
            const picoImgBase64 = picoChartRef.value.chart.toBase64Image();
            const equipImgBase64 = equipChartRef.value.chart.toBase64Image();
            
            doc.addImage(picoImgBase64, 'PNG', 14, posY + 70, 110, 60);
            doc.addImage(equipImgBase64, 'PNG', 135, posY + 70, 60, 60);
            posY += 140; 
        } else {
            posY += 70; 
        }
    }

    // Configuración de Tabla Vectorial
    let columnas = [];
    let filas = [];

    if (tipoReporteGenerado.value === 'GENERAL') {
        columnas = [['Fecha', 'Sala', 'Docente', 'Horario Asignado']];
        filas = reservas.value.map(r => [
            new Date(r.inicio).toLocaleDateString('es-MX'),
            (typeof r.sala === 'object') ? (r.sala.nombre_sala || r.sala.nombre) : r.sala,
            r.maestro_nombre || r.maestro,
            `${new Date(r.inicio).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12:false})} - ${new Date(r.fin).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12:false})}`
        ]);
    } else if (tipoReporteGenerado.value === 'OCUPACION') {
        columnas = [['Identificador del Espacio', 'Sesiones Agendadas', 'Tiempo de Uso Absoluto']];
        filas = reporteOcupacion.value.map(item => [
            item.nombre,
            `${item.reservas} clases`,
            `${item.horas.toFixed(1)} hrs`
        ]);
    } else if (tipoReporteGenerado.value === 'DOCENTE') {
        columnas = [['Nombre del Catedrático', 'Materias Impartidas', 'Sesiones Totales', 'Horas de Uso']];
        filas = reporteDocente.value.map(item => [
            item.nombre,
            item.materiasStr,
            `${item.reservas} bloques`,
            `${item.horas.toFixed(1)} hrs`
        ]);
    }

    autoTable(doc, {
        startY: posY,
        head: columnas,
        body: filas,
        headStyles: { fillColor: colorPrimario, textColor: [255, 255, 255] },
        alternateRowStyles: { fillColor: [245, 245, 245] },
        styles: { fontSize: 9, cellPadding: 3 },
        margin: { left: 14, right: 14 }
    });

    return doc.output('blob');
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

// ==========================================
// 6. CICLO DE VIDA (Hooks)
// ==========================================
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
</script>

<template>
  <div class="container-fluid px-4 py-4">
    
    <HeaderInstitucional 
        titulo="Módulo de Reportes" 
        subtitulo="Monitoreo de rendimiento e indicadores clave de infraestructura."
        icono="bi-bar-chart-line-fill"
    >
        <template #acciones>
            <div class="btn-group bg-white p-1 rounded shadow-sm border border-light-subtle">
                <button 
                    @click="vistaActual = 'historial'" 
                    class="btn rounded px-3 fw-semibold transition-all btn-sm" 
                    :class="vistaActual === 'historial' ? 'btn-primary text-white shadow-sm' : 'btn-light text-secondary border-0'">
                    <i class="bi bi-clock-history me-1"></i> Historial Archivos
                </button>
                <button 
                    @click="vistaActual = 'nuevo'" 
                    class="btn rounded px-3 fw-semibold transition-all btn-sm" 
                    :class="vistaActual === 'nuevo' ? 'btn-primary text-white shadow-sm' : 'btn-light text-secondary border-0'">
                    <i class="bi bi-cpu me-1"></i> Análisis Dinámico
                </button>
            </div>
        </template>
    </HeaderInstitucional>

    <div v-if="vistaActual === 'historial'" class="fade-in">
        <div class="card shadow-sm border-0 mb-4 bg-white rounded-3">
            <div class="card-body p-4 d-flex flex-wrap gap-3 align-items-end">
                <div class="flex-grow-1" style="min-width: 200px;">
                    <label class="form-label small fw-bold text-dark-emphasis mb-1">Filtrar por Categoría</label>
                    <select class="form-select border-light-subtle" v-model="filtrosHistorial.tipo" @change="cargarHistorial">
                        <option value="">Todas las categorías</option>
                        <option value="GENERAL">General (Bitácora)</option>
                        <option value="OCUPACION">Ocupación de Espacios</option>
                        <option value="DOCENTE">Productividad Docente</option>
                    </select>
                </div>
                <div class="flex-grow-1" style="min-width: 150px;">
                    <label class="form-label small fw-bold text-dark-emphasis mb-1">Filtrar por Año</label>
                    <input type="number" class="form-control border-light-subtle" v-model="filtrosHistorial.anio" @change="cargarHistorial">
                </div>
                <button class="btn btn-outline-secondary d-flex align-items-center gap-2 fw-semibold shadow-sm" @click="cargarHistorial">
                    <i class="bi bi-arrow-clockwise"></i> Sincronizar
                </button>
            </div>
        </div>

        <div class="card shadow-sm border-0 bg-white overflow-hidden rounded-3">
            <div v-if="cargandoHistorial" class="p-5 text-center">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="text-muted mt-2 small">Consultando base de datos...</p>
            </div>

            <div v-else-if="historial.length === 0" class="p-5 text-center text-muted">
                <i class="bi bi-folder-x display-3 opacity-50 text-secondary"></i>
                <p class="mt-3 fs-5 fw-semibold text-dark">Historial vacío</p>
                <p class="text-muted small">No se han archivado reportes ejecutados en este período.</p>
            </div>

            <div v-else class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="custom-table-header">
                        <tr>
                            <th class="ps-4">Título del Documento</th>
                            <th>Tipo de Análisis</th>
                            <th>División Académica</th>
                            <th>Generado Por</th>
                            <th>Fecha Registro</th>
                            <th class="text-end pe-4">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="rep in historial" :key="rep.id" class="border-bottom border-light-subtle">
                            <td class="fw-bold text-dark ps-4">{{ rep.titulo }}</td>
                            <td>
                                <span class="badge bg-secondary-subtle text-secondary-emphasis border border-secondary-subtle px-2 py-1 rounded-pill">{{ rep.tipo_legible }}</span>
                            </td>
                            <td class="text-muted small">{{ rep.division_nombre }}</td>
                            <td class="text-muted">{{ rep.creado_por }}</td>
                            <td class="text-muted small">{{ new Date(rep.fecha_generacion).toLocaleDateString('es-MX', {day: '2-digit', month: 'short', year: 'numeric'}) }}</td>
                            <td class="text-end pe-4">
                                <div class="d-flex justify-content-end gap-2">
                                    <a 
                                        v-if="rep.archivo" 
                                        :href="rep.archivo" 
                                        target="_blank"
                                        class="btn btn-sm btn-outline-primary fw-semibold d-flex align-items-center gap-1 shadow-sm"
                                        title="Abrir PDF original"
                                    >
                                        <i class="bi bi-file-earmark-pdf-fill"></i> PDF
                                    </a>
                                    <button 
                                        @click="eliminarDelHistorial(rep.id)" 
                                        class="btn btn-sm btn-outline-danger d-flex align-items-center shadow-sm"
                                        title="Eliminar registro"
                                    >
                                        <i class="bi bi-trash3-fill"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div v-else class="fade-in">
        <div v-if="mensajeExito" class="alert alert-success border-0 shadow-sm mb-3 d-flex align-items-center rounded-3">
            <i class="bi bi-check-circle-fill me-2 fs-5"></i> {{ mensajeExito }}
        </div>

        <div class="card mb-4 shadow-sm border-0 bg-white rounded-3">
            <div class="card-body p-4">
                <div class="row g-3 align-items-end">
                    <div class="col-md-3">
                        <label class="form-label small fw-bold text-dark-emphasis mb-1">Fecha de Inicio</label>
                        <input type="date" v-model="fechaInicio" class="form-control border-light-subtle">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small fw-bold text-dark-emphasis mb-1">Fecha de Término</label>
                        <input type="date" v-model="fechaFin" class="form-control border-light-subtle">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label small fw-bold text-dark-emphasis mb-1">Modelo de Reporte</label>
                        <select v-model="tipoReporteGenerado" class="form-select border-primary-subtle fw-semibold text-dark">
                            <option value="GENERAL">General (Bitácora Completa)</option>
                            <option value="OCUPACION">Ocupación (Métricas de Infraestructura)</option>
                            <option value="DOCENTE">Productividad e Impacto Docente</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <button @click="generarAnalisisEnVivo" class="btn btn-primary w-100 fw-bold shadow-sm" :disabled="cargando">
                            <span v-if="cargando" class="spinner-border spinner-border-sm me-2"></span>
                            <i v-else class="bi bi-lightning-charge-fill me-1"></i> {{ cargando ? 'Masticando datos...' : 'Ejecutar Análisis' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger border-0 shadow-sm mb-4 rounded-3">
            <i class="bi bi-exclamation-octagon-fill me-2"></i>{{ error }}
        </div>

        <div v-if="reservas.length > 0" class="fade-in">
            
            <div class="d-flex justify-content-end gap-2 mb-3">
                <button @click="descargarPDFLocal" class="btn btn-sm btn-outline-secondary fw-semibold bg-white shadow-sm" :disabled="cargandoAccion">
                    <i class="bi bi-file-earmark-arrow-down"></i> Descargar Copia Local
                </button>
                <button @click="guardarReporteEnSistema" class="btn btn-success fw-bold shadow-sm" :disabled="cargandoAccion">
                    <span v-if="cargandoAccion" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-cloud-arrow-up-fill me-1"></i> Archivar en Servidor
                </button>
            </div>

            <div id="reporte-imprimible" class="bg-white p-4 p-lg-5 rounded-4 shadow-sm border border-light-subtle">
                
                <div class="d-flex justify-content-between align-items-center border-bottom pb-4 mb-4">
                    <div>
                        <h4 class="fw-bold text-uppercase text-dark mb-1">
                            {{ tipoReporteGenerado === 'GENERAL' ? 'Reporte General de Actividad' : (tipoReporteGenerado === 'OCUPACION' ? 'Reporte de Ocupación de Salas' : 'Reporte de Productividad Docente') }}
                        </h4>
                        <span class="badge bg-primary text-white px-2 py-1 small fw-semibold">Filtro Temporal: {{ fechaInicio }} al {{ fechaFin }}</span>
                    </div>
                    <div class="text-end">
                        <small class="text-muted d-block fw-bold text-uppercase">División de Sistemas</small>
                        <small class="text-muted small">Corte: {{ new Date().toLocaleDateString('es-MX') }}</small>
                    </div>
                </div>

                <div class="row g-3 mb-4 row-cols-2 row-cols-md-3 row-cols-xl-5">
                    <div class="col">
                        <div class="card h-100 border-0 border-start border-4 border-primary bg-light bg-opacity-50 shadow-sm rounded-3">
                            <div class="card-body p-3">
                                <small class="text-muted text-uppercase fw-bold d-block mb-1" style="font-size: 0.65rem;">Sala Más Demandada</small>
                                <h5 class="fw-bold text-dark mb-0 text-truncate" :title="stats.salaTop">{{ stats.salaTop }}</h5>
                            </div>
                        </div>
                    </div>
                    <div class="col">
                        <div class="card h-100 border-0 border-start border-4 border-success bg-light bg-opacity-50 shadow-sm rounded-3">
                            <div class="card-body p-3">
                                <small class="text-muted text-uppercase fw-bold d-block mb-1" style="font-size: 0.65rem;">Horas Totales Uso</small>
                                <h5 class="fw-bold text-success mb-0">{{ stats.horasTotales }} <span class="fs-6 fw-normal text-muted">hrs</span></h5>
                            </div>
                        </div>
                    </div>
                    <div class="col">
                        <div class="card h-100 border-0 border-start border-4 border-info bg-light bg-opacity-50 shadow-sm rounded-3">
                            <div class="card-body p-3">
                                <small class="text-muted text-uppercase fw-bold d-block mb-1" style="font-size: 0.65rem;">Volumen Reservas</small>
                                <h5 class="fw-bold text-info mb-0">{{ stats.totalReservas }} <span class="fs-6 fw-normal text-muted">bloques</span></h5>
                            </div>
                        </div>
                    </div>
                    <div class="col">
                        <div class="card h-100 border-0 border-start border-4 border-warning bg-light bg-opacity-50 shadow-sm rounded-3">
                            <div class="card-body p-3">
                                <small class="text-muted text-uppercase fw-bold d-block mb-1" style="font-size: 0.65rem;">Docente Top</small>
                                <h5 class="fw-bold text-warning-emphasis mb-0 text-truncate" :title="stats.maestroTop">{{ stats.maestroTop }}</h5>
                            </div>
                        </div>
                    </div>
                    <div class="col">
                        <div class="card h-100 border-0 border-start border-4 border-secondary bg-light bg-opacity-50 shadow-sm rounded-3">
                            <div class="card-body p-3">
                                <small class="text-muted text-uppercase fw-bold d-block mb-1" style="font-size: 0.65rem;">Aprovechamiento</small>
                                <h5 class="fw-bold text-secondary mb-0">{{ stats.aprovechamiento }} <span class="fs-6 fw-normal text-muted">global</span></h5>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row g-4 mb-4">
                    <div class="col-lg-8">
                        <div class="card border border-light-subtle rounded shadow-sm h-100 bg-white">
                            <div class="card-header bg-light border-bottom-0 pt-3 pb-0">
                                <h6 class="fw-bold text-dark mb-0"><i class="bi bi-bar-chart-fill me-2 text-primary"></i>Frecuencia Operativa por Espacio</h6>
                            </div>
                            <div class="card-body" style="min-height: 230px;">
                                <Bar ref="barChartRef" :data="chartDataSalas" :options="chartOptions" />
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4">
                        <div class="card border border-light-subtle rounded shadow-sm h-100 bg-white">
                            <div class="card-header bg-light border-bottom-0 pt-3 pb-0">
                                <h6 class="fw-bold text-dark mb-0"><i class="bi bi-pie-chart-fill me-2 text-success"></i>Tipos de Actividad</h6>
                            </div>
                            <div class="card-body d-flex align-items-center justify-content-center" style="min-height: 230px;">
                                <Pie ref="pieChartRef" :data="chartDataActividades" :options="chartOptions" />
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row g-4 mb-5">
                    <div class="col-lg-7">
                        <div class="card border border-light-subtle rounded shadow-sm h-100 bg-white">
                            <div class="card-header bg-light border-bottom-0 pt-3 pb-0 d-flex justify-content-between">
                                <h6 class="fw-bold text-dark mb-0"><i class="bi bi-clock-history me-2 text-warning"></i>Saturación: Horas Pico</h6>
                            </div>
                            <div class="card-body" style="min-height: 230px;">
                                <Bar ref="picoChartRef" :data="chartDataHorasPico" :options="chartOptions" />
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-5">
                        <div class="card border border-light-subtle rounded shadow-sm h-100 bg-white">
                            <div class="card-header bg-light border-bottom-0 pt-3 pb-0">
                                <h6 class="fw-bold text-dark mb-0"><i class="bi bi-projector me-2 text-success"></i>Demanda de Equipamiento</h6>
                            </div>
                            <div class="card-body d-flex align-items-center justify-content-center" style="min-height: 230px;">
                                <Bar ref="equipChartRef" :data="chartDataEquipamiento" :options="chartOptions" />
                            </div>
                        </div>
                    </div>
                </div>
                
                <div v-if="tipoReporteGenerado === 'GENERAL'" class="fade-in">
                    <h5 class="fw-bold text-dark border-bottom pb-2 mb-3"><i class="bi bi-list-task me-2 text-primary"></i>Bitácora Desglosada de Actividades</h5>
                    <div class="table-responsive">
                        <table class="table table-sm table-striped table-hover align-middle small">
                            <thead class="custom-table-header">
                                <tr><th class="ps-3">Fecha</th><th>Sala</th><th>Docente</th><th class="pe-3">Horario Asignado</th></tr>
                            </thead>
                            <tbody>
                                <tr v-for="r in reservas.slice(0, 50)" :key="r.id">
                                    <td class="ps-3 text-dark fw-semibold">{{ new Date(r.inicio).toLocaleDateString('es-MX') }}</td>
                                    <td class="text-primary fw-bold">{{ (typeof r.sala === 'object') ? (r.sala.nombre_sala || r.sala.nombre) : r.sala }}</td>
                                    <td class="text-muted">{{ r.maestro_nombre || r.maestro }}</td>
                                    <td class="pe-3 text-muted">{{ new Date(r.inicio).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12:false}) }} - {{ new Date(r.fin).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', hour12:false}) }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <p v-if="reservas.length > 50" class="text-center text-muted fst-italic mt-3 small border-top pt-2">
                        Imprimiendo un corte parcial de los primeros 50 registros de un universo total de {{ reservas.length }} filas detectadas.
                    </p>
                </div>

                <div v-else-if="tipoReporteGenerado === 'OCUPACION'" class="fade-in">
                    <h5 class="fw-bold text-dark border-bottom pb-2 mb-3"><i class="bi bi-building me-2 text-primary"></i>Detalle de Aprovechamiento de Infraestructura</h5>
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="custom-table-header">
                                <tr>
                                    <th class="ps-3">Identificador del Espacio</th>
                                    <th class="text-center">Sesiones Agendadas</th>
                                    <th class="text-center">Tiempo de Uso Absoluto</th>
                                    <th class="text-center pe-3">Nivel de Explotación</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in reporteOcupacion" :key="item.nombre" class="border-bottom border-light-subtle">
                                    <td class="fw-bold text-dark ps-3">{{ item.nombre }}</td>
                                    <td class="text-center text-muted fw-semibold">{{ item.reservas }} clases</td>
                                    <td class="text-center fw-bold text-primary">{{ item.horas.toFixed(1) }} hrs</td>
                                    <td class="text-center pe-3">
                                        <span v-if="item.horas > 20" class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 rounded-pill px-3">Alto Rendimiento</span>
                                        <span v-else-if="item.horas > 5" class="badge bg-warning bg-opacity-10 text-warning-emphasis border border-warning border-opacity-25 rounded-pill px-3">Estable</span>
                                        <span v-else class="badge bg-secondary bg-opacity-10 text-secondary border border-secondary border-opacity-25 rounded-pill px-3">Subutilizada</span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div v-else-if="tipoReporteGenerado === 'DOCENTE'" class="fade-in">
                    <h5 class="fw-bold text-dark border-bottom pb-2 mb-3"><i class="bi bi-person-workspace me-2 text-primary"></i>Carga y Productividad Docente</h5>
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="custom-table-header">
                                <tr>
                                    <th class="ps-3">Nombre Completo del Catedrático</th>
                                    <th>Cúmulo de Materias Impartidas en Espacios</th>
                                    <th class="text-center">Sesiones Totales</th>
                                    <th class="text-center pe-3">Horas en Laboratorios</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in reporteDocente" :key="item.nombre" class="border-bottom border-light-subtle">
                                    <td class="fw-bold text-dark ps-3">{{ item.nombre }}</td>
                                    <td class="small text-muted text-truncate" style="max-width: 300px;" :title="item.materiasStr">{{ item.materiasStr }}</td>
                                    <td class="text-center text-muted fw-semibold">{{ item.reservas }} bloques</td>
                                    <td class="text-center fw-bold text-primary pe-3">{{ item.horas.toFixed(1) }} h</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

.custom-table-header {
    background-color: #005f86 !important;
}
.custom-table-header th {
    color: #ffffff !important;
    font-weight: 600;
    font-size: 0.85rem;
   text-transform: uppercase;
    padding-top: 10px;
    padding-bottom: 10px;
    border: none;
}
.transition-all {
    transition: all 0.2s ease;
}
</style>