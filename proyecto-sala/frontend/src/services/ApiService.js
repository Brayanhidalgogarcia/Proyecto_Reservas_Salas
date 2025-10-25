import axios from 'axios';

// Creamos una instancia de Axios con la configuración base.
// Usamos la URL de tu API de Django que definimos anteriormente.
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/version1/',
    headers: {
        'Content-Type': 'application/json'
    }
});

// Exportamos un objeto con los métodos para comunicarnos con los endpoints.
// Cada método corresponde a una acción que queremos realizar en el backend.
export default {
    // --- Métodos para Salas ---
    obtenerSalas() {
        return apiClient.get('/salas/');
    },

    // --- Métodos para Reservas ---
    obtenerReservas() {
        return apiClient.get('/reservas/');
    },

    // --- Métodos para Maestros ---
    obtenerMaestros() {
        return apiClient.get('/maestros/');
    },


};

