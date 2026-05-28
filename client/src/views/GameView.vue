<template>
  <div>
    <div v-if="loading">
      <p>Загрузка вопросов...</p>
    </div>
    <div v-else-if="lobby">
      <h1>Игра: {{ lobby.quiz.quiz_name }}</h1>
      <form @submit.prevent="submitAnswers">
        <div v-for="(question, index) in lobby.quiz.questions" :key="question.id || index">
          <p>
            <strong>Вопрос {{ index + 1 }}:</strong> {{ question.question }}
          </p>
          <input v-model="answers[index]" type="text" placeholder="Ваш ответ" />
        </div>
        <button type="submit" :disabled="submitting">
          {{ submitting ? 'Отправка...' : 'Сдать ответы' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { lobbyApi } from '../api/lobby'

const route = useRoute()
const router = useRouter()

const lobby = ref(null)
const loading = ref(true)
const submitting = ref(false)
const answers = ref([])

onMounted(async () => {
  try {
    const response = await lobbyApi.getInfo()
    lobby.value = response.data
    const power = lobby.value.quiz.questions.length
    answers.value = Array.from({ length: power }).fill('')
    loading.value = false
  } catch (error) {
    console.error('Ошибка при получении данных игры:', error)
    router.push('/lobbies')
  }
})

const submitAnswers = async () => {
  if (!confirm('Вы уверены, что хотите сдать ответы и выйти?')) return

  submitting.value = true
  try {
    const answers_ = answers.value.map((a) => a.trim())
    const response = await lobbyApi.compare(answers_)
    const results = response.data

    router.push({
      name: 'lobby-results',
      params: { token: route.params.token },
      state: {
        results: JSON.stringify(results),
        questions: JSON.stringify(lobby.value.quiz.questions),
        userAnswers: JSON.stringify(answers_),
      },
    })
  } catch (error) {
    console.error('Ошибка при сдаче ответов:', error)
    alert('Не удалось сдать ответы!')
  } finally {
    await lobbyApi.exit()
    submitting.value = false
  }
}
</script>
