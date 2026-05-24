<template>
  <div>
    <h1>Добро пожаловать в zkahoot</h1>

    <div v-if="authStore.authError">
      <p>{{ authStore.authError }}</p>
    </div>

    <form @submit.prevent="onLogin">
      <h3>Вход</h3>
      <input v-model="loginForm.login"
             type="text"
             placeholder="Логин"
             required />
      <input v-model="loginForm.password"
             type="password"
             placeholder="Пароль"
             required />
      <button type="submit">Войти</button>
    </form>

    <hr />

    <form @submit.prevent="onRegister">
      <h3>Регистрация</h3>
      <input v-model="registerForm.login"
             type="text"
             placeholder="Новый логин"
             required />
      <input v-model="registerForm.password"
             type="password"
             placeholder="Новый пароль"
             required />
      <button type="submit">Зарегистрироваться</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
  authStore.authError = null
})

const loginForm = ref({ login: '', password: '' })
const registerForm = ref({ login: '', password: '' })

const onLogin = async () => {
  const success = await authStore.login(loginForm.value.login, loginForm.value.password)
  if (success) {
    router.push('/')
  }
}

const onRegister = async () => {
  const success = await authStore.register(registerForm.value.login, registerForm.value.password)
  if (success) {
    router.push('/')
  }
}
</script>

<style scoped>
  div > h1 {
    margin: 32px 0;
  }
</style>
