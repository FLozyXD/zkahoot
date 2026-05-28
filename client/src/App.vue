<template>
  <div>
    <!-- Навигация видна только авторизованным пользователям -->
    <nav v-if="authStore.isAuthenticated">
      <router-link to="/">Главная</router-link>
      <router-link to="/quiz">Квизы</router-link>
      <router-link to="/lobbies">Лобби</router-link>
      <router-link to="/settings">Настройки</router-link>
      <div>
        <span>{{ authStore.username }}</span>
        <button @click="onLogout">Выйти</button>
      </div>
    </nav>
    <hr v-if="authStore.isAuthenticated" />
    <router-view />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import { lobbyApi } from './api/lobby'

const authStore = useAuthStore()
const router = useRouter()

const onLogout = async () => {
  if (router.currentRoute.value.name === 'lobby-detail') {
    try {
      await lobbyApi.exit()
    } catch (error) {
      console.error('Ошибка при выходе из лобби перед logout:', error)
    }
  }

  authStore.logout()
  router.push('/login')
}
</script>

<style>
.color-red {
  color: #d93526;
}
* {
  margin: 8px;
}
nav,
nav > div {
  display: flex;
  align-items: center;
}
nav > div {
  gap: 32px;
}
</style>
