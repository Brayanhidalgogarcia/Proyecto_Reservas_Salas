/**
 * @file ApiService.js
 * @description Capa de servicios centralizada para la comunicación HTTP con el backend (Django REST Framework).
 * Implementa Axios, inyección automática de tokens JWT mediante interceptores y manejo global de errores 401.
 */

import axios from 'axios';

// ==========================================
// 1. CONFIGURACIÓN DE INSTANCIA AXIOS
// ==========================================

/**
 * Instancia principal de Axios. 
 * Utiliza variables de entorno para la URL si están disponibles (Producción), 
 * o el servidor local por defecto (Desarrollo).
 */
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1/',
  headers: {
    'Content-Type': 'application/json'
  }
});

// ==========================================
// 2. INTERCEPTORES DE PETICIÓN Y RESPUESTA
// ==========================================

/**
 * INTERCEPTOR DE REQUEST (Ida)
 * Antes de que la petición salga hacia el servidor, busca el token de acceso
 * en el almacenamiento local y lo inyecta en las cabeceras de autorización.
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * INTERCEPTOR DE RESPONSE (Vuelta)
 * Monitorea todas las respuestas del servidor. Si detecta un error 401 (Unauthorized),
 * significa que el token expiró o es inválido. Destruye la sesión completa de forma segura
 * y expulsa al usuario a la pantalla de Login.
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("Sesión expirada o token inválido. Redirigiendo al login...");
      
      // Limpieza exhaustiva de todos los rastros de la sesión en el cliente
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('is_superuser');
      localStorage.removeItem('username');
      localStorage.removeItem('nombre_usuario'); 
      localStorage.removeItem('user_division');
      
      // Redirección forzada. Se usa window.location porque el router de Vue 
      // no está inyectado directamente en este archivo puro de JavaScript.
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ==========================================
// 3. MÓDULOS DE ENDPOINTS
// ==========================================

export default {

  // ----------------------------------------
  // MÓDULO: SEGURIDAD Y USUARIOS
  // ----------------------------------------
  obtenerUsuarios() {
    return apiClient.get('/usuarios/');
  },
  obtenerUsuario(id) {
    return apiClient.get(`/usuarios/${id}/`);
  },
  actualizarPasswordUsuario(idUsuario, nuevaPassword) {
    return apiClient.put(`/usuarios/${idUsuario}/actualizar_password/`, {
      nueva_password: nuevaPassword
    });
  },
  crearUsuario(datosUsuario) {
    return apiClient.post('/usuarios/', datosUsuario);
  },
  actualizarUsuario(id, datosUsuario) {
    return apiClient.put(`/usuarios/${id}/`, datosUsuario);
  },
  eliminarUsuario(id) {
    return apiClient.delete(`/usuarios/${id}/`);
  },
  /**
   * Endpoint específico administrativo para registrar docentes.
   * @param {Object} datos - { username, password, matricula, email }
   */
  registrarUsuario(datos) {
    return apiClient.post('/admin/registro-usuario/', datos);
  },

  // ----------------------------------------
  // MÓDULO: CATÁLOGOS BASE (Infraestructura)
  // ----------------------------------------
  obtenerDivisiones() { return apiClient.get('/divisiones/'); },
  obtenerDivision(clave) { return apiClient.get(`/divisiones/${clave}/`); },
  crearDivision(datos) { return apiClient.post('/divisiones/', datos); },
  actualizarDivision(clave, datos) { return apiClient.put(`/divisiones/${clave}/`, datos); },
  eliminarDivision(clave) { return apiClient.delete(`/divisiones/${clave}/`); },

  obtenerEdificios() { return apiClient.get('/edificios/'); },
  obtenerEdificio(id) { return apiClient.get(`/edificios/${id}/`); },
  crearEdificio(datos) { return apiClient.post('/edificios/', datos); },
  actualizarEdificio(id, datos) { return apiClient.put(`/edificios/${id}/`, datos); },
  eliminarEdificio(id) { return apiClient.delete(`/edificios/${id}/`); },

  obtenerSalas() { return apiClient.get('/salas/'); },
  obtenerSala(clave) { return apiClient.get(`/salas/${clave}/`); },
  crearSala(datos) { return apiClient.post('/salas/', datos); },
  actualizarSala(clave, datos) { return apiClient.put(`/salas/${clave}/`, datos); },
  eliminarSala(clave) { return apiClient.delete(`/salas/${clave}/`); },

  // ----------------------------------------
  // MÓDULO: CATÁLOGOS ACADÉMICOS
  // ----------------------------------------
  obtenerActividades() { return apiClient.get('/actividades/'); },

  obtenerAsignaturas() { return apiClient.get('/asignaturas/'); },
  obtenerAsignatura(clave) { return apiClient.get(`/asignaturas/${clave}/`); },
  crearAsignatura(datos) { return apiClient.post('/asignaturas/', datos); },
  actualizarAsignatura(clave, datos) { return apiClient.put(`/asignaturas/${clave}/`, datos); },
  eliminarAsignatura(clave) { return apiClient.delete(`/asignaturas/${clave}/`); },

  obtenerMaestros() { return apiClient.get('/maestros/'); },
  obtenerMaestro(matricula) { return apiClient.get(`/maestros/${matricula}/`); },
  crearMaestro(datos) { return apiClient.post('/maestros/', datos); },
  actualizarMaestro(matricula, datos) { return apiClient.put(`/maestros/${matricula}/`, datos); },
  eliminarMaestro(matricula) { return apiClient.delete(`/maestros/${matricula}/`); },

  // ----------------------------------------
  // MÓDULO: RESERVAS Y OPERACIONES
  // ----------------------------------------
  /**
   * Obtiene la bitácora de reservas. Permite filtrar dinámicamente mediante Query Params.
   * @param {Object} filtros - Ej. { sala: 1, fecha: '2026-06-16' }
   */
  obtenerReservas(filtros = {}) {
    const params = new URLSearchParams(filtros).toString();
    return apiClient.get(`/reservas/?${params}`);
  },
  obtenerReserva(id) { return apiClient.get(`/reservas/${id}/`); },
  crearReserva(datos) { return apiClient.post('/reservas/', datos); },
  actualizarReserva(id, datos) { return apiClient.put(`/reservas/${id}/`, datos); },
  eliminarReserva(id) { return apiClient.delete(`/reservas/${id}/`); }

};