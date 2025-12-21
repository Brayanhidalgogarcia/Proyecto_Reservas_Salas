<script setup>
import { ref } from 'vue';

const form = ref({
  username: "", 
  password: "",
  remember: false
});

const error = ref(null);
const cargando = ref(false);

async function login() {
  if (!form.value.username || !form.value.password) {
    error.value = "Por favor, completa todos los campos.";
    return;
  }
  
  cargando.value = true;
  error.value = null;

  try {
    console.log("Intentando iniciar sesión con:", form.value);
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    alert(`Bienvenido (simulado) ${form.value.username}`);

  } catch (err) {
    error.value = "Error al iniciar sesión. Verifica tus credenciales.";
    console.error("Error de login:", err);
  } finally {
    cargando.value = false;
  }
}
</script>

<template>
  <div class="login-container">
    <div class="left-side"></div>

    <div class="right-side">
      <div class="topbar">
        <img src="https://upload.wikimedia.org/wikipedia/commons/e/e9/Logo_de_la_UJAT.svg" alt="Logo UJAT">
        <span class="fw-bold fs-4">Universidad Juárez Autónoma de Tabasco</span>
      </div>

      <div class="form-box">
        <div class="form-box-inner">
          <h4>Inicia sesión aquí</h4>
          
          <div v-if="error" class="alert alert-danger">{{ error }}</div>

          <form @submit.prevent="login">
            <div class="mb-3">
              <label for="username" class="form-label">Usuario</label> 
              <input type="text" v-model="form.username" class="form-control" id="username" placeholder="Nombre de usuario">
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">Contraseña</label>
              <input type="password" v-model="form.password" class="form-control" id="password" placeholder="Contraseña">
            </div>

            <div class="d-flex justify-content-between align-items-center mb-3">
              <div class="form-check">
                <input class="form-check-input" type="checkbox" v-model="form.remember" id="remember">
                <label class="form-check-label" for="remember">Recuérdame</label>
              </div>
            </div>

            <button type="submit" class="btn btn-dark w-100" :disabled="cargando">
              {{ cargando ? 'Iniciando...' : 'Iniciar Sesión' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
.left-side {
    flex: 0.5;
    background: url('@/assets/imagenes/sesion.jpg') no-repeat center center; 
    background-size: cover;
    filter: brightness(0.8);
}

.right-side {
  flex: 0.5;
  display: flex;
  flex-direction: column;
  background: #fff;
}
.topbar {
  background-color: #005f86;
  color: white;
  padding: 20px 20px;
  display: flex;
  align-items: center;
}
.topbar img {
  height: 80px;
  margin-right: 30px;
}
.form-box {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow-y: auto;
  padding: 20px;
}
.form-box-inner {
  width: 100%;
  max-width: 420px;
}
.form-box-inner h4 {
  margin-bottom: 1.5rem;
}

:global(body) {
  margin: 0;
  height: 100vh;
  display: flex;
  font-family: Arial, sans-serif;
}
:global(#app) {
  width: 100%;
  height: 100%;
}

</style>
