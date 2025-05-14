<template>
  <div class="client-detail" v-if="client">
    <h1>{{ client.email }}</h1>

    <p><strong>Имя:</strong> {{ client.full_name || '-' }}</p>
    <p><strong>Телефон:</strong> {{ client.phone || '-' }}</p>
    <p><strong>Пол:</strong> {{ client.gender || '-' }}</p>
    <p><strong>Дата рождения:</strong> {{ client.birth_date || '-' }}</p>
    <p><strong>Telegram ID:</strong> {{ client.telegram_id || '-' }}</p>
    <p><strong>Дата регистрации:</strong> {{ formatDate(client.creationdate) }}</p>

    <div class="stats">
      <p><strong>Сумма:</strong> {{ client.total_amount || 0 }} ₽</p>
      <p><strong>Куплено товаров:</strong> {{ client.total_tickets || 0 }}</p>
      <p><strong>Число покупок:</strong> {{ client.purchases_count || 0 }}</p>
      <p><strong>Первая покупка:</strong> {{ formatDate(client.first_purchase) }}</p>
      <p><strong>Последняя покупка:</strong> {{ formatDate(client.last_purchase) }}</p>
    </div>

    <div class="tags">
      <h3>
        Метки:
        <button class="edit-btn" @click="editingTags = true">✏️</button>
      </h3>

      <div v-if="editingTags">
        <input v-model="tagInput" placeholder="напр. vip, рассылка, новые" />
        <div class="edit-controls">
          <button @click="saveTags">Сохранить</button>
          <button class="cancel-btn" @click="cancelEdit">Отмена</button>
        </div>
      </div>

      <div v-else class="tag-list">
        <span class="tag" v-for="tag in parseTags(client.tags)" :key="tag">{{ tag }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/axios";

export default {
  name: "ClientDetail",
  data() {
    return {
      client: null,
      editingTags: false,
      tagInput: ""
    };
  },
  created() {
    this.fetchClient();
  },
  methods: {
    async fetchClient() {
      const id = this.$route.params.id;
      const companyId = localStorage.getItem("company_id");
      try {
        const { data } = await axios.get(`/api/core/clients/${id}/`, {
          params: { company_id: companyId }
        });
        this.client = data;
        this.tagInput = data.tags || "";
      } catch (error) {
        console.error("Ошибка при загрузке клиента:", error);
      }
    },
    formatDate(iso) {
      return iso ? new Date(iso).toLocaleDateString() : "-";
    },
    parseTags(tags) {
      return (tags || "").split(",").map(tag => tag.trim()).filter(Boolean);
    },
    async saveTags() {
      try {
        await axios.patch(`/api/core/clients/${this.client.id}/`, {
          tags: this.tagInput
        });
        this.client.tags = this.tagInput;
        this.editingTags = false;
      } catch (error) {
        console.error("Ошибка при сохранении тегов:", error);
        alert("Не удалось сохранить метки.");
      }
    },
    cancelEdit() {
      this.tagInput = this.client.tags || "";
      this.editingTags = false;
    }
  }
};
</script>

<style scoped>
.client-detail {
  max-width: 700px;
  margin: 40px auto;
  background: #fff;
  padding: 25px;
  border-radius: 20px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.05);
}

.stats {
  margin-top: 20px;
}

.tags {
  margin-top: 30px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.tag {
  background-color: #ececec;
  color: #333;
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 15px;
}

.edit-btn {
  background: none;
  border: none;
  cursor: pointer;
  margin-left: 10px;
}

.edit-controls {
  margin-top: 10px;
}

.edit-controls button {
  margin-right: 10px;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
}

.edit-controls button:first-of-type {
  background: #535af4;
  color: white;
  border: none;
}

.cancel-btn {
  background: #ccc;
  border: none;
}
</style>