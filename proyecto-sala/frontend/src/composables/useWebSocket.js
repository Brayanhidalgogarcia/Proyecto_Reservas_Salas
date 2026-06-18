/**
 * @file useWebSocket.js
 * @description Composable de Vue para gestionar la conexión bidireccional en tiempo real (WebSockets).
 * Mantiene la interfaz sincronizada escuchando actualizaciones del backend de Django.
 * Incluye lógica de auto-reconexión y limpieza automática al destruir el componente.
 */

// ==========================================
// 1. IMPORTS
// ==========================================
import { onUnmounted } from 'vue';

// ==========================================
// 2. EXPORTACIÓN DEL COMPOSABLE
// ==========================================

/**
 * Inicializa y gestiona el ciclo de vida de un WebSocket.
 * @param {Function} onMessageCallback - Función que se ejecutará cada vez que el servidor 
 * notifique un cambio (generalmente para volver a ejecutar la petición GET de datos).
 * @returns {Object} Un objeto con la función `conectar` para iniciar la escucha.
 */
export function useWebSocket(onMessageCallback) {
    /** @type {WebSocket|null} */
    let socket = null;

    /**
     * Construye la URL dinámica y establece la conexión con el servidor.
     */
    const conectar = () => {
        // 1. Detección Inteligente del Entorno
        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        
        let host = window.location.host;
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            host = '127.0.0.1:8000';
        }

        // Prioriza la variable de entorno de Vite (para producción), sino usa el cálculo local
        const wsUrl = import.meta.env.VITE_WS_URL || `${wsProtocol}${host}/ws/reservas/`;
        
        // 2. Inicialización del Socket
        socket = new WebSocket(wsUrl);

        // 3. Manejadores de Eventos (Event Listeners)
        socket.onopen = () => {
            console.info("🟢 WebSocket Conectado exitosamente a:", wsUrl);
        };
        
        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.info("🔄 Actualización en tiempo real recibida:", data.message || 'Cambio detectado');
                
                // Ejecuta la función inyectada por el componente (ej. cargarDatos)
                if (typeof onMessageCallback === 'function') {
                    onMessageCallback();
                }
            } catch (error) {
                console.error("Error al procesar el mensaje del WebSocket:", error);
            }
        };

        socket.onclose = () => {
            console.warn("🟡 WebSocket desconectado. Intentando reconectar en 3 segundos...");
            setTimeout(conectar, 3000);
        };
        
        socket.onerror = (err) => {
            console.error("🔴 Error en la capa de transporte del WebSocket:", err);
            socket.close(); // Forzamos el cierre para desencadenar el onclose y su reconexión
        };
    };

    // ==========================================
    // 3. CICLO DE VIDA (Limpieza de Memoria)
    // ==========================================
    
    /**
     * Vue se encarga automáticamente de ejecutar esto cuando el componente
     * que llamó a `useWebSocket` se destruye (ej. al cambiar de página).
     */
    onUnmounted(() => {
        if (socket) {
            // Se anula el onclose para evitar que el setTimeout intente reconectar 
            // a un componente que ya no existe en la pantalla.
            socket.onclose = null; 
            socket.close();
            console.info("⚪ Conexión WebSocket cerrada limpiamente (Componente destruido).");
        }
    });

    return { conectar };
}