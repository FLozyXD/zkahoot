<template>
  <div>
    <h1>Настройки аккаунта</h1>

    <div v-if="status_ || authStore.authError">
      <p>{{ status_ || authStore.authError }}</p>
    </div>

    <form @submit.prevent="changeLogin">
      <h3>Изменить логин</h3>
      <input v-model="changeLoginForm.new_login"
             type="text"
             placeholder="Новый логин"
             required /><br />
      <input v-model="changeLoginForm.password"
             type="password"
             placeholder="Пароль"
             required /><br />
      <button type="submit">Применить</button>
    </form>

    <hr />

    <form @submit.prevent="changePass">
      <h3>Изменить пароль</h3>
      <input v-model="changePassForm.password"
             type="password"
             placeholder="Старый пароль"
             required /><br />
      <input v-model="changePassForm.new_password"
             type="password"
             placeholder="Новый пароль"
             required /><br />
      <button type="submit">Применить</button>
    </form>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useAuthStore } from '../stores/auth'

  const authStore = useAuthStore()
  const status_ = ref(null)

  const resetMessages = () => {
    authStore.authError = null
    status_.value = null
  }

  const resetLoginForm = () => {
    changeLoginForm.value.login = authStore.username
    changeLoginForm.value.password = ''
    changeLoginForm.value.new_login = ''
  }
  const changeLoginForm = ref({})

  const resetPassForm = () => {
    changePassForm.value.login = authStore.username
    changePassForm.value.password = ''
    changePassForm.value.new_password = ''
  }
  const changePassForm = ref({})

  onMounted(() => {
    resetMessages()
    resetLoginForm()
    resetPassForm()
  })

  const changeLogin = async () => {
    resetMessages()
    const unpacked = Object.values(changeLoginForm.value)
    const response = await authStore.changeLogin(...unpacked)
    if (!response)
      return
    resetLoginForm()
    status_.value = 'Логин успешно изменен!'
  }

  const changePass = async () => {
    resetMessages()
    const unpacked = Object.values(changePassForm.value)
    const response = await authStore.changePass(...unpacked)
    if (!response)
      return
    resetPassForm()
    status_.value = 'Пароль успешно изменен!'
  }
</script>
