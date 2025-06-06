<template>
  <div class="clients-page">
    <h1>Все покупатели</h1>

    <div class="top-controls">
      <router-link to="/clients/import">
        <button class="csv-btn">Импорт CSV</button>
      </router-link>
      <button class="view-settings-btn" @click="toggleSettings">⚙️ Настроить вид</button>
    </div>

    <table class="clients-table" v-if="clients.length">
      <thead>
        <tr>
          <th v-if="visibleColumns.email">Email</th>
          <th v-if="visibleColumns.full_name">Имя</th>
          <th v-if="visibleColumns.phone">Телефон</th>
          <th v-if="visibleColumns.gender">Пол</th>
          <th v-if="visibleColumns.birth_date">Дата рождения</th>
          <th v-if="visibleColumns.telegram_id">Telegram ID</th>
          <th v-if="visibleColumns.total_amount">Сумма</th>
          <th v-if="visibleColumns.avg_check">Средний чек</th>
          <th v-if="visibleColumns.total_tickets">Куплено товаров</th>
          <th v-if="visibleColumns.purchases_count">Число покупок</th>
          <th v-if="visibleColumns.first_purchase">Первая покупка</th>
          <th v-if="visibleColumns.last_purchase">Последняя покупка</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="client in clients"
          :key="client.id"
          @click="goToClient(client.id)"
          style="cursor: pointer"
        >
          <td v-if="visibleColumns.email">{{ client.email || "-" }}</td>
          <td v-if="visibleColumns.full_name">{{ client.full_name || "-" }}</td>
          <td v-if="visibleColumns.phone">{{ client.phone || "-" }}</td>
          <td v-if="visibleColumns.gender">{{ client.gender || "-" }}</td>
          <td v-if="visibleColumns.birth_date">{{ client.birth_date || "-" }}</td>
          <td v-if="visibleColumns.telegram_id">{{ client.telegram_id || "-" }}</td>
          <td v-if="visibleColumns.total_amount">{{ client.total_amount || 0 }}</td>
          <td v-if="visibleColumns.avg_check">{{ client.avg_check || 0 }}</td>
          <td v-if="visibleColumns.total_tickets">{{ client.total_tickets || 0 }}</td>
          <td v-if="visibleColumns.purchases_count">{{ client.purchases_count || 0 }}</td>
          <td v-if="visibleColumns.first_purchase">{{ formatDate(client.first_purchase) }}</td>
          <td v-if="visibleColumns.last_purchase">{{ formatDate(client.last_purchase) }}</td>
        </tr>
      </tbody>
    </table>

    <p v-else>Пока нет покупателей.</p>

    <div v-if="showColumnSettings" class="modal-overlay">
      <div class="modal">
        <h3>Выберите до 6 столбцов</h3>
        <div class="checkbox-group">
          <label v-for="(label, key) in columnLabels" :key="key">
            <input
              type="checkbox"
              :checked="visibleColumns[key]"
              @change="toggleColumn(key)"
            />
            {{ label }}
          </label>
        </div>
        <button @click="saveColumnSettings">Сохранить</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/axios";

export default {
  name: "ClientsPage",
  data() {
    return {
      clients: [],
      showColumnSettings: false,
      visibleColumns: {
        email: true,
        full_name: true,
        phone: true,
        gender: false,
        birth_date: false,
        telegram_id: false,
        total_amount: true,
        avg_check: false,
        total_tickets: true,
        purchases_count: true,
        first_purchase: false,
        last_purchase: false,
      },
      columnLabels: {
        email: "Email",
        full_name: "Имя",
        phone: "Телефон",
        gender: "Пол",
        birth_date: "Дата рождения",
        telegram_id: "Telegram ID",
        total_amount: "Сумма",
        avg_check: "Средний чек",
        total_tickets: "Куплено товаров",
        purchases_count: "Число покупок",
        first_purchase: "Первая покупка",
        last_purchase: "Последняя покупка",
      },
    };
  },
  created() {
    const saved = localStorage.getItem("client_column_visibility");
    if (saved) {
      this.visibleColumns = JSON.parse(saved);
    }
    this.fetchClients();
  },
  methods: {
    async fetchClients() {
      try {
        const companyId = localStorage.getItem("company_id");
        const response = await axios.get("/api/core/clients/", {
          params: { company_id: companyId },
        });
        this.clients = response.data;
      } catch (error) {
        console.error("Ошибка при загрузке клиентов:", error);
      }
    },
    toggleSettings() {
      this.showColumnSettings = !this.showColumnSettings;
    },
    countSelectedColumns() {
      return Object.values(this.visibleColumns).filter(Boolean).length;
    },
    toggleColumn(key) {
      if (this.visibleColumns[key]) {
        this.visibleColumns[key] = false;
      } else if (this.countSelectedColumns() < 6) {
        this.visibleColumns[key] = true;
      }
    },
    saveColumnSettings() {
      localStorage.setItem("client_column_visibility", JSON.stringify(this.visibleColumns));
      this.showColumnSettings = false;
    },
    formatDate(iso) {
      return iso ? new Date(iso).toLocaleDateString() : "-";
    },
    goToClient(id) {
      this.$router.push(`/clients/${id}`);
    }
  }
};
</script>

<style scoped>
.clients-page {
  max-width: 1200px;
  margin: 30px auto;
  padding: 20px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

.top-controls {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-bottom: 20px;
}

.csv-btn,
.view-settings-btn {
  background: none;
  border: 1px solid #ccc;
  padding: 10px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
}

.clients-table {
  width: 100%;
  border-collapse: collapse;
}

.clients-table th,
.clients-table td {
  border: 1px solid #eee;
  padding: 12px;
  text-align: left;
}

.clients-table th {
  background-color: #f9f9f9;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal {
  background: white;
  padding: 30px;
  border-radius: 10px;
  width: 300px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 20px 0;
}

.modal button {
  background-color: #535af4;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
}
</style>
