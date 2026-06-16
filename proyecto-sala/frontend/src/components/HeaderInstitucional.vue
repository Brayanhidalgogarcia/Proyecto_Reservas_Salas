<template>
  <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 pb-3 border-bottom">
    
    <div class="mb-3 mb-md-0">
        <h2 class="fw-bold text-dark mb-0">
            <i v-if="icono" :class="[icono, 'text-primary', 'me-2']"></i>
            {{ titulo }}
        </h2>
        <p v-if="subtitulo" class="text-muted small mb-0 mt-1">{{ subtitulo }}</p>
    </div>
    
    <div class="d-flex gap-2 align-items-center">
        <slot name="acciones"></slot>
    </div>

  </div>
</template>

<script setup>
defineProps({
  titulo: {
    type: String,
    required: true
  },
  subtitulo: {
    type: String,
    default: ''
  },
  icono: {
    type: String,
    default: ''
  }
});
</script>