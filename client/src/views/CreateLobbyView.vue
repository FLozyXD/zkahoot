<template>
  <div>
    <h1>Создание лобби</h1>

    <form @submit.prevent="createLobby">
      <div>
        <input v-model="name" placeholder="Название лобби" required />
        <div class="choose-quiz-field">
          <input
            v-model="quizSearchQuery"
            placeholder="Название квиза"
            @keydown.enter.prevent="fetchQuizzes"
          />
          <button type="button" @click="fetchQuizzes">Найти</button>
        </div>

        <div v-if="quizzes.length > 0">
          <ul
            v-for="quiz in quizzes"
            class="quizzes"
            :key="quiz.id"
            @click="selectedQuizId = quiz.id"
          >
            <li>
              {{ quiz.quiz_name }} ({{ quiz.questions.length }} вопр.)
              <span v-if="selectedQuizId === quiz.id">(Выбран)</span>
            </li>
          </ul>
        </div>
        <p v-else class="not-found">Квиз не найден!</p>
      </div>

      <div class="control-buttons">
        <button type="submit" :disabled="!selectedQuizId || !name">Создать</button>
        <button
          class="back"
          type="button"
          @click="$router.push('/lobbies')"
          style="margin-left: 10px"
        >
          К списку лобби
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { lobbyApi, quizApi } from '../api/lobby'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
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
  if (route.query.quizId) {
    selectedQuizId.value = parseInt(route.query.quizId)
    quizSearchQuery.value = route.query.quizName || ''
  }
  fetchQuizzes()
})
</script>

<style scoped>
.choose-quiz-field,
.control-buttons {
  display: flex;
  gap: 16px;
}
.choose-quiz-field,
span,
ul {
  margin: 0;
}
.choose-quiz-field > * {
  margin-bottom: 0;
}
.control-buttons > .back {
  width: 30%;
}
.not-found,
li {
  margin: 32px 0;
}
li {
  cursor: pointer;
}
</style>
