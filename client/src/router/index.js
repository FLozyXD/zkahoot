import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes:[
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    }
  ]
})

// Навигационный гард для проверки токена
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Если страница требует авторизации, а токена нет - кидаем на логин
    next('/login');
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // Если пользователь уже вошел, не пускаем его на страницу логина
    next('/');
  } else {
    next();
  }
});

export default router