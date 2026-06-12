<script setup>
import { ref, shallowRef } from 'vue';

// Importación de los subcomponentes
import TabEdificios from '@/components/catalogos/TabEdificios.vue';
import TabSalas from '@/components/catalogos/TabSalas.vue';
import TabMaestros from '@/components/catalogos/TabMaestros.vue';
import TabAsignaturas from '@/components/catalogos/TabAsignaturas.vue';

// Estado reactivo para controlar qué pestaña está activa
const tabActiva = ref('edificios');

// Mapeo dinámico de componentes para Vue
const componentes = {
    edificios: TabEdificios,
    salas: TabSalas,
    maestros: TabMaestros,
    asignaturas: TabAsignaturas
};
</script>

<template>
  <div class="container-fluid px-4 py-4 d-flex justify-content-center">
    
    <div class="w-100" style="max-width: 1200px;">
        
        <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
                <h2 class="fw-bold text-dark mb-0">
                    <i class="bi bi-database-fill-gear text-primary me-2"></i>Gestión de Catálogos
                </h2>
                <p class="text-muted small mb-0 mt-1">Administración centralizada de infraestructura y padrón académico.</p>
            </div>
        </div>

        <div class="card shadow-sm border-0 rounded-3 bg-white overflow-hidden">
            
            <div class="card-header bg-light border-bottom p-0">
                <ul class="nav nav-tabs nav-fill border-0" style="margin-bottom: -1px;">
                    <li class="nav-item">
                        <button 
                            class="nav-link fw-bold border-0 py-3 rounded-0 transition-all"
                            :class="tabActiva === 'edificios' ? 'active-tab' : 'text-muted hover-tab'"
                            @click="tabActiva = 'edificios'"
                        >
                            <i class="bi bi-building me-2"></i>Edificios
                        </button>
                    </li>
                    <li class="nav-item">
                        <button 
                            class="nav-link fw-bold border-0 py-3 rounded-0 transition-all"
                            :class="tabActiva === 'salas' ? 'active-tab' : 'text-muted hover-tab'"
                            @click="tabActiva = 'salas'"
                        >
                            <i class="bi bi-door-open-fill me-2"></i>Salas y Espacios
                        </button>
                    </li>
                    <li class="nav-item">
                        <button 
                            class="nav-link fw-bold border-0 py-3 rounded-0 transition-all"
                            :class="tabActiva === 'maestros' ? 'active-tab' : 'text-muted hover-tab'"
                            @click="tabActiva = 'maestros'"
                        >
                            <i class="bi bi-person-badge-fill me-2"></i>Padrón Docente
                        </button>
                    </li>
                    <li class="nav-item">
                        <button 
                            class="nav-link fw-bold border-0 py-3 rounded-0 transition-all"
                            :class="tabActiva === 'asignaturas' ? 'active-tab' : 'text-muted hover-tab'"
                            @click="tabActiva = 'asignaturas'"
                        >
                            <i class="bi bi-journal-bookmark-fill me-2"></i>Asignaturas
                        </button>
                    </li>
                </ul>
            </div>

            <div class="card-body p-0 bg-white" style="min-height: 400px;">
                <transition name="fade" mode="out-in">
                    <component :is="componentes[tabActiva]"></component>
                </transition>
            </div>

        </div>
    </div>
  </div>
</template>

<style scoped>
/* Color y diseño institucional para las pestañas */
.text-primary { color: #005f86 !important; }

.transition-all { transition: all 0.2s ease; }

.hover-tab:hover {
    background-color: #f8f9fa;
    color: #005f86 !important;
}

.active-tab {
    background-color: #ffffff;
    color: #005f86 !important;
    border-top: 3px solid #005f86 !important;
    border-bottom: 1px solid #ffffff !important;
}

/* Transición suave al cambiar de pestaña */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>