<template>
  <div>
    <h1>Управление квизами</h1>

    <!-- Блок создания нового квиза -->
    <section>
      <h3>Создать новый квиз</h3>
      <form @submit.prevent="submitCreateQuiz">
        <input v-model="newQuiz.name" type="text" placeholder="Название квиза" required />

        <div v-for="(q, index) in newQuiz.questions" :key="index" style="margin-bottom: 10px">
          <div class="question-field">
            <span>{{ index + 1 }}</span>
            <input v-model="q.text" placeholder="Текст вопроса" required />
            <input v-model="q.answer" placeholder="Правильный ответ" required />
            <button
              type="button"
              @click="removeQuestion(index)"
              v-if="newQuiz.questions.length > 1"
            >
              Удалить
            </button>
          </div>
        </div>
        <div class="quiz-control-buttons">
          <button class="new" type="button" @click="addQuestion">Добавить еще вопрос</button>
          <button type="submit">Сохранить квиз</button>
        </div>
      </form>
    </section>

    <hr />

    <section v-if="editingQuiz">
      <h3>Редактировать квиз</h3>
      <form @submit.prevent="submitEditQuiz">
        <input v-model="editingQuiz.quiz_name" type="text" placeholder="Название квиза" required />

        <div
          v-for="(q, index) in editingQuiz.questions"
          :key="q.id || index"
          style="margin-bottom: 10px"
        >
          <div class="question-field">
            <span>{{ index + 1 }}</span>
            <input v-model="q.question" placeholder="Текст вопроса" required />
            <input v-model="q.answer.answer" placeholder="Правильный ответ" required />
            <button
              type="button"
              @click="removeEditQuestion(index)"
              v-if="editingQuiz.questions.length > 1"
            >
              Удалить
            </button>
          </div>
        </div>

        <div class="quiz-control-buttons">
          <button class="new" type="button" @click="addEditQuestion">Добавить еще вопрос</button>
          <button type="submit">Сохранить изменения</button>
          <button type="button" @click="cancelEdit">Отмена</button>
        </div>
      </form>
    </section>

    <hr v-if="editingQuiz" />

    <!-- Блок списка квизов -->
    <section>
      <h3>Список квизов</h3>

      <!-- Поиск (по доке query обязателен, иначе 400 ошибка) -->
      <form class="search-field" @submit.prevent="fetchQuizzes">
        <input v-model="searchQuery" placeholder="Поиск по названию" />
        <button type="submit">Найти</button>
      </form>

      <ul v-if="quizzes.length > 0">
        <li v-for="quiz in quizzes" :key="quiz.id">
          <strong>{{ quiz.quiz_name }}</strong> (Вопросов: {{ quiz.questions.length }})
          <button v-if="canManageQuiz(quiz)" @click="startEditQuiz(quiz)">Редактировать</button>
          <button v-if="canManageQuiz(quiz)" @click="deleteQuiz(quiz.id)">Удалить</button>
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
import { useAuthStore } from '../stores/auth'

// Состояние
const authStore = useAuthStore()
const quizzes = ref([])
const searchQuery = ref('')
const editingQuiz = ref(null)
const newQuiz = ref({
  name: '',
  questions: [{ text: '', answer: '' }],
})

const canManageQuiz = (quiz) => quiz.creator_id === authStore.userId

const createEmptyEditQuestion = (quizId) => ({
  id: null,
  quiz_id: quizId,
  question: '',
  answer: {
    id: null,
    answer: '',
  },
  type_dependent: null,
  question_type: 'text',
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
    if (editingQuiz.value?.id === quiz_id) {
      editingQuiz.value = null
    }
    fetchQuizzes()
  } catch (error) {
    console.error('Ошибка при удалении квиза:', error)
  }
}

const startEditQuiz = (quiz) => {
  editingQuiz.value = JSON.parse(JSON.stringify(quiz))
}

const cancelEdit = () => {
  editingQuiz.value = null
}

const addEditQuestion = () => {
  editingQuiz.value.questions.push(createEmptyEditQuestion(editingQuiz.value.id))
}

const removeEditQuestion = (index) => {
  editingQuiz.value.questions.splice(index, 1)
}

const submitEditQuiz = async () => {
  try {
    await api.post('/quiz/change', {
      quiz_id: editingQuiz.value.id,
      quiz_name: editingQuiz.value.quiz_name,
      questions: editingQuiz.value.questions,
    })
    alert('Квиз успешно изменен!')
    editingQuiz.value = null
    fetchQuizzes()
  } catch (error) {
    console.error('Ошибка при изменении квиза:', error)
    alert('Не удалось изменить квиз')
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
onMounted(async () => {
  await authStore.loadCurrentUser()
  await fetchQuizzes()
})
</script>

<style scoped>
form input {
  margin-bottom: 8px;
}
.question-field {
  display: flex;
  align-items: center;
  gap: 16px;
  text-align: center;
  margin-bottom: 16px;
}
.question-field > input,
.question-field > button,
.search-field input {
  margin-bottom: 0;
}
.question-field > button {
  width: 20%;
}
.quiz-control-buttons {
  display: flex;
  gap: 16px;
}
.quiz-control-buttons > .new {
  width: 30%;
}
.search-field {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}
ul button {
  margin-left: 16px;
}
</style>
