<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

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
    
    const response = await fetch('http://127.0.0.1:8000/api/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: form.value.username,
            password: form.value.password
        })
    });

  
    const data = await response.json();

    if (response.ok) {
       
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        
       
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('is_superuser', data.is_superuser); 
        
        
        const nombreMostrar = data.nombre_completo || data.username;
        localStorage.setItem('nombre_usuario', nombreMostrar);
        localStorage.setItem('user_division', data.division || '');

        
        window.location.href = '/disponibilidad'; 

    } else {
        
        error.value = data.detail || "Usuario o contraseña incorrectos.";
    }

  } catch (err) {
    error.value = "Error de conexión. Verifica que el servidor Backend esté encendido.";
    console.error("Error de red:", err);
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
              <input type="text" v-model="form.username" class="form-control" id="username" placeholder="Tu usuario administrativo">
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">Contraseña</label>
              <input type="password" v-model="form.password" class="form-control" id="password" placeholder="Tu contraseña">
            </div>

            <div class="d-flex justify-content-between align-items-center mb-3">
              <!---<div class="form-check">
                <input class="form-check-input" type="checkbox" v-model="form.remember" id="remember">
                <label class="form-check-label" for="remember">Recordarme</label>
              </div>-->
            </div>

            <button type="submit" class="btn btn-dark w-100" :disabled="cargando">
              <span v-if="cargando" class="spinner-border spinner-border-sm me-2"></span>
              {{ cargando ? 'Verificando...' : 'Iniciar Sesión' }}
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
 
    background-color: #f0f2f5; 
}


@media (max-width: 768px) {
    .left-side { display: none; }
    .right-side { flex: 1; }
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
  height: 60px; 
  margin-right: 20px;
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
  color: #333;
}


:global(body) {
  margin: 0;
  padding: 0;
  height: 100vh;
  font-family: Arial, sans-serif;
}
:global(#app) {
  width: 100%;
  height: 100%;
}
</style>