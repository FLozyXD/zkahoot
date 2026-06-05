<template>
  <div>
    <h1>Результаты игры</h1>

    <section>
      <h3>Скорборд</h3>
      <table v-if="scoreboard.length">
        <thead>
          <tr>
            <th>Место</th>
            <th>Игрок</th>
            <th>Счёт</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in scoreboard" :key="row.login">
            <td>{{ row.submitted ? index + 1 : '-' }}</td>
            <td>{{ row.login }}</td>
            <td>{{ row.correct }} / {{ row.total }}</td>
            <td>{{ row.submitted ? 'Сдал' : 'Играет' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>Скорборд пока недоступен</p>
      <p v-if="scoreboard.length && !allSubmitted">Ожидание ответов остальных игроков...</p>
    </section>

    <hr />

    <div v-if="!results.length">
      <p>Нет данных о ваших ответах</p>
      <button @click="goHome">На главную</button>
    </div>

    <div v-else>
      <p><strong>Ваш результат:</strong> {{ correctAnswersCount }} из {{ totalQuestionsCount }}</p>

      <div v-for="(question, index) in questions" :key="index">
        <p>
          <strong>Вопрос {{ index + 1 }}:</strong> {{ question.question }}
        </p>
        <p>
          Ваш ответ: <em>{{ userAnswers[index] }}</em>
          <span v-if="results[index]"> (Верно)</span>
          <span v-else> (Неверно)</span>
        </p>
        <hr />
      </div>

      <div class="control">
        <button @click="goHome">Вернуться на главную</button>
        <button @click="goLobbies">Список лобби</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { onBeforeRouteLeave, useRouter } from 'vue-router'
import { lobbyApi } from '../api/lobby'

const router = useRouter()
const results = ref([])
const questions = ref([])
const userAnswers = ref([])
const scoreboard = ref([])
let scoreboardInterval = null
let hasLeftLobby = false

onMounted(() => {
  if (history.state && history.state.results) {
    results.value = JSON.parse(history.state.results)
    questions.value = JSON.parse(history.state.questions)
    userAnswers.value = JSON.parse(history.state.userAnswers)
    scoreboard.value = JSON.parse(history.state.scoreboard || '[]')
  }
  fetchScoreboard()
  scoreboardInterval = setInterval(fetchScoreboard, 2000)
})

const correctAnswersCount = computed(() => results.value.filter((isCorrect) => isCorrect).length)
const totalQuestionsCount = computed(() => results.value.length)
const allSubmitted = computed(
  () => scoreboard.value.length > 0 && scoreboard.value.every((row) => row.submitted),
)

const fetchScoreboard = async () => {
  try {
    const response = await lobbyApi.scoreboard()
    scoreboard.value = response.data
  } catch (error) {
    console.error('Ошибка при получении скорборда:', error)
  }
}

const leaveLobby = async () => {
  if (hasLeftLobby) return
  hasLeftLobby = true

  try {
    await lobbyApi.exit()
  } catch (error) {
    console.error('Ошибка при выходе из лобби после игры:', error)
  }
}

const goHome = async () => {
  await leaveLobby()
  router.push('/')
}

const goLobbies = async () => {
  await leaveLobby()
  router.push('/lobbies')
}

onUnmounted(() => {
  if (scoreboardInterval) clearInterval(scoreboardInterval)
})

onBeforeRouteLeave(async () => {
  if (scoreboardInterval) clearInterval(scoreboardInterval)
  await leaveLobby()
})
</script>

<style scoped>
.control {
  display: flex;
  gap: 16px;
}
table {
  margin-top: 16px;
}
</style>
