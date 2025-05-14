<template>
  <div class="import-page">
    <h1>Импорт покупателей</h1>

    <div class="upload-section">
      <label>Загрузите CSV-файл:</label>
      <input type="file" accept=".csv" @change="handleFileUpload" />

      <label>
        <input type="checkbox" v-model="excludeInvalidEmails" />
        Исключить невалидные email
      </label>
    </div>

    <div class="mapping-section" v-if="csvHeaders.length">
      <h3>Настройка соответствия полей</h3>
      <div class="mapping-grid">
        <div
          v-for="field in supportedFields"
          :key="field.key"
          class="mapping-item"
        >
          <label>
            {{ field.label }}
            <span v-if="field.required" style="color: red">*</span>
          </label>
          <select v-model="fieldMapping[field.key]">
            <option disabled value="">Выбрать колонку</option>
            <option v-for="header in csvHeaders" :key="header" :value="header">
              {{ header }}
            </option>
          </select>
        </div>
      </div>

      <div class="tags">
        <label>Добавить метки (теги):</label>
        <input
          type="text"
          v-model="tags"
          placeholder="напр. новые, рассылка, Москва"
        />
      </div>

      <button @click="submitImport">Импортировать</button>
    </div>

    <div v-if="importResult">
      <p>Импортировано: {{ importResult.imported }}</p>
      <p>Пропущено: {{ importResult.skipped }}</p>
    </div>
  </div>
</template>

<script>
import axios from "@/axios";
import Papa from "papaparse";

export default {
  name: "ClientImport",
  data() {
    return {
      file: null,
      csvHeaders: [],
      fieldMapping: {},
      tags: "",
      excludeInvalidEmails: true,
      importResult: null,
      supportedFields: [
        { key: "email", label: "E-mail", required: true },
        { key: "full_name", label: "Имя" },
        { key: "phone", label: "Телефон" },
        { key: "gender", label: "Пол" },
        { key: "birth_date", label: "Дата рождения" }
      ]
    };
  },
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0];
      this.file = file;
      Papa.parse(file, {
        header: true,
        complete: (results) => {
          this.csvHeaders = Object.keys(results.data[0] || {});
        }
      });
    },
    async submitImport() {
      const companyId = localStorage.getItem("company_id");

      if (!this.fieldMapping.email) {
        alert("Не указано поле с email — импорт невозможен.");
        return;
      }

      if (!this.file) {
        alert("Файл не выбран");
        return;
      }

      console.log("Отправка данных импорта:", {
        file: this.file.name,
        fieldMapping: this.fieldMapping,
        excludeInvalidEmails: this.excludeInvalidEmails,
        tags: this.tags,
        companyId: companyId
      });

      const formData = new FormData();
      formData.append("file", this.file);
      formData.append("field_mapping", JSON.stringify(this.fieldMapping));
      formData.append("exclude_invalid_emails", this.excludeInvalidEmails);
      formData.append("tags", this.tags);

      try {
        const response = await axios.post("/api/core/clients/import/", formData, {
          params: { company_id: companyId }
        });
        this.importResult = response.data;
        console.log("Успешный импорт:", response.data);
      } catch (error) {
        console.error("Ошибка при импорте:", error);
        alert("Произошла ошибка при импорте");
      }
    }
  }
};
</script>

<style scoped>
.import-page {
  max-width: 800px;
  margin: 30px auto;
  background: #fff;
  padding: 20px;
  border-radius: 20px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.05);
}
.upload-section,
.mapping-section {
  margin-bottom: 30px;
}
.mapping-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 15px;
}
.mapping-item select {
  width: 100%;
}
.tags input {
  width: 100%;
  padding: 8px;
}
button {
  margin-top: 20px;
  padding: 10px 20px;
  background: #535af4;
  color: #fff;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}
</style>
