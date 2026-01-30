import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1/', 
  headers: {
    'Content-Type': 'application/json'
  }
});

// --- INTERCEPTOR DE SEGURIDAD (TOKEN) ---
// Antes de enviar cualquier petición, revisa si hay un token guardado
// y lo pega en la cabecera "Authorization".
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

// --- INTERCEPTOR DE ERRORES (Opcional pero recomendado) ---
// Si el token venció (Error 401), podemos sacar al usuario automáticamente.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token vencido o inválido
      console.warn("Sesión expirada. Redirigiendo al login...");
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      // Forzamos la recarga hacia el login para limpiar el estado
      if (window.location.pathname !== '/login') {
          window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default {

  
  // Actualizamos las rutas a '/usuarios/' porque cambiamos el backend
  obtenerUsuarios() {
    return apiClient.get('/usuarios/');
  },
  obtenerUsuario(id) { 
    return apiClient.get(`/usuarios/${id}/`);
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

  // --- DIVISIONES ---
  obtenerDivisiones() {
    return apiClient.get('/divisiones/');
  },
  obtenerDivision(claveDivision) { 
    return apiClient.get(`/divisiones/${claveDivision}/`);
  },
  crearDivision(datosDivision) {
    return apiClient.post('/divisiones/', datosDivision);
  },
  actualizarDivision(claveDivision, datosDivision) {
    return apiClient.put(`/divisiones/${claveDivision}/`, datosDivision);
  },
  eliminarDivision(claveDivision) {
    return apiClient.delete(`/divisiones/${claveDivision}/`);
  },

  // --- ASIGNATURAS ---
  obtenerAsignaturas() {
    return apiClient.get('/asignaturas/');
  },
  obtenerAsignatura(claveAsignatura) { 
    return apiClient.get(`/asignaturas/${claveAsignatura}/`);
  },
  crearAsignatura(datosAsignatura) {
    return apiClient.post('/asignaturas/', datosAsignatura);
  },
  actualizarAsignatura(claveAsignatura, datosAsignatura) {
    return apiClient.put(`/asignaturas/${claveAsignatura}/`, datosAsignatura);
  },
  eliminarAsignatura(claveAsignatura) {
    return apiClient.delete(`/asignaturas/${claveAsignatura}/`);
  },

  // --- SALAS ---
  obtenerSalas() {
    return apiClient.get('/salas/');
  },
  obtenerSala(claveSala) { 
    return apiClient.get(`/salas/${claveSala}/`);
  },
  crearSala(datosSala) {
    return apiClient.post('/salas/', datosSala);
  },
  actualizarSala(claveSala, datosSala) {
    return apiClient.put(`/salas/${claveSala}/`, datosSala);
  },
  eliminarSala(claveSala) {
    return apiClient.delete(`/salas/${claveSala}/`);
  },

  // --- MAESTROS ---
  obtenerMaestros() {
    return apiClient.get('/maestros/');
  },
  obtenerMaestro(matriculaM) { 
    return apiClient.get(`/maestros/${matriculaM}/`);
  },
  crearMaestro(datosMaestro) {
    return apiClient.post('/maestros/', datosMaestro);
  },
  actualizarMaestro(matriculaM, datosMaestro) {
    return apiClient.put(`/maestros/${matriculaM}/`, datosMaestro);
  },
  eliminarMaestro(matriculaM) {
    return apiClient.delete(`/maestros/${matriculaM}/`);
  },

  // --- RESERVAS ---
  obtenerReservas(filtros = {}) {
    const params = new URLSearchParams(filtros).toString();
    return apiClient.get(`/reservas/?${params}`);
  },

  obtenerReserva(id) {
    return apiClient.get(`/reservas/${id}/`);
  },
  crearReserva(datosReserva) {
    return apiClient.post('/reservas/', datosReserva);
  },
  actualizarReserva(id, datosReserva) {
    return apiClient.put(`/reservas/${id}/`, datosReserva);
  },
  eliminarReserva(id) {
    return apiClient.delete(`/reservas/${id}/`);
  }

};