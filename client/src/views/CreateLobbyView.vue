<template>
  <div>
    <h1>Создание лобби</h1>

    <form @submit.prevent="createLobby">
      <div style="margin-bottom: 10px">
        <label>Название лобби: </label>
        <input v-model="name" required />
      </div>

      <div style="margin-bottom: 20px">
        <h3>Выберите квиз</h3>
        <div style="margin-bottom: 10px">
          <input v-model="quizSearchQuery" placeholder="Поиск квиза..." />
          <button type="button" @click="fetchQuizzes">Найти</button>
        </div>

        <div
          v-if="quizzes.length > 0"
          style="max-height: 200px; overflow-y: auto; border: 1px solid #eee; padding: 10px"
        >
          <div
            v-for="quiz in quizzes"
            :key="quiz.id"
            @click="selectedQuizId = quiz.id"
            :style="{
              padding: '5px',
              cursor: 'pointer',
              backgroundColor: selectedQuizId === quiz.id ? '#e0e0e0' : 'transparent',
            }"
          >
            {{ quiz.quiz_name }} ({{ quiz.questions.length }} вопр.)
          </div>
        </div>
        <p v-else>Квизы не найдены. Пожалуйста, создайте квиз на странице "Квизы".</p>
      </div>

      <button type="submit" :disabled="!selectedQuizId || !name">Создать</button>
      <button type="button" @click="$router.push('/lobbies')" style="margin-left: 10px">
        Отмена
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { lobbyApi, quizApi } from '../api/lobby'
import { useRouter } from 'vue-router'

const router = useRouter()
const name = ref('')
const selectedQuizId = ref(null)
const quizzes = ref([])
const quizSearchQuery = ref('')

const fetchQuizzes = async () => {
  try {
    const response = await quizApi.search(quizSearchQuery.value)
    quizzes.value = response.data
  } catch (error) {
    console.error('Ошибка при поиске квизов:', error)
  }
}

const createLobby = async () => {
  if (!selectedQuizId.value || !name.value) return
  try {
    const response = await lobbyApi.create(name.value, selectedQuizId.value)
    const token = response.data.token
    router.push(`/lobbies/${token}`)
  } catch (error) {
    console.error('Ошибка при создании лобби:', error)
    alert('Не удалось создать лобби. Возможно, вы уже состоите в другом лобби.')
  }
}

onMounted(() => {
  fetchQuizzes()
})
</script>
