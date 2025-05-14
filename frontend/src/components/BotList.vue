<template>
  <div class="page-container">
    <div class="bot-list-wrapper">
      <div class="page-header">
        <h1>Ваши чат-боты</h1>
      </div>

      <div class="controls">
        <div class="top-controls">
          <div class="search-box">
            <span class="search-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" stroke="#aaa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </span>
            <input type="text" placeholder="Поиск чат-ботов" v-model="searchQuery" />
          </div>

          <select class="sort-select" v-model="selectedSort">
            <option value="new">Сначала новые</option>
            <option value="old">Сначала старые</option>
          </select>

          <div class="spacer"></div>
          <button class="new-bot-button" @click="createNewBot">Новый чат-бот</button>
        </div>
      </div>

      <div v-if="filteredBots.length > 0">
        <div class="bot-card" v-for="bot in filteredBots" :key="bot.id">
          <div class="bot-card-main" @click="openBot(bot.id)">
            <div class="bot-info">
              <h2>
                {{ bot.name }}
                <button class="edit-icon" @click.stop="openNameEditor(bot)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="#535af4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                    <path d="M12 20h9" />
                    <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
                  </svg>
                </button>
              </h2>

              <div v-if="bot.userlink" class="bot-link-row">
                <a :href="`https://t.me/${bot.userlink}`" target="_blank" class="bot-link-text">@{{ bot.userlink }}</a>
                <span class="copy-icon" @click.stop="copyLink(bot.userlink)" title="Скопировать ссылку">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" stroke="#535af4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <rect x="3" y="3" width="13" height="13" rx="2" ry="2"></rect>
                  </svg>
                </span>
              </div>
            </div>

            <div class="bot-meta">
              <span class="bot-status" :class="statusClass(bot.status)">
                {{ bot.status ? bot.status.charAt(0).toUpperCase() + bot.status.slice(1) : "Draft" }}
              </span>
              <small>{{ formatDate(bot.creationdate) }}</small>
            </div>
          </div>

          <div class="bot-card-actions">
            <button @click.stop="toggleDropdown(bot.id)">⋮</button>
            <div v-if="activeDropdown === bot.id" class="dropdown-menu">
              <div @click="openBot(bot.id)">Открыть</div>
              <div @click="toggleBotStatus(bot)">
                {{ bot.status === 'running' ? 'Остановить' : 'Запустить' }}
              </div>
              <div @click="duplicateBot(bot)">Дублировать</div>
              <div @click="deleteBot(bot.id)">Удалить</div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="no-bots-message">У вас пока нет чат-ботов. Создайте первый!</div>

      <!-- Modal для переименования -->
      <div v-if="editingBot" class="modal-overlay">
        <div class="modal-window">
          <h3>Редактировать имя бота</h3>
          <input v-model="editedName" placeholder="Новое имя бота" />
          <div class="modal-actions">
            <button @click="saveBotName">Сохранить</button>
            <button class="cancel-btn" @click="cancelEdit">Отмена</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "@/axios"

export default {
  data() {
    return {
      bots: [],
      searchQuery: '',
      selectedSort: 'new',
      activeDropdown: null,
      editingBot: null,
      editedName: ''
    }
  },
  computed: {
    filteredBots() {
      return this.bots
        .filter(bot => bot.name.toLowerCase().includes(this.searchQuery.toLowerCase()))
        .sort((a, b) => {
          const dateA = new Date(a.creationdate)
          const dateB = new Date(b.creationdate)
          return this.selectedSort === "new" ? dateB - dateA : dateA - dateB
        })
    }
  },
  methods: {
    async fetchBots() {
      try {
        const companyId = localStorage.getItem("company_id")
        const { data } = await axios.get("/api/core/user_bots/", {
          params: { company_id: companyId }
        })
        this.bots = data

        await Promise.all(this.bots.map(async bot => {
          if (bot.token) {
            try {
              const res = await axios.get("/api/core/get_bot_username/", {
                params: { token: bot.token }
              })
              bot.userlink = res.data.username || ''
            } catch {
              bot.userlink = ''
            }
          }
        }))
      } catch (error) {
        console.error("Ошибка при загрузке ботов:", error)
      }
    },
    async createNewBot() {
      try {
        const companyId = localStorage.getItem("company_id")
        const { data } = await axios.post("/api/bots/bots/", {
          name: "Новый бот",
          company: companyId,
          token: "placeholder-token",
          status: "draft"
        })
        this.$router.push(`/edit/${data.id}`)
      } catch (error) {
        console.error("Ошибка при создании бота:", error)
      }
    },
    openBot(id) {
      this.$router.push(`/edit/${id}`)
    },
    toggleDropdown(id) {
      this.activeDropdown = this.activeDropdown === id ? null : id
    },
    async toggleBotStatus(bot) {
      try {
        const newStatus = bot.status === 'running' ? 'stopped' : 'running'
        await axios.patch(`/api/bots/bots/${bot.id}/`, { status: newStatus })
        bot.status = newStatus
        this.activeDropdown = null
      } catch (error) {
        console.error("Ошибка при изменении статуса:", error)
      }
    },
    async duplicateBot(bot) {
      try {
        const companyId = localStorage.getItem("company_id")
        const { data } = await axios.post("/api/bots/bots/", {
          name: bot.name + " (копия)",
          company: companyId,
          token: "placeholder-token",
          status: "draft"
        })
        this.bots.push(data)
        this.activeDropdown = null
      } catch (error) {
        console.error("Ошибка при дублировании бота:", error)
      }
    },
    async deleteBot(id) {
      if (!confirm("Вы уверены, что хотите удалить этого бота?")) return
      try {
        await axios.patch(`/api/bots/bots/${id}/`, { deleted: true })
        this.bots = this.bots.filter(bot => bot.id !== id)
        this.activeDropdown = null
      } catch (error) {
        console.error("Ошибка при удалении бота:", error)
      }
    },
    copyLink(username) {
      navigator.clipboard.writeText(`https://t.me/${username}`)
    },
    formatDate(date) {
      return new Date(date).toLocaleString()
    },
    statusClass(status) {
      switch (status) {
        case "running": return "running"
        case "stopped": return "stopped"
        default: return "draft"
      }
    },
    openNameEditor(bot) {
      this.editingBot = bot
      this.editedName = bot.name
    },
    cancelEdit() {
      this.editingBot = null
      this.editedName = ''
    },
    async saveBotName() {
      if (!this.editedName.trim()) return
      try {
        await axios.patch(`/api/bots/bots/${this.editingBot.id}/`, {
          name: this.editedName
        })
        this.editingBot.name = this.editedName
      } catch (e) {
        console.error("Ошибка при сохранении имени:", e)
      }
      this.cancelEdit()
    }
  },
  created() {
    this.fetchBots()
  }
}
</script>


<style scoped>
.page-container {
  background-color: #f7f7f8;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 30px 0;
}

.bot-list-wrapper {
  background-color: #ffffff;
  width: 80%;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
}

.page-header {
  text-align: center;
  margin-bottom: 20px;
}

.controls {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.top-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.search-box {
  position: relative;
  width: 200px;
}

.search-box input {
  width: 100%;
  padding: 8px 10px 8px 35px;
  border: 1px solid #ccc;
  border-radius: 20px;
  font-size: 14px;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
}

.sort-select {
  margin-left: 20px;
  padding: 8px 15px;
  border: 1px solid #ccc;
  border-radius: 20px;
  font-size: 14px;
}

.new-bot-button {
  background-color: #535af4;
  color: #ffffff;
  border: none;
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 16px;
  cursor: pointer;
}

.bot-card {
  position: relative;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

.bot-card-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bot-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.bot-link-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 5px;
}

.bot-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  font-size: 14px;
  gap: 5px;
}

.bot-meta small {
  font-size: 14px;
  color: #888;
}

.bot-status {
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 14px;
  text-transform: capitalize;
  background: #d3d3d3;
  color: #555;
}

.bot-status.running {
  background: #d4f7dc;
  color: #28a745;
}

.bot-status.stopped {
  background: #fff3cd;
  color: #856404;
}

.no-bots-message {
  text-align: center;
  font-size: 16px;
  color: #888;
  margin-top: 30px;
}

.bot-card-actions {
  position: absolute;
  top: 15px;
  right: 15px;
}

.bot-card-actions button {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
}

.dropdown-menu {
  position: absolute;
  top: 35px;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 10;
  min-width: 140px;
}

.dropdown-menu div {
  padding: 10px;
  cursor: pointer;
}

.dropdown-menu div:hover {
  background: #f7f7f7;
}

.edit-icon {
  background: none;
  border: none;
  padding: 0;
  margin-left: 6px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-window {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  width: 300px;
}

.modal-window input {
  width: 100%;
  padding: 8px;
  font-size: 14px;
  margin-bottom: 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-actions button {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.modal-actions button:first-child {
  background-color: #535af4;
  color: white;
}

.modal-actions button:last-child {
  background-color: #ccc;
}
</style>
