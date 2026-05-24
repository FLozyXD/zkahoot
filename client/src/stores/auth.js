import { defineStore } from 'pinia'
import api from '../api/index.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('auth_token') || null,
    username: localStorage.getItem('user_login') || null,
    authError: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(login, password) {
      try {
        const response = await api.post('/auth/get-token', { login, password })
        if (response.data.token) {
          this.token = response.data.token
          this.username = login
          localStorage.setItem('auth_token', this.token)
          localStorage.setItem('user_login', this.username)
          this.authError = null
          return true
        }
      } catch (error) {
        this.authError = error.response?.data?.cause || 'Ошибка при входе'
        return false
      }
    },
    async register(login, password) {
      try {
        const response = await api.post('/auth/register', { login, password })
        if (response.status === 200) {
          return await this.login(login, password)
        }
      } catch (error) {
        this.authError = error.response?.data?.cause || 'Ошибка при регистрации'
        return false
      }
    },
    async logout() {
      this.token = null
      this.username = null
      this.authError = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_login')
    },
  },
})
