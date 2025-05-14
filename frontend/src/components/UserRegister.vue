<template>
  <div class="auth-page">
    <h1>Регистрация компании</h1>
    <form @submit.prevent="registerUser">
      <div class="form-group">
        <label for="title">Название компании</label>
        <input type="text" id="title" v-model="title" required />
      </div>
      <div class="form-group">
        <label for="email">Электронная почта</label>
        <input type="email" id="email" v-model="email" required />
      </div>
      <div class="form-group">
        <label for="password">Пароль</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit" :disabled="isLoading">Зарегистрироваться</button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>
    <p class="login-link">
      Уже есть аккаунт? <router-link to="/login">Войти</router-link>
    </p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      title: "",
      email: "",
      password: "",
      errorMessage: "",
      isLoading: false,
    };
  },
  methods: {
    async registerUser() {
      this.isLoading = true;
      try {
        await axios.post(
          "http://127.0.0.1:8000/api/core/register/",
          {
            title: this.title,
            email: this.email,
            password: this.password,
          },
          {
            withCredentials: true, // сохраняем сессию
          }
        );

        this.$router.push("/login"); // после регистрации — переход на логин
      } catch (error) {
        this.errorMessage =
          error.response?.data?.error || "Ошибка регистрации. Попробуйте снова.";
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>



<style scoped>
/* Внешний фон страницы */
body {
  background-color: #f7f7f8;
  margin: 0;
  padding: 0;
}


.auth-page {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border-radius: 10px;
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 500px;
  box-sizing: border-box;
}

h1 {
  text-align: left;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 400;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

form input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 20px;
  background-color: #fff;
  margin-bottom: 15px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #535af4;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  box-sizing: border-box;
  margin-bottom: 15px;
}

button:hover {
  background-color: #3b43f2;
}

.error {
  color: red;
  font-size: 14px;
  text-align: center;
}

.login-link {
  text-align: center;
  margin-top: 10px;
}

.login-link a {
  color: #a0a0a0;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>