<template>
  <div>
    <!-- Навигация видна только авторизованным пользователям -->
    <nav v-if="authStore.isAuthenticated">
      <router-link to="/">Главная</router-link> | 
      <button @click="onLogout">Выйти</button>
    </nav>
    <hr v-if="authStore.isAuthenticated" />

    <!-- Сюда подставляются наши страницы (LoginView или HomeView) -->
    <router-view />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const onLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>