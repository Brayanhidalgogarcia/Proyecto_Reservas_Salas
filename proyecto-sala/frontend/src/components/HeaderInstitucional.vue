<script setup>
/**
 * @file HeaderInstitucional.vue
 * @description Componente UI global para estandarizar los encabezados de todas las vistas.
 * Implementa un título, subtítulo descriptivo, un icono dinámico y una ranura (slot)
 * para inyectar botones de acción o controles (ej. fechas) alineados a la derecha.
 */

// ==========================================
// 1. PROPIEDADES (PROPS)
// ==========================================
defineProps({
  /** * Título principal de la vista (Ej. 'Disponibilidad') 
   */
  titulo: {
    type: String,
    required: true
  },
  /** * Breve descripción del propósito del módulo debajo del título. 
   */
  subtitulo: {
    type: String,
    default: ''
  },
  /** * Clase CSS del catálogo de Bootstrap Icons (Ej. 'bi-calendar-check').
   * Se renderiza automáticamente con el color institucional.
   */
  icono: {
    type: String,
    default: ''
  }
});
</script>

<template>
  <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 pb-3 border-bottom border-light-subtle">
    
    <div class="mb-3 mb-md-0">
        <h2 class="fw-bold text-dark mb-0 d-flex align-items-center">
            <i v-if="icono" :class="[icono, 'text-primary-custom', 'me-2']"></i>
            {{ titulo }}
        </h2>
        <p v-if="subtitulo" class="text-muted small mb-0 mt-1">{{ subtitulo }}</p>
    </div>
    
    <div class="d-flex gap-2 align-items-center">
        <slot name="acciones"></slot>
    </div>

  </div>
</template>

<style scoped>
/* Forzamos el color institucional exclusivo para el icono del encabezado */
.text-primary-custom {
    color: #005f86 !important;
}
</style>