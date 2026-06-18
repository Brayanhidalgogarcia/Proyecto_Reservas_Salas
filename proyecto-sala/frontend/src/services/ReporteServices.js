/**
 * @file ReporteServices.js
 * @description Servicio especializado para la gestión del historial de reportes y bitácoras (Módulo reportes).
 * Extiende la configuración base de la API para administrar la subida y descarga de 
 * archivos binarios (PDFs) mediante el protocolo multipart/form-data.
 */

import { apiClient } from '@/services/ApiService'; 

const RESOURCE = '/reportes/'; 

export default {
    
    // ==========================================
    // MÉTODOS DE HISTORIAL Y ARCHIVO
    // ==========================================

    /**
     * Consulta el catálogo histórico de reportes guardados en el servidor.
     * @param {Object} filtros - Parámetros de búsqueda opcionales. 
     * Ej: { tipo: 'OCUPACION', anio: 2026, page: 1 }
     * @returns {Promise} Promesa con el array de reportes.
     */
    obtenerReportes(filtros = {}) {
        return apiClient.get(RESOURCE, { params: filtros });
    },

    /**
     * Empaqueta un archivo binario (PDF) junto con su metadata (título, fechas) 
     * en un objeto FormData para enviarlo de forma segura al backend de Django.
     * * @param {Object} payload - Objeto con la información del reporte.
     * @param {string} payload.titulo - Nombre visible del documento.
     * @param {string} payload.tipo - Categoría (GENERAL, OCUPACION, DOCENTE).
     * @param {string} payload.fecha_inicio_datos - Rango de inicio del análisis (YYYY-MM-DD).
     * @param {string} payload.fecha_fin_datos - Rango de fin del análisis (YYYY-MM-DD).
     * @param {File} payload.archivo - Objeto binario nativo de JavaScript (El PDF generado).
     * @returns {Promise} Promesa con la respuesta de la creación.
     */
    crearReporte(payload) {
        const formData = new FormData();

        // 1. Inyección de Metadata
        formData.append('titulo', payload.titulo);
        formData.append('tipo', payload.tipo);
        
        if (payload.fecha_inicio_datos) {
            formData.append('fecha_inicio_datos', payload.fecha_inicio_datos);
        }
        if (payload.fecha_fin_datos) {
            formData.append('fecha_fin_datos', payload.fecha_fin_datos);
        }

        // 2. Inyección del Archivo Físico
        if (payload.archivo) {
            formData.append('archivo', payload.archivo);
        }

        // 3. Envío forzando la cabecera multipart
        return apiClient.post(RESOURCE, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    },

    /**
     * Elimina permanentemente un registro de reporte y su archivo PDF asociado en el servidor.
     * @param {number|string} id - Identificador único del reporte.
     * @returns {Promise}
     */
    eliminarReporte(id) {
        return apiClient.delete(`${RESOURCE}${id}/`);
    },

    /**
     * Descarga el archivo físico forzando la interpretación de la respuesta como un 
     * Blob (Binary Large Object), ideal para manejar PDFs desde el cliente.
     * @param {string} urlRelativa - Ruta directa al archivo proporcionada por el backend.
     * @returns {Promise<Blob>} Promesa que resuelve en el flujo binario del archivo.
     */
    descargarReporte(urlRelativa) {
        return apiClient.get(urlRelativa, {
            responseType: 'blob' 
        });
    }
};