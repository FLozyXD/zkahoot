<template>
  <div>
    <h1>Управление квизами</h1>

    <!-- Блок создания нового квиза -->
    <section>
      <h2>Создать новый квиз</h2>
      <form @submit.prevent="submitCreateQuiz">
        <div>
          <label>Название квиза: </label>
          <input v-model="newQuiz.name" type="text" required />
        </div>

        <h3>Вопросы</h3>
        <div v-for="(q, index) in newQuiz.questions" :key="index" style="margin-bottom: 10px">
          <span>{{ index + 1 }}. </span>
          <input v-model="q.text" placeholder="Текст вопроса" required />
          <input v-model="q.answer" placeholder="Правильный ответ" required />
          <button type="button" @click="removeQuestion(index)" v-if="newQuiz.questions.length > 1">
            Удалить вопрос
          </button>
        </div>

        <button type="button" @click="addQuestion">Добавить еще вопрос</button>
        <br /><br />
        <button type="submit">Сохранить квиз</button>
      </form>
    </section>

    <hr />

    <!-- Блок списка квизов -->
    <section>
      <h2>Список квизов</h2>

      <!-- Поиск (по доке query обязателен, иначе 400 ошибка) -->
      <div>
        <input v-model="searchQuery" placeholder="Поиск по названию..." />
        <button @click="fetchQuizzes">Найти</button>
      </div>

      <ul v-if="quizzes.length > 0">
        <li v-for="quiz in quizzes" :key="quiz.id">
          <strong>{{ quiz.quiz_name }}</strong> (Вопросов: {{ quiz.questions.length }})
          <button @click="deleteQuiz(quiz.id)">Удалить</button>
          <!-- В будущем здесь появится кнопка "Создать лобби" -->
        </li>
      </ul>
      <p v-else>Квизы не найдены. Создайте свой первый квиз!</p>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'

// Состояние
const quizzes = ref([])
const searchQuery = ref('')
const newQuiz = ref({
  name: '',
  questions: [{ text: '', answer: '' }],
})

// Запрос списка квизов
const fetchQuizzes = async () => {
  try {
    const response = await api.get('/quiz/search', {
      params: { query: searchQuery.value },
    })
    quizzes.value = response.data
  } catch (error) {
    console.error('Ошибка при поиске квизов:', error)
  }
}

// Удаление квиза
const deleteQuiz = async (quiz_id) => {
  if (!confirm('Вы уверены, что хотите удалить этот квиз?')) return
  try {
    await api.delete('/quiz/delete', { data: { quiz_id } })
    fetchQuizzes()
  } catch (error) {
    console.error('Ошибка при удалении квиза:', error)
  }
}

// Управление формой создания
const addQuestion = () => {
  newQuiz.value.questions.push({ text: '', answer: '' })
}

const removeQuestion = (index) => {
  newQuiz.value.questions.splice(index, 1)
}

const submitCreateQuiz = async () => {
  try {
    await api.post('/quiz/register', newQuiz.value)
    // Сбрасываем форму после успешного создания
    newQuiz.value = { name: '', questions: [{ text: '', answer: '' }] }
    alert('Квиз успешно создан!')
    fetchQuizzes()
  } catch (error) {
    console.error('Ошибка при создании квиза:', error)
    alert('Не удалось создать квиз')
  }
}

// Загружаем список при открытии страницы (с пустым запросом ищем все)
onMounted(() => {
  fetchQuizzes()
})
</script>
