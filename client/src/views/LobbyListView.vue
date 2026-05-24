<template>
  <div>
    <h1>Список лобби</h1>

    <div class="create">
      <router-link to="/lobbies/create">
        <button>Создать лобби</button>
      </router-link>
    </div>

    <section>
      <h3>Присоединиться по коду</h3>
      <div>
        <input v-model="joinToken" placeholder="Код лобби" />
        <button @click="joinByToken">Присоединиться</button>
      </div>
      <p v-if="joinError" class="color-red">{{ joinError }}</p>
    </section>

    <section class="lobbies">
      <h3>Доступные лобби</h3>
      <div>
        <input v-model="searchQuery" placeholder="Поиск по названию..." />
        <button @click="fetchLobbies">Найти</button>
      </div>

      <ul v-if="lobbies.length > 0">
        <li v-for="lobby in lobbies" :key="lobby.token">
          <strong>{{ lobby.name }}</strong> (Квиз: {{ lobby.quiz.quiz_name }})
          <br />
          Игроков: {{ lobby.users.length }}
          <button @click="joinLobby(lobby.token)" style="margin-left: 10px;">Войти</button>
        </li>
      </ul>
      <p v-else>Лобби не найдены</p>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { lobbyApi } from '../api/lobby';
import { useRouter } from 'vue-router';

const router = useRouter();
const lobbies = ref([]);
const searchQuery = ref('');
const joinToken = ref('');
const joinError = ref('');

const fetchLobbies = async () => {
  try {
    const response = await lobbyApi.search(searchQuery.value);
    lobbies.value = response.data;
  } catch (error) {
    console.error('Ошибка при поиске лобби:', error);
  }
};

const joinLobby = async (token) => {
  try {
    await lobbyApi.join(token);
    router.push(`/lobbies/${token}`);
  } catch (error) {
    console.error('Ошибка при входе в лобби:', error);
    alert('Не удалось войти в лобби. Возможно, оно уже запущено или вы уже в другом лобби.');
  }
};

const joinByToken = async () => {
  if (!joinToken.value) return;
  joinError.value = '';
  try {
    await lobbyApi.join(joinToken.value);
    router.push(`/lobbies/${joinToken.value}`);
  } catch (error) {
    joinError.value = 'Лобби не найдено или произошла ошибка';
    console.error('Ошибка при входе по токену:', error);
  }
};

onMounted(() => {
  fetchLobbies();
});
</script>

<style scoped>
  .create {
    margin: 32px 0;
  }
  section > div {
    display: flex;
    gap: 16px;
    align-items: stretch;
  }
  section > div > input {
    margin-bottom: 0;
  }
  .lobbies > ul, .lobbies p {
    margin-top: 16px;
  }
</style>
