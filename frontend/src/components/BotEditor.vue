<template>
  <div class="bot-editor">
    <div class="bot-editor__top-bar">
      <div class="token-display">
        <span class="token-label">Токен:</span>
        <code>{{ token }}</code>
        <button class="token-edit-btn" @click="showTokenEditor = true">✏️</button>
      </div>
      <button class="save-structure-btn" @click="saveStructure">💾 Сохранить чат-бот</button>
    </div>

    <div v-if="showTokenEditor" class="token-modal">
      <h4>Редактировать токен</h4>
      <input v-model="editedToken" placeholder="Введите новый токен" />
      <div class="modal-actions">
        <button @click="saveToken">Сохранить</button>
        <button class="cancel-btn" @click="showTokenEditor = false">Отмена</button>
      </div>
    </div>

    <h1>Редактор бота</h1>

    <div v-if="loading" class="status">Загрузка...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <div v-else class="bot-editor__container">
      <div class="bot-editor__sidebar">
        <h3>Добавить блок</h3>
        <button @click="addBlock('start')">Старт</button>
        <button @click="addBlock('message')">Сообщение</button>
        <button @click="addBlock('menu')">Меню</button>
        <button @click="addBlock('data_capture')">Сбор данных</button>
      </div>

      <div class="bot-editor__canvas">
        <VueFlow
          v-model:nodes="nodes"
          v-model:edges="edges"
          fit-view-on-init
          class="flow-canvas"
          :node-types="nodeTypes"
          @node-click="onNodeClick"
          @connect="onConnect"
          @edge-click="onEdgeClick"
          style="width: 100%; height: 100%"
        >
          <Background variant="dots" gap="16" size="1" />
        </VueFlow>
      </div>

      <div class="bot-editor__properties" v-if="selectedNode">
        <div class="bot-editor__header">
          <h3>Свойства блока</h3>
          <div class="header-actions">
            <button class="action-btn" @click="copyNode">📄</button>
            <button class="action-btn" @click="deleteNode">🗑️</button>
            <button class="close-btn" @click="selectedNode = null">✕</button>
          </div>
        </div>

        <!-- Старт -->
        <div v-if="selectedNode.data.type === 'start'">
          <p><span class="label-muted">Запуск по</span> <code>/start</code></p>
        </div>

        <!-- Сообщение -->
        <div v-else-if="selectedNode.data.type === 'message'">
          <label for="message">Сообщение</label>
          <textarea id="message" v-model="selectedNode.data.content" :maxlength="200" placeholder="Введите сообщение..." rows="4"></textarea>
          <div class="char-count">{{ selectedNode.data.content.length }}/200</div>
        </div>

        <!-- Меню -->
        <div v-else-if="selectedNode.data.type === 'menu'">
          <label for="menu-message">Сообщение</label>
          <textarea id="menu-message" v-model="selectedNode.data.content" :maxlength="200" placeholder="Введите сообщение..." rows="4"></textarea>
          <div class="char-count">{{ selectedNode.data.content.length }}/200</div>

          <h4>Кнопки</h4>
          <div v-for="(button, index) in selectedNode.data.buttons" :key="index" class="menu-button">
            <input v-model="selectedNode.data.buttons[index].text" :maxlength="40" placeholder="Текст кнопки" />
            <button @click="removeButton(index)" class="remove-button">✕</button>
          </div>
          <button @click="addButton" :disabled="selectedNode.data.buttons.length >= 10" class="add-button">
            + Добавить кнопку
          </button>
        </div>

        <!-- Сбор данных -->
        <div v-else-if="selectedNode.data.type === 'data_capture'">
          <label for="capture-message">Сообщение</label>
          <textarea id="capture-message" v-model="selectedNode.data.message" :maxlength="200" placeholder="Введите сообщение..." rows="4"></textarea>
          <div class="char-count">{{ selectedNode.data.content.length }}/200</div>

          <h4>Кнопки</h4>
          <div v-for="(button, index) in selectedNode.data.buttons" :key="index" class="menu-button">
            <input v-model="selectedNode.data.buttons[index].text" :maxlength="40" placeholder="Текст кнопки" />
            <button @click="removeButton(index)" class="remove-button">✕</button>
          </div>
          <button @click="addButton" :disabled="selectedNode.data.buttons.length >= 10" class="add-button">
            + Добавить кнопку
          </button>

          <h4>Сбор данных</h4>
          <p>Почта (обязательно)</p>
          <label><input type="checkbox" v-model="selectedNode.data.collect_birth_date" /> Дата рождения</label><br />
          <label><input type="checkbox" v-model="selectedNode.data.collect_username" /> Имя пользователя</label><br />
          <label><input type="checkbox" v-model="selectedNode.data.collect_gender" /> Пол</label><br />
          <label><input type="checkbox" v-model="selectedNode.data.collect_phone" /> Телефон</label>
        </div>
      </div>

      <div class="toast" v-if="toastMessage">{{ toastMessage }}</div>
    </div>
  </div>
</template>

<script>
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { markRaw } from 'vue'
import CustomNode from '@/components/CustomNode.vue'
import axios from '@/axios'

export default {
  name: 'BotEditor',
  components: { VueFlow, Background },
  data() {
    return {
      loading: true,
      error: null,
      blocks: [],
      connections: [],
      token: '',
      editedToken: '',
      showTokenEditor: false,
      nodes: [],
      edges: [],
      selectedNode: null,
      toastMessage: '',
      nodeTypes: {
        custom: markRaw(CustomNode)
      }
    }
  },
  methods: {
    async fetchStructure(botId) {
      try {
        const response = await axios.get(`/api/bots/${botId}/structure/`)
        this.blocks = response.data.blocks
        this.connections = response.data.connections

        this.nodes = this.blocks.map(this.formatNode)
        this.edges = this.connections.map(conn => {
          const sourceHandle = conn.button_index != null ? `btn-${conn.button_index}` : null
          return {
            id: `e${conn.source}-${conn.target}`,
            source: String(conn.source),
            target: String(conn.target),
            sourceHandle
          }
        })
      } catch (error) {
        this.error = 'Не удалось загрузить структуру бота.'
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    async fetchToken(botId) {
      try {
        const response = await axios.get(`/api/bots/${botId}/token/`)
        this.token = response.data.token
        this.editedToken = response.data.token
      } catch {
        this.token = ''
        this.editedToken = ''
      }
    },

    async saveToken() {
      const botId = parseInt(this.$route.params.id)
      try {
        await axios.post(`/api/bots/${botId}/token/`, { token: this.editedToken })
        this.token = this.editedToken
        this.showTokenEditor = false
        this.showToast('Токен обновлён')
      } catch {
        this.showToast('Ошибка при обновлении токена')
      }
    },

    async saveStructure() {
      const botId = parseInt(this.$route.params.id)
      try {
        const payload = {
          blocks: this.nodes.map(n => ({
            id: n.id,
            type: n.data.type,
            title: n.data.label,
            content: n.data.content ?? n.data.message ?? '',
            buttons: (n.data.buttons || []).map(b => ({
              text: typeof b === 'string' ? b : b.text,
              target_block: b.target_block ?? null
            })),
            collect_birth_date: n.data.collect_birth_date,
            collect_username: n.data.collect_username,
            collect_gender: n.data.collect_gender,
            collect_phone: n.data.collect_phone,
            x: n.position.x,
            y: n.position.y
          })),
          connections: this.edges.map(e => ({
            source: e.source,
            target: e.target,
            button_index: e.sourceHandle?.startsWith('btn-')
              ? parseInt(e.sourceHandle.replace('btn-', ''))
              : null
          }))
        }
        await axios.post(`/api/bots/${botId}/save_structure/`, payload)
        this.showToast('Структура сохранена')
      } catch (error) {
        this.showToast('Ошибка при сохранении')
        console.error(error)
      }
    },

    addBlock(type) {
      const id = (Date.now() + Math.random()).toString()
      const block = {
        id,
        type,
        title: this.translateType(type),
        content: '',
        message: '',
        buttons: (type === 'menu' || type === 'data_capture')
          ? [{ text: 'Кнопка 1', target_block: null }]
          : [],
        collect_birth_date: false,
        collect_username: false,
        collect_gender: false,
        collect_phone: false
      }
      this.nodes.push(this.formatNode(block))
    },

    formatNode(block) {
      return {
        id: String(block.id),
        position: {
          x: block.x ?? Math.random() * 600,
          y: block.y ?? Math.random() * 400
        },
        type: 'custom',
        data: {
          label: block.title,
          type: block.type,
          content: block.content ?? block.message ?? '',
          buttons: block.buttons ?? [],
          collect_birth_date: block.collect_birth_date,
          collect_username: block.collect_username,
          collect_gender: block.collect_gender,
          collect_phone: block.collect_phone
        }
      }
    },

    onNodeClick({ node }) {
      this.selectedNode = node
    },

    onConnect({ source, target, sourceHandle }) {
      const edgeId = `e${source}-${target}`
      if (!this.edges.some(e => e.id === edgeId)) {
        this.edges.push({ id: edgeId, source, target, sourceHandle })
        this.showToast('Связь добавлена')
      }
    },

    onEdgeClick({ edge }) {
      if (confirm('Удалить эту связь?')) {
        this.edges = this.edges.filter(e => e.id !== edge.id)
        this.showToast('Связь удалена')
      }
    },

    copyNode() {
      if (!this.selectedNode) return
      const newId = (Date.now() + Math.random()).toString()
      const copy = {
        id: newId,
        position: {
          x: this.selectedNode.position.x + 60,
          y: this.selectedNode.position.y + 60
        },
        type: 'custom',
        data: JSON.parse(JSON.stringify(this.selectedNode.data))
      }
      this.nodes.push(copy)
      this.showToast('Блок скопирован')
    },

    deleteNode() {
      if (!this.selectedNode) return
      this.nodes = this.nodes.filter(n => n.id !== this.selectedNode.id)
      this.edges = this.edges.filter(e => e.source !== this.selectedNode.id && e.target !== this.selectedNode.id)
      this.selectedNode = null
      this.showToast('Блок удалён')
    },

    addButton() {
      if (this.selectedNode && this.selectedNode.data.buttons.length < 10) {
        const last = this.selectedNode.data.buttons.at(-1)
        if (!last || (typeof last === 'string' ? last.trim() !== '' : last.text?.trim() !== '')) {
          this.selectedNode.data.buttons.push({
            text: `Кнопка ${this.selectedNode.data.buttons.length + 1}`,
            target_block: null
          })
        } else {
          this.showToast('Сначала заполните предыдущую кнопку!')
        }
      }
    },

    removeButton(index) {
      if (this.selectedNode) {
        this.selectedNode.data.buttons.splice(index, 1)
      }
    },

    translateType(type) {
      switch (type) {
        case 'start': return 'Старт'
        case 'message': return 'Сообщение'
        case 'menu': return 'Меню'
        case 'data_capture': return 'Сбор данных'
        default: return 'Блок'
      }
    },

    showToast(message) {
      this.toastMessage = message
      setTimeout(() => (this.toastMessage = ''), 2500)
    }
  },

  created() {
    const companyId = localStorage.getItem("company_id")
    const userType = localStorage.getItem("user_type")

    if (!companyId || !userType) {
      alert("Доступ запрещён. Пожалуйста, авторизуйтесь.")
      this.$router.push("/login")
      return
    }

    const botId = parseInt(this.$route.params.id)
    this.fetchStructure(botId)
    this.fetchToken(botId)
  }
}
</script>


<style scoped>
.bot-editor {
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  font-size: 24px;
  margin-bottom: 20px;
}

.bot-editor__top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 20px;
}

.token-display {
  display: flex;
  align-items: center;
  background: #f3f3ff;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  border: 1px solid #ccc;
}

.token-display .token-label {
  margin-right: 6px;
  font-weight: 500;
}

.token-display code {
  font-family: monospace;
  background: #e0e0ff;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 8px;
}

.token-edit-btn {
  background: none;
  border: none;
  font-size: 16px;
  margin-left: 4px;
  cursor: pointer;
  color: #535af4;
}

.save-structure-btn {
  background-color: #535af4;
  color: white;
  padding: 10px 14px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: background 0.2s ease;
}

.save-structure-btn:hover {
  background-color: #4348e0;
}

.token-modal {
  position: fixed;
  top: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 20px 24px;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
  z-index: 9999;
  min-width: 320px;
  border: 1px solid #ccc;
}

.token-modal h4 {
  margin-bottom: 12px;
  font-size: 16px;
}

.token-modal input {
  width: 100%;
  padding: 8px;
  font-size: 14px;
  border-radius: 6px;
  border: 1px solid #aaa;
  margin-bottom: 12px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.token-modal button {
  padding: 8px 14px;
  font-size: 14px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.token-modal .cancel-btn {
  background-color: #ccc;
  color: black;
}

.token-modal button:not(.cancel-btn) {
  background-color: #535af4;
  color: white;
}

.status {
  font-size: 16px;
  color: #777;
}

.status.error {
  color: red;
}

.bot-editor__container {
  display: flex;
  height: calc(100vh - 160px);
  overflow: hidden;
}

.bot-editor__sidebar {
  width: 220px;
  margin-right: 20px;
  padding: 15px;
  background-color: #f1f1f1;
  border-radius: 12px;
  height: 600px;
  box-sizing: border-box;
}

.bot-editor__sidebar h3 {
  margin-bottom: 15px;
  font-size: 18px;
}

.bot-editor__sidebar button {
  width: 100%;
  margin-bottom: 12px;
  padding: 12px;
  font-size: 14px;
  background-color: #ffffff;
  border: 1px solid #ccc;
  border-radius: 10px;
  cursor: pointer;
}

.bot-editor__canvas {
  flex-grow: 1;
  position: relative;
  width: 100%;
  height: 600px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  border-radius: 10px;
  overflow: hidden;
}

.bot-editor__canvas .flow-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.bot-editor__properties {
  width: 320px;
  height: 600px;
  margin-left: 20px;
  padding: 15px;
  background-color: #fdfdfd;
  border-left: 1px solid #ccc;
  border-radius: 10px;
  font-size: 14px;
}

.bot-editor__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 6px;
}

.action-btn,
.close-btn {
  border: none;
  background: none;
  font-size: 18px;
  cursor: pointer;
}

textarea {
  width: 100%;
  border-radius: 6px;
  border: 1px solid #ccc;
  padding: 8px;
  font-size: 14px;
}

.char-count {
  font-size: 12px;
  color: #666;
  text-align: right;
  margin-top: 4px;
}

.menu-button {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.menu-button input {
  flex: 1;
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 6px;
  margin-right: 8px;
  font-size: 14px;
}

.remove-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #c00;
}

.add-button {
  margin-top: 10px;
  width: 100%;
  padding: 10px;
  font-size: 14px;
  background-color: #eee;
  border: 1px dashed #aaa;
  border-radius: 6px;
  cursor: pointer;
}

.toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: #535af4;
  color: #fff;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 9999;
}
</style>
