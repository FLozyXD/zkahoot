<template>
  <div>
    <h1>Результаты игры</h1>

    <div v-if="!results.length">
      <p>Нет данных о результатах</p>
      <button @click="goHome">На главную</button>
    </div>

    <div v-else>
      <p>
        <strong>Ваш результат:</strong> {{ correctAnswersCount }} из {{ totalQuestionsCount }}
      </p>

      <div v-for="(question, index) in questions" :key="index">
        <p><strong>Вопрос {{ index + 1 }}:</strong> {{ question.question }}</p>
        <p>
          Ваш ответ: <em>{{ userAnswers[index] }}</em>
          <span v-if="results[index]"> (Верно)</span>
          <span v-else> (Неверно)</span>
        </p>
        <hr />
      </div>

      <div>
        <button @click="goHome">Вернуться на главную</button>
        <button @click="goLobbies">Список лобби</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const results = ref([])
const questions = ref([])
const userAnswers = ref([])

onMounted(() => {
  if (history.state && history.state.results) {
    results.value = JSON.parse(history.state.results)
    questions.value = JSON.parse(history.state.questions)
    userAnswers.value = JSON.parse(history.state.userAnswers)
  }
})

const correctAnswersCount = computed(() => results.value.filter(isCorrect => isCorrect).length)
const totalQuestionsCount = computed(() => results.value.length)

const goHome = () => {
  router.push('/')
}

const goLobbies = () => {
  router.push('/lobbies')
}
</script>
