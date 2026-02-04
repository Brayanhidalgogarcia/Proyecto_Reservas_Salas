
import { apiClient } from '@/services/ApiService'; 

const RESOURCE = '/reportes/'; 

export default {
    /**     
     * @param {Object} filtros - { tipo: 'OCUPACION', anio: 2025, page: 1 }
     */
    obtenerReportes(filtros = {}) {
       
        return apiClient.get(RESOURCE, { params: filtros });
    },

    
    crearReporte(payload) {
        const formData = new FormData();

        
        formData.append('titulo', payload.titulo);
        formData.append('tipo', payload.tipo);
        
        if (payload.fecha_inicio_datos) {
            formData.append('fecha_inicio_datos', payload.fecha_inicio_datos);
        }
        if (payload.fecha_fin_datos) {
            formData.append('fecha_fin_datos', payload.fecha_fin_datos);
        }

 
        if (payload.archivo) {
            formData.append('archivo', payload.archivo);
        }

       
        return apiClient.post(RESOURCE, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    },

    
    eliminarReporte(id) {
        return apiClient.delete(`${RESOURCE}${id}/`);
    },

    
    descargarReporte(urlRelativa) {
        return apiClient.get(urlRelativa, {
            responseType: 'blob' 
        });
    }
};