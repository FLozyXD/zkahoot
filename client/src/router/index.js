import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import QuizView from '../views/QuizView.vue'
import LobbyListView from '../views/LobbyListView.vue'
import CreateLobbyView from '../views/CreateLobbyView.vue'
import LobbyDetailView from '../views/LobbyDetailView.vue'
import GameView from '../views/GameView.vue'
import ResultsView from '../views/ResultsView.vue'
import SettingsView from '../views/SettingsView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresGuest: true },
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/quiz',
      name: 'quiz',
      component: QuizView,
      meta: { requiresAuth: true },
    },
    {
      path: '/lobbies',
      name: 'lobbies',
      component: LobbyListView,
      meta: { requiresAuth: true },
    },
    {
      path: '/lobbies/create',
      name: 'create-lobby',
      component: CreateLobbyView,
      meta: { requiresAuth: true },
    },
    {
      path: '/lobbies/:token',
      name: 'lobby-detail',
      component: LobbyDetailView,
      meta: { requiresAuth: true },
    },
    {
      path: '/lobbies/:token/play',
      name: 'lobby-game',
      component: GameView,
      meta: { requiresAuth: true },
    },
    {
      path: '/lobbies/:token/results',
      name: 'lobby-results',
      component: ResultsView,
      meta: { requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'user-settings',
      component: SettingsView,
      meta: { requiresAuth: true },
    },
  ],
})

// Навигационный гард для проверки токена
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Если страница требует авторизации, а токена нет - кидаем на логин
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // Если пользователь уже вошел, не пускаем его на страницу логина
    next('/')
  } else {
    next()
  }
})

export default router
