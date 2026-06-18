<script setup>
/**
 * @file GestionCatalogosView.vue
 * @description Vista principal para la administración de catálogos del sistema.
 * Actúa como un contenedor (wrapper) que implementa un sistema de pestañas dinámicas 
 * para gestionar Edificios, Salas, Maestros y Asignaturas sin recargar la página.
 */

// ==========================================
// 1. IMPORTS
// ==========================================
import { ref } from 'vue';
import HeaderInstitucional from '@/components/HeaderInstitucional.vue';

// Importación de los subcomponentes del módulo
import TabEdificios from '@/components/catalogos/TabEdificios.vue';
import TabSalas from '@/components/catalogos/TabSalas.vue';
import TabMaestros from '@/components/catalogos/TabMaestros.vue';
import TabAsignaturas from '@/components/catalogos/TabAsignaturas.vue';

// ==========================================
// 2. CONFIGURACIÓN Y COMPOSABLES
// ==========================================

/**
 * Diccionario estático que mapea los identificadores de texto
 * con los componentes reales importados. Es consumido por <component :is="...">.
 */
const componentes = {
    edificios: TabEdificios,
    salas: TabSalas,
    maestros: TabMaestros,
    asignaturas: TabAsignaturas
};

// ==========================================
// 3. ESTADO REACTIVO (Variables)
// ==========================================

/**
 * Controla qué pestaña (y por ende, qué subcomponente) se está renderizando actualmente.
 * @type {import('vue').Ref<string>}
 */
const tabActiva = ref('edificios');

// ==========================================
// 4, 5, 6. COMPUTADAS, MÉTODOS Y CICLO DE VIDA
// ==========================================
// (La lógica pesada está delegada a cada subcomponente respectivo)
</script>

<template>
  <div class="container-fluid px-4 py-4">
    
    <HeaderInstitucional 
        titulo="Gestión de Catálogos" 
        subtitulo="Administración centralizada de infraestructura y padrón académico."
        icono="bi-database-fill-gear"
    />

    <div class="row justify-content-center mt-2">
        <div class="col-12 col-xl-11">

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
  </div>
</template>

<style scoped>
/* Transiciones suaves */
.transition-all { transition: all 0.2s ease; }

/* Estilos inactivos (Hover) */
.hover-tab:hover {
    background-color: #f8f9fa;
    color: #005f86 !important;
}

/* Estilos de pestaña activa (Color Institucional) */
.active-tab {
    background-color: #ffffff;
    color: #005f86 !important;
    border-top: 3px solid #005f86 !important;
    border-bottom: 1px solid #ffffff !important;
}

/* Transición de fundido para el intercambio de componentes Vue */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>