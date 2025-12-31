<script setup>
import { ref, onMounted, computed } from 'vue';
import ApiService from '@/services/ApiService.js';
import * as XLSX from 'xlsx';

// --- NUEVOS IMPORTS PARA PDF ---
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

// Registrar componentes de Chart.js
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

// --- Estado ---
const reservas = ref([]);
const salas = ref([]);
const cargando = ref(false);
const cargandoPDF = ref(false); // Estado para el botón de PDF
const error = ref(null);

// Filtros
const fechaInicio = ref('');
const fechaFin = ref('');
const salaSeleccionada = ref('');

// Estadísticas Calculadas
const stats = ref({
    salaTop: 'N/A',
    maestroTop: 'N/A',
    materiaTop: 'N/A',
    tasaOcupacion: 0,
    horasTotales: 0,
    diaPico: 'N/A'
});

// Datos para Gráficos
const chartDataSalas = ref({ labels: [], datasets: [] });
const chartDataDias = ref({ labels: [], datasets: [] });
const chartOptions = { responsive: true, maintainAspectRatio: false };

// --- Carga inicial ---
onMounted(async () => {
  try {
    const responseSalas = await ApiService.obtenerSalas();
    salas.value = responseSalas.data || responseSalas;
    
    // Fechas por defecto: Mes actual
    const hoy = new Date();
    // Primer día del mes
    const primerDia = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
    // Último día del mes
    const ultimoDia = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0);
    
    // Formato YYYY-MM-DD local
    const offset = primerDia.getTimezoneOffset() * 60000;
    fechaInicio.value = new Date(primerDia - offset).toISOString().split('T')[0];
    fechaFin.value = new Date(ultimoDia - offset).toISOString().split('T')[0];
    
    generarReporte(); 
  } catch (err) {
    console.error("Error cargando datos iniciales", err);
  }
});

// --- Generar Reporte (Lógica de Filtrado Local) ---
async function generarReporte() {
  cargando.value = true;
  error.value = null;
  reservas.value = [];

  try {
    // 1. Obtenemos TODAS las reservas (sin filtros al backend para evitar errores de API)
    const response = await ApiService.obtenerReservas();
    const todosLosDatos = response.data || response;

    if (!Array.isArray(todosLosDatos)) {
        throw new Error("El formato de respuesta de reservas no es una lista válida.");
    }

    // 2. Preparamos fechas de filtro (Inicio a las 00:00, Fin a las 23:59)
    // Usamos string comparison para evitar problemas de zona horaria simples
    const fInicio = fechaInicio.value; 
    const fFin = fechaFin.value;

    // 3. Filtramos manualmente en el Frontend
    reservas.value = todosLosDatos.filter(r => {
        // Extraemos la parte de la fecha YYYY-MM-DD de la reserva
        const fechaReserva = r.inicio ? r.inicio.split('T')[0] : '';
        
        // A) Filtro de Fecha
        const enRango = fechaReserva >= fInicio && fechaReserva <= fFin;
        
        // B) Filtro de Sala (si está seleccionada)
        let coincideSala = true;
        if (salaSeleccionada.value) {
            const idSalaReserva = (typeof r.sala === 'object') ? r.sala.id : r.sala;
            // Comparamos como string por si acaso
            coincideSala = String(idSalaReserva) === String(salaSeleccionada.value);
            // También intentamos comparar por clave si la API devuelve objetos distintos
            if (!coincideSala && typeof r.sala === 'object') {
                coincideSala = r.sala.clave_sala === salaSeleccionada.value;
            }
        }

        return enRango && coincideSala;
    });
    
    // Una vez tenemos los datos filtrados, calculamos las estadísticas
    calcularEstadisticas();
    prepararGraficos();

  } catch (err) {
    error.value = 'Error al generar el reporte. Verifique la conexión.';
    console.error(err);
  } finally {
    cargando.value = false;
  }
}

// --- Lógica de Negocio: Cálculo de Estadísticas ---
function calcularEstadisticas() {
    if (reservas.value.length === 0) {
        resetStats();
        return;
    }

    // 1. Contadores
    const conteoSalas = {};
    const conteoMaestros = {};
    const conteoMaterias = {};
    const conteoDias = { 0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0 }; // Dom-Sab
    let totalHoras = 0;

    reservas.value.forEach(r => {
        // Normalizar nombres
        const s = (typeof r.sala === 'object') ? (r.sala.nombre_sala || r.sala.nombre) : (r.sala_nombre || r.sala || 'Desconocido');
        const m = r.maestro_nombre || r.maestro || 'Desconocido';
        const mat = r.asignatura_nombre || r.asignatura || 'Desconocido';
        
        // Contar
        conteoSalas[s] = (conteoSalas[s] || 0) + 1;
        conteoMaestros[m] = (conteoMaestros[m] || 0) + 1;
        conteoMaterias[mat] = (conteoMaterias[mat] || 0) + 1;

        // Horas
        const inicio = new Date(r.inicio);
        const fin = new Date(r.fin);
        const duracion = (fin - inicio) / (1000 * 60 * 60); // en horas
        if (!isNaN(duracion)) {
            totalHoras += duracion;
        }

        // Día de la semana
        const diaSemana = inicio.getDay(); 
        conteoDias[diaSemana]++;
    });

    // 2. Encontrar los ganadores (Top)
    stats.value.salaTop = getKeyWithMaxVal(conteoSalas);
    stats.value.maestroTop = getKeyWithMaxVal(conteoMaestros);
    stats.value.materiaTop = getKeyWithMaxVal(conteoMaterias);
    stats.value.horasTotales = totalHoras.toFixed(1);

    // 3. Día Pico
    const diasNombres = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'];
    const diaIndex = Object.keys(conteoDias).reduce((a, b) => conteoDias[a] > conteoDias[b] ? a : b);
    stats.value.diaPico = diasNombres[diaIndex];

    // 4. Tasa de Ocupación (Estimada)
    const start = new Date(fechaInicio.value);
    const end = new Date(fechaFin.value);
    const diasDiferencia = Math.max(1, Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1);
    const capacidadTotalHoras = diasDiferencia * 8 * (salas.value.length || 1); // 8 horas laborales
    
    stats.value.tasaOcupacion = ((totalHoras / capacidadTotalHoras) * 100).toFixed(1) + '%';
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

    // A) Gráfico de Barras: Uso por Sala
    const conteoSalas = {};
    reservas.value.forEach(r => {
        const s = (typeof r.sala === 'object') ? (r.sala.nombre_sala || r.sala.nombre) : (r.sala_nombre || r.sala || 'Desconocido');
        conteoSalas[s] = (conteoSalas[s] || 0) + 1;
    });

    chartDataSalas.value = {
        labels: Object.keys(conteoSalas),
        datasets: [{
            label: 'Reservas por Sala',
            backgroundColor: '#005f86',
            data: Object.values(conteoSalas)
        }]
    };

    // B) Gráfico de Pastel: Distribución por Materia
    const conteoMat = {};
    reservas.value.forEach(r => {
        const m = r.asignatura_nombre || r.asignatura || 'Otros';
        conteoMat[m] = (conteoMat[m] || 0) + 1;
    });
    
    // Top 5
    const top5 = Object.entries(conteoMat).sort((a,b) => b[1]-a[1]).slice(0, 5);
    
    chartDataDias.value = {
        labels: top5.map(x => x[0]),
        datasets: [{
            backgroundColor: ['#41B883', '#E46651', '#00D8FF', '#DD1B16', '#ffc107'],
            data: top5.map(x => x[1])
        }]
    };
}

// --- Exportar a Excel ---
function descargarExcel() {
  if (reservas.value.length === 0) return;

  const datosParaExcel = reservas.value.map(reserva => {
      // Manejo seguro de nombres
      const salaStr = (typeof reserva.sala === 'object') ? (reserva.sala.nombre_sala || reserva.sala.nombre) : (reserva.sala_nombre || reserva.sala);
      
      return {
        'Maestro': reserva.maestro_nombre || reserva.maestro,
        'Asignatura': reserva.asignatura_nombre || reserva.asignatura,
        'Sala': salaStr,
        'Fecha Inicio': formatDateTime(reserva.inicio),
        'Fecha Fin': formatDateTime(reserva.fin),
        'Tema': reserva.tema
      };
  });

  const hoja = XLSX.utils.json_to_sheet(datosParaExcel);
  const libro = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(libro, hoja, "Reporte");
  const fechaHoy = new Date().toISOString().split('T')[0];
  XLSX.writeFile(libro, `Reporte_Salas_UJAT_${fechaHoy}.xlsx`);
}

// --- NUEVA FUNCIÓN: Descargar PDF ---
const descargarPDF = async () => {
    // Validar si hay datos
    if (reservas.value.length === 0) return;

    cargandoPDF.value = true;
    
    // Seleccionamos el contenedor que queremos "fotografiar"
    const elemento = document.getElementById('reporte-imprimible');
    
    if (elemento) {
        try {
            // 1. Convertir HTML a Canvas (Imagen)
            const canvas = await html2canvas(elemento, {
                scale: 2, // Mejor resolución
                useCORS: true // Por si hay imágenes externas
            });

            // 2. Crear PDF
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF('p', 'mm', 'a4'); // p = portrait, mm = milímetros, a4 = tamaño
            
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
            
            // 3. Agregar imagen al PDF
            pdf.addImage(imgData, 'PNG', 0, 10, pdfWidth, pdfHeight); // 10mm de margen superior
            
            // 4. Descargar
            const fechaHoy = new Date().toISOString().split('T')[0];
            pdf.save(`Reporte_Grafico_UJAT_${fechaHoy}.pdf`);
            
        } catch (error) {
            console.error("Error al generar PDF:", error);
            alert("Hubo un error al generar el PDF.");
        } finally {
            cargandoPDF.value = false;
        }
    }
};

// --- Utilidades ---
function formatDateTime(dateTimeString) {
  if (!dateTimeString) return 'N/A';
  const dt = new Date(dateTimeString);
  return dt.toLocaleDateString('es-MX') + ' ' + dt.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
}
</script>

<template>
  <div class="container-fluid p-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="text-dark fw-bold mb-0">
            <i class="bi bi-bar-chart-line-fill text-primary me-2"></i>Reporte de Uso
        </h2>
        
        <!-- Grupo de Botones de Exportación -->
        <div v-if="reservas.length > 0">
            <button @click="descargarExcel" class="btn btn-success me-2">
                <i class="bi bi-file-earmark-excel me-1"></i> Excel
            </button>
            <button @click="descargarPDF" class="btn btn-danger" :disabled="cargandoPDF">
                <span v-if="cargandoPDF" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-file-earmark-pdf me-1"></i> 
                {{ cargandoPDF ? 'Generando...' : 'PDF con Gráficas' }}
            </button>
        </div>
    </div>

    <!-- 1. Panel de Filtros -->
    <div class="card mb-4 shadow-sm border-0">
      <div class="card-body bg-light rounded">
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="form-label small fw-bold text-muted">Fecha Inicio</label>
            <input type="date" v-model="fechaInicio" class="form-control">
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-bold text-muted">Fecha Fin</label>
            <input type="date" v-model="fechaFin" class="form-control">
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-bold text-muted">Sala (Opcional)</label>
            <select v-model="salaSeleccionada" class="form-select">
              <option value="">Todas las salas</option>
              <!-- Ajuste de clave/id para el select -->
              <option v-for="sala in salas" :key="sala.id || sala.clave_sala" :value="sala.id || sala.clave_sala">
                {{ sala.nombre_sala || sala.nombre }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <button @click="generarReporte" class="btn btn-primary w-100" :disabled="cargando">
              <span v-if="cargando" class="spinner-border spinner-border-sm me-2"></span>
              {{ cargando ? 'Analizando...' : 'Generar Reporte' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- CONTENEDOR PARA IMPRESIÓN (ID ÚNICO) -->
    <div id="reporte-imprimible" class="bg-white p-3 rounded" v-if="!cargando && reservas.length > 0">
        
        <!-- 2. Tarjetas de KPI -->
        <div class="row g-4 mb-4">
            <div class="col-md-3">
                <div class="card h-100 border-0 shadow-sm border-start border-4 border-primary">
                    <div class="card-body">
                        <h6 class="text-muted text-uppercase small">Sala más usada</h6>
                        <h4 class="fw-bold text-primary mb-0 text-truncate">{{ stats.salaTop }}</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card h-100 border-0 shadow-sm border-start border-4 border-success">
                    <div class="card-body">
                        <h6 class="text-muted text-uppercase small">Maestro más frecuente</h6>
                        <h4 class="fw-bold text-success mb-0 text-truncate">{{ stats.maestroTop }}</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card h-100 border-0 shadow-sm border-start border-4 border-warning">
                    <div class="card-body">
                        <h6 class="text-muted text-uppercase small">Día con más demanda</h6>
                        <h4 class="fw-bold text-warning mb-0">{{ stats.diaPico }}</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card h-100 border-0 shadow-sm border-start border-4 border-info">
                    <div class="card-body">
                        <h6 class="text-muted text-uppercase small">Tasa de Ocupación</h6>
                        <h4 class="fw-bold text-info mb-0">{{ stats.tasaOcupacion }}</h4>
                        <small class="text-muted">{{ stats.horasTotales }} horas totales</small>
                    </div>
                </div>
            </div>
        </div>

        <!-- 3. Sección de Gráficos -->
        <div class="row mb-4">
            <div class="col-md-8">
                <div class="card shadow-sm border-0 h-100">
                    <div class="card-header bg-white fw-bold">Uso por Sala</div>
                    <div class="card-body" style="height: 300px;">
                        <Bar :data="chartDataSalas" :options="chartOptions" />
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card shadow-sm border-0 h-100">
                    <div class="card-header bg-white fw-bold">Top Materias</div>
                    <div class="card-body" style="height: 300px;">
                        <Pie :data="chartDataDias" :options="chartOptions" />
                    </div>
                </div>
            </div>
        </div>

        <!-- 4. Tabla Detallada -->
        <div class="card shadow-sm border-0">
        <div class="card-header bg-white fw-bold">Detalle de Registros</div>
        <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
            <thead class="table-light">
                <tr>
                <th>Maestro</th>
                <th>Asignatura</th>
                <th>Sala</th>
                <th>Fecha</th>
                <th>Horario</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="reserva in reservas" :key="reserva.id">
                <td>{{ reserva.maestro_nombre || reserva.maestro }}</td>
                <td>{{ reserva.asignatura_nombre || reserva.asignatura }}</td>
               
                <td class="fw-bold text-primary">
                    {{ (typeof reserva.sala === 'object') ? (reserva.sala.nombre_sala || reserva.sala.nombre) : (reserva.sala_nombre || reserva.sala) }}
                </td>
                <td>{{ new Date(reserva.inicio).toLocaleDateString('es-MX') }}</td>
                <td>
                    <span class="badge bg-light text-dark border">
                        {{ new Date(reserva.inicio).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}) }} - 
                        {{ new Date(reserva.fin).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}) }}
                    </span>
                </td>
                </tr>
            </tbody>
            </table>
        </div>
        <div class="card-footer bg-white text-muted small">
            Mostrando {{ reservas.length }} registros
        </div>
        </div>
    
    </div> 

    <div v-if="!cargando && reservas.length === 0 && !error" class="text-center py-5 text-muted">
        <i class="bi bi-search display-4 mb-3"></i>
        <p>No se encontraron datos para el periodo seleccionado.</p>
    </div>

  </div>
</template>

<style scoped>
.card { border-radius: 8px; }
.text-truncate {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
}
</style>