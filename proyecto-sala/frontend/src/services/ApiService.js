import axios from 'axios';


const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1/', 
  headers: {
    'Content-Type': 'application/json'
    
  }
});


export default {


  obtenerPerfilesAdmin() {
    return apiClient.get('/perfiles/');
  },
  obtenerPerfilAdmin(matriculaUD) { 
    return apiClient.get(`/perfiles/${matriculaUD}/`);
  },
  crearPerfilAdmin(datosPerfil) {
    
    return apiClient.post('/perfiles/', datosPerfil);
  },
  actualizarPerfilAdmin(matriculaUD, datosPerfil) {
    return apiClient.put(`/perfiles/${matriculaUD}/`, datosPerfil);
  },
  eliminarPerfilAdmin(matriculaUD) {
    return apiClient.delete(`/perfiles/${matriculaUD}/`);
  },


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

  // --- Métodos para Asignaturas ---
  obtenerAsignaturas() {
    return apiClient.get('/asignaturas/');
  },
  obtenerAsignatura(claveAsignatura) { // La PK es la clave
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

  // --- Métodos para Salas ---
  obtenerSalas() {
    return apiClient.get('/salas/');
  },
  obtenerSala(claveSala) { // La PK es la clave
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

  // --- Métodos para Maestros ---
  obtenerMaestros() {
    return apiClient.get('/maestros/');
  },
  obtenerMaestro(matriculaM) { // La PK es la matrícula
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

 
  obtenerReservas(filtros = {}) {
    // Convierte el objeto { clave: valor } a string de URL "clave=valor&..."
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

