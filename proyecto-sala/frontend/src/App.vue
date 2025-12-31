<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-layout">
   
    <div class="topbar">
      <div class="logo-text">
       
        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e9/Logo_de_la_UJAT.svg" alt="Logo UJAT" class="logo-img">
        Universidad Juárez Autónoma de Tabasco
      </div>
      <div class="topbar-icons">
      
        <img src="https://cdn-icons-png.flaticon.com/512/1828/1828479.png" title="Configuración" class="icon">
        <img src="https://cdn-icons-png.flaticon.com/512/1077/1077114.png" title="Usuario" class="icon">
      </div>
    </div>

    <div class="container-fluid main-container">
      <div class="row flex-nowrap">
       
        <div class="col-auto col-md-3 col-xl-2 px-sm-2 px-0 sidebar">
          <div class="d-flex flex-column align-items-center align-items-sm-start px-3 pt-2 text-white min-vh-100">
            <ul class="nav nav-pills flex-column mb-sm-auto mb-0 align-items-center align-items-sm-start w-100" id="menu">
              <li class="nav-item w-100">
                <RouterLink to="/disponibilidad" class="nav-link align-middle px-0 text-dark">
                  <span class="ms-1 d-none d-sm-inline">Consultar Disponibilidad</span>
                </RouterLink>
              </li>
              <li class="nav-item w-100">
                <RouterLink to="/reservar" class="nav-link px-0 align-middle text-dark">
                  <span class="ms-1 d-none d-sm-inline">Apartar Sala Audiovisual</span>
                </RouterLink>
              </li>
              <li class="nav-item w-100">
                <RouterLink to="/reportes" class="nav-link px-0 align-middle text-dark">
                  <span class="ms-1 d-none d-sm-inline">Consultar Reportes</span>
                </RouterLink>
              </li>
              <!--
              <li class="nav-item w-100">
                <RouterLink to="/alta-usuario" class="nav-link px-0 align-middle text-dark">
                  <span class="ms-1 d-none d-sm-inline">Dar de Alta Usuario</span>
                </RouterLink>
              </li>
              -->
            </ul>
          </div>
        </div>

       
        <div class="col py-3 content-area">
          <RouterView />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

.topbar {
  background-color: #005f86;
  color: white;
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 80px;
}

.logo-text {
  font-weight: bold;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
}

.logo-img {
  height: 60px;
  margin-right: 15px;
}

.icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-left: 15px;
  cursor: pointer;
  filter: brightness(0) invert(1); 
}

.sidebar {
  background-color: #e9ecef;
  border-right: 1px solid #dee2e6;
}

.nav-link {
  padding: 15px 10px;
  font-size: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.nav-link:hover {
  background-color: #ced4da;
}

.router-link-active {
  background-color: #ced4da;
  font-weight: bold;
}

.content-area {
  background-color: #f8f9fa;
  min-height: calc(100vh - 80px);
}
</style>