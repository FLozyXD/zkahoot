import { defineStore } from 'pinia'
import api from '../api/index.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('auth_token') || null,
    username: localStorage.getItem('user_login') || null,
    userId: Number(localStorage.getItem('user_id')) || null,
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
          this.username = response.data.login || login
          this.userId = response.data.user_id
          localStorage.setItem('auth_token', this.token)
          localStorage.setItem('user_login', this.username)
          localStorage.setItem('user_id', this.userId)
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
    async loadCurrentUser() {
      if (!this.token || this.userId) return

      try {
        const response = await api.get('/auth/me')
        this.username = response.data.login
        this.userId = response.data.user_id
        localStorage.setItem('user_login', this.username)
        localStorage.setItem('user_id', this.userId)
      } catch (error) {
        this.authError = error.response?.data?.cause || 'Ошибка при получении пользователя'
      }
    },
    async changeLogin(login, password, new_login) {
      try {
        if (login === new_login) throw new Error('Новый логин должен отличаться от старого')
        const response = await api.post('/auth/change-login', {
          login,
          password,
          new_login,
        })
        if (response.status !== 200) throw new Error()
        await this.logout()
        return await this.login(new_login, password)
      } catch (error) {
        const cause = error.response?.data?.cause
        this.authError = error.message || cause || 'Ошибка при смене логина'
        return false
      }
    },
    async changePass(login, password, new_password) {
      try {
        if (password === new_password) throw new Error('Новый пароль должен отличаться от старого')
        const response = await api.post('/auth/change-password', {
          login,
          password,
          new_password,
        })
        if (response.status !== 200) throw new Error()
        await this.logout()
        return await this.login(login, new_password)
      } catch (error) {
        const cause = error.response?.data?.cause
        this.authError = error.message || cause || 'Ошибка при смене пароля'
        return false
      }
    },
    async logout() {
      this.token = null
      this.username = null
      this.userId = null
      this.authError = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_login')
      localStorage.removeItem('user_id')
    },
  },
})
