<template>
  <div>
    <h1>Добро пожаловать в Quiz App</h1>

    <div v-if="authStore.authError">
      <p>Ошибка: {{ authStore.authError }}</p>
    </div>

    <form @submit.prevent="onLogin">
      <h2>Вход</h2>
      <div>
        <label>Логин:</label>
        <input v-model="loginForm.login" type="text" required />
      </div>
      <div>
        <label>Пароль:</label>
        <input v-model="loginForm.password" type="password" required />
      </div>
      <button type="submit">Войти</button>
    </form>

    <hr />

    <form @submit.prevent="onRegister">
      <h2>Регистрация</h2>
      <div>
        <label>Новый логин:</label>
        <input v-model="registerForm.login" type="text" required />
      </div>
      <div>
        <label>Новый пароль:</label>
        <input v-model="registerForm.password" type="password" required />
      </div>
      <button type="submit">Зарегистрироваться</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

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
