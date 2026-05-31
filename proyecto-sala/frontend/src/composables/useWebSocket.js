import { onUnmounted } from 'vue';

export function useWebSocket(onMessageCallback) {
    let socket = null;

    const conectar = () => {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const host = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
                    ? '127.0.0.1:8000' 
                    : window.location.host; 

        const wsUrl = `${wsProtocol}${host}/ws/reservas/`;
        
        socket = new WebSocket(wsUrl);

        socket.onopen = () => console.log("🟢 WebSocket Conectado a:", wsUrl);
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("📩 Actualización recibida:", data.message);
            // Ejecuta la función que le mande el componente (ej. cargarDatos)
            if (onMessageCallback) onMessageCallback();
        };

        socket.onclose = () => {
            console.warn("WebSocket desconectado. Intentando reconectar...");
            setTimeout(conectar, 3000);
        };
        
        socket.onerror = (err) => {
            console.error("Error en WebSocket:", err);
            socket.close();
        };
    };

    // Vue se encarga automáticamente de cerrar la conexión cuando el usuario se va de la pantalla
    onUnmounted(() => {
        if (socket) {
            socket.onclose = null; // Evita que intente reconectar al salir
            socket.close();
            console.log("🔴 WebSocket cerrado limpiamente.");
        }
    });

    return { conectar };
}