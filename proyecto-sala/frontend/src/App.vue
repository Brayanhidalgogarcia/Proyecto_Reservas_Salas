<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <!-- Estos son los enlaces de navegación principales de nuestra app -->
        <RouterLink to="/">Salas</RouterLink>
        <RouterLink to="/reservas">Mis Reservas</RouterLink>
      </nav>
    </div>
  </header>

  <!-- RouterView es el componente especial que renderizará la página
       correspondiente a la URL actual (ej. la vista de Salas o la de Reservas) -->
  <RouterView />
</template>

<style scoped>
/* Estilos simplificados para la navegación */
header {
  line-height: 1.5;
  max-height: 100vh;
  padding-bottom: 2rem;
  border-bottom: 1px solid #ddd;
  margin-bottom: 2rem;
}

nav {
  width: 100%;
  font-size: 1rem;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: hsla(160, 100%, 37%, 1);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}
</style>
