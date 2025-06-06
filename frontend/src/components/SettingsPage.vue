<template>
  <div class="settings-page">
    <h1>Настройки компании</h1>

    <div class="company-info">
      <h2>Основная информация</h2>
      <form @submit.prevent="updateCompanyInfo">
        <div class="form-group">
          <label>Название компании</label>
          <input v-model="companyTitle" type="text" required />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="companyEmail" type="email" required />
        </div>
        <div class="form-group">
          <label>Старый пароль</label>
          <input v-model="oldPassword" type="password" />
        </div>
        <div class="form-group">
          <label>Новый пароль</label>
          <input v-model="newPassword" type="password" />
        </div>

        <button type="submit" class="save-button">Сохранить изменения</button>
      </form>
    </div>

    <div class="subusers-section">
      <h2>Пользователи</h2>
      <div class="subusers-list">
        <div v-for="subuser in subusers" :key="subuser.id" class="subuser-item">
          {{ subuser.email }}
          <button class="delete-btn" @click="deleteSubuser(subuser.id)">✕</button>
        </div>
      </div>

      <div class="add-subuser-form">
        <h3>Добавить пользователя</h3>
        <form @submit.prevent="addSubuser">
          <div class="form-group">
            <label>Email</label>
            <input v-model="newSubuserEmail" type="email" required />
          </div>
          <div class="form-group">
            <label>Пароль</label>
            <input v-model="newSubuserPassword" type="password" required />
          </div>

          <button type="submit" class="add-button">Добавить</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/axios";

export default {
  name: "SettingsPage",
  data() {
    return {
      companyTitle: localStorage.getItem("company_title") || "",
      companyEmail: localStorage.getItem("email") || "",
      oldPassword: "",
      newPassword: "",
      subusers: [],
      newSubuserEmail: "",
      newSubuserPassword: "",
    };
  },
  methods: {
    async updateCompanyInfo() {
      try {
        const companyId = localStorage.getItem("company_id");
        await axios.put(`http://127.0.0.1:8000/api/core/company/${companyId}/`, {
          title: this.companyTitle,
          email: this.companyEmail,
          old_password: this.oldPassword,
          new_password: this.newPassword,
        });
        alert("Информация обновлена успешно!");
      } catch (error) {
        console.error(error);
        alert("Ошибка при обновлении информации");
      }
    },
    async fetchSubusers() {
      try {
        const company_id = localStorage.getItem("company_id");
        const response = await axios.get(`http://127.0.0.1:8000/api/core/subusers/`, {
          params: { company_id: company_id }
        });
        this.subusers = response.data;
      } catch (error) {
        console.error("Ошибка при загрузке пользователей:", error);
      }
    },
    async addSubuser() {
      try {
        const companyId = localStorage.getItem("company_id");
        const now = new Date().toISOString();

        await axios.post("http://127.0.0.1:8000/api/core/subusers/", {
          email: this.newSubuserEmail,
          password: this.newSubuserPassword,
          company: companyId,
          creationdate: now,
        });

        alert("Пользователь успешно добавлен!");
        this.newSubuserEmail = "";
        this.newSubuserPassword = "";
        this.fetchSubusers();
      } catch (error) {
        console.error("Ошибка при добавлении пользователя:", error.response?.data || error);
        alert("Ошибка: " + (error.response?.data?.error || "Что-то пошло не так"));
      }
    },
    async deleteSubuser(subuserId) {
      if (!confirm("Удалить этого пользователя?")) return;

      try {
        await axios.delete("http://127.0.0.1:8000/api/core/subusers/", {
          data: { id: subuserId }
        });
        this.fetchSubusers();
      } catch (error) {
        console.error("Ошибка при удалении:", error.response?.data || error);
        alert("Не удалось удалить пользователя.");
      }
    }
  },
  created() {
    this.fetchSubusers();
  },
};
</script>

<style scoped>
.settings-page {
  max-width: 800px;
  margin: 30px auto;
  padding: 20px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
}

h1, h2, h3 {
  text-align: center;
  color: #333;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

input {
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #ccc;
}

.save-button, .add-button {
  background-color: #535af4;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.save-button:hover, .add-button:hover {
  background-color: #3b43f2;
}

.subusers-list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.subuser-item {
  background: #f7f7f8;
  padding: 10px;
  border-radius: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.delete-btn {
  background: none;
  border: none;
  color: #c00;
  font-size: 16px;
  cursor: pointer;
}
</style>
