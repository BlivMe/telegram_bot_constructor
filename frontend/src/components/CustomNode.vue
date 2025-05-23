<template>
  <div class="custom-node">
    <!-- Вход (кроме старта) -->
    <Handle
      v-if="data.type !== 'start'"
      type="target"
      position="left"
      :style="handleStyleLeft"
    />

    <!-- Контент блока -->
    <div class="custom-node__content">
      <div class="custom-node__title">
        {{ data.label }}
      </div>

      <!-- Старт -->
      <div v-if="data.type === 'start'" class="custom-node__subtitle">
        Запуск по /start
      </div>

      <!-- Сообщение и меню и сбор -->
      <div
        v-if="['message', 'menu', 'data_capture'].includes(data.type)"
        class="custom-node__message"
      >
        {{ data.content?.trim() || 'Введите ваше сообщение' }}
      </div>

      <!-- Кнопки (меню и сбор данных) -->
      <div
        v-if="['menu', 'data_capture'].includes(data.type)"
        class="custom-node__buttons"
      >
        <div
          v-for="(btn, index) in data.buttons"
          :key="index"
          class="custom-node__button"
        >
          {{ typeof btn === 'string' ? btn : btn.text || `Кнопка ${index + 1}` }}
          <Handle
            class="button-handle"
            type="source"
            position="right"
            :style="{ top: '50%', transform: 'translateY(-50%)' }"
            :id="`btn-${index}`"
          />
        </div>
      </div>

      <!-- Поля сбора (только data_capture) -->
      <div v-if="data.type === 'data_capture'" class="custom-node__fields">
        <span class="custom-node__fields-label">
          Данные: {{ fieldsList }}
        </span>
      </div>
    </div>

    <!-- Выход вниз, кроме меню и data_capture -->
    <Handle
      v-if="!['menu', 'data_capture'].includes(data.type)"
      type="source"
      position="bottom"
      :style="handleStyleBottom"
    />
    <div
      v-if="!['menu', 'data_capture'].includes(data.type)"
      class="custom-node__bottom-text"
    >
      Следующий шаг
    </div>
  </div>
</template>

<script>
import { Handle } from '@vue-flow/core'

export default {
  name: 'CustomNode',
  props: ['data'],
  components: { Handle },
  computed: {
    handleStyleLeft() {
      return {
        top: '50%',
        transform: 'translateY(-50%)',
        left: '-4px',
        background: '#535af4',
        width: '8px',
        height: '8px',
        borderRadius: '50%'
      }
    },
    handleStyleBottom() {
      return {
        background: '#535af4',
        width: '8px',
        height: '8px',
        borderRadius: '50%'
      }
    },
    fieldsList() {
      const fields = ['Почта']
      if (this.data.collect_phone) fields.push('Телефон')
      if (this.data.collect_birth_date) fields.push('Дата рождения')
      if (this.data.collect_username) fields.push('Имя пользователя')
      if (this.data.collect_gender) fields.push('Пол')
      return fields.join(', ')
    }
  }
}
</script>

<style scoped>
.custom-node {
  width: 180px;
  min-height: 100px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #535af4;
  background-color: #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  position: relative;
  text-align: center;
}

.custom-node__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-grow: 1;
  width: 100%;
}

.custom-node__title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.custom-node__subtitle {
  font-size: 12px;
  font-weight: normal;
  color: #333;
  margin-top: 4px;
}

.custom-node__message {
  font-size: 14px;
  font-weight: normal;
  color: #333;
  margin-top: 6px;
  margin-bottom: 6px;
  max-width: 160px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.custom-node__buttons {
  margin-top: 6px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.custom-node__button {
  background: #f0f0f0;
  padding: 4px 6px;
  border-radius: 6px;
  font-size: 13px;
  position: relative;
  max-width: 160px;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  text-align: left;
}

.custom-node__fields {
  margin-top: 6px;
}

.custom-node__fields-label {
  font-size: 11px;
  color: #555;
  word-wrap: break-word;
}

.button-handle {
  position: absolute;
  right: -4px;
  background: #535af4;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.custom-node__bottom-text {
  font-size: 10px;
  color: #999;
  margin-bottom: 6px;
}
</style>

