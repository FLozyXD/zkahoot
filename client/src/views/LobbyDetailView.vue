<template>
  <div>
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="lobby">
      <h1>Лобби: {{ lobby.name }}</h1>
      <p>
        Код для входа: <strong>{{ lobby.token }}</strong>
      </p>
      <p>Квиз: {{ lobby.quiz.quiz_name }}</p>

      <h3>Игроки ({{ lobby.users.length }}):</h3>
      <ul>
        <li v-for="userLogin in lobby.users" :key="userLogin">
          {{ userLogin }} <span v-if="isOwner(userLogin)"> (Организатор)</span>
        </li>
      </ul>

      <div v-if="isOwner(authStore.login)">
        <button @click="startGame" :disabled="starting">Начать игру</button>
      </div>
      <div v-else>
        <p v-if="gameStarted" style="color: green; font-weight: bold">ИГРА НАЧАЛАСЬ!</p>
        <p v-else>Ожидание начала игры организатором...</p>
      </div>

      <p v-if="statusMessage" style="margin-top: 10px; color: blue">{{ statusMessage }}</p>

      <button @click="leaveLobby" style="margin-top: 20px">Покинуть лобби</button>
    </div>
    <div v-else>
      <p>Лобби не найдено или вы из него вышли.</p>
      <router-link to="/lobbies">Вернуться к списку</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { lobbyApi } from '../api/lobby'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const lobby = ref(null)
const loading = ref(true)
const starting = ref(false)
const statusMessage = ref('')
const gameStarted = ref(false)
let infoInterval = null
let hasLeftLobby = false

const fetchInfo = async () => {
  try {
    const response = await lobbyApi.getInfo()
    lobby.value = response.data
    loading.value = false
  } catch (error) {
    console.error('Ошибка при получении инфо о лобби:', error)
    if (error.response?.status === 404) {
      router.push('/lobbies')
    }
  }
}

const isOwner = (login) => {
  // Мы предположили, что первый в списке - владелец
  return lobby.value?.users[0] === login
}

const startGame = async () => {
  starting.value = true
  statusMessage.value = ''
  try {
    await lobbyApi.run()
    statusMessage.value = 'Игра успешно запущена!'
  } catch (error) {
    console.error('Ошибка при запуске игры:', error)
    statusMessage.value = 'Не удалось запустить игру.'
  } finally {
    starting.value = false
  }
}

const leaveLobby = async () => {
  hasLeftLobby = true
  try {
    await lobbyApi.exit()
    router.push('/lobbies')
  } catch (error) {
    console.error('Ошибка при выходе:', error)
    router.push('/lobbies')
  }
}

const exitLobbyOnLeave = async () => {
  if (hasLeftLobby || !lobby.value || !authStore.isAuthenticated) return

  hasLeftLobby = true
  try {
    await lobbyApi.exit()
  } catch (error) {
    console.error('Ошибка при автоматическом выходе из лобби:', error)
  }
}

const waitForStart = async () => {
  if (isOwner(authStore.login)) return

  try {
    const response = await lobbyApi.pollRunning(route.params.token)
    if (response.status === 200) {
      gameStarted.value = true
      statusMessage.value = 'Игра началась!'
    } else if (response.status === 202) {
      setTimeout(waitForStart, 2000)
    }
  } catch (error) {
    console.error('Ошибка при ожидании начала:', error)
    setTimeout(waitForStart, 2000)
  }
}

onMounted(async () => {
  await fetchInfo()
  // Опрашиваем список игроков каждые 3 секунды
  infoInterval = setInterval(fetchInfo, 3000)

  if (lobby.value && !isOwner(authStore.login)) {
    waitForStart()
  }
})

onUnmounted(() => {
  if (infoInterval) clearInterval(infoInterval)
})

onBeforeRouteLeave(async () => {
  if (infoInterval) clearInterval(infoInterval)
  await exitLobbyOnLeave()
})
</script>
