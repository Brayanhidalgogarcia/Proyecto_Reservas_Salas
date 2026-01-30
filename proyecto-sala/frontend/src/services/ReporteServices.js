
import { apiClient } from '@/services/ApiService'; 

const RESOURCE = '/reportes/'; 

export default {
    /**
     * Obtiene el historial de reportes con filtros inteligentes.
     * @param {Object} filtros - { tipo: 'OCUPACION', anio: 2025, page: 1 }
     */
    obtenerReportes(filtros = {}) {
        // Usamos apiClient (que ya tiene el token y la URL base configurados)
        return apiClient.get(RESOURCE, { params: filtros });
    },

    /**
     * Crea un nuevo reporte y sube el archivo generado.
     */
    crearReporte(payload) {
        const formData = new FormData();

        // Agregamos los campos de texto
        formData.append('titulo', payload.titulo);
        formData.append('tipo', payload.tipo);
        
        if (payload.fecha_inicio_datos) {
            formData.append('fecha_inicio_datos', payload.fecha_inicio_datos);
        }
        if (payload.fecha_fin_datos) {
            formData.append('fecha_fin_datos', payload.fecha_fin_datos);
        }

        // Agregamos el archivo físico si existe
        if (payload.archivo) {
            formData.append('archivo', payload.archivo);
        }

        // Enviamos con la cabecera correcta para subida de archivos
        return apiClient.post(RESOURCE, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    },

    /**
     * Elimina un reporte del historial (Solo Admin).
     */
    eliminarReporte(id) {
        return apiClient.delete(`${RESOURCE}${id}/`);
    },

    /**
     * Descarga el archivo asociado al reporte.
     */
    descargarReporte(urlRelativa) {
        return apiClient.get(urlRelativa, {
            responseType: 'blob' 
        });
    }
};