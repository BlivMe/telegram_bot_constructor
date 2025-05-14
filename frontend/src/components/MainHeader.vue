<template>
  <nav class="main-header">
    <div class="left-section">
      <img src="@/assets/logo.png" alt="Логотип" class="logo" />
    </div>

    <div class="center-section">
      <router-link to="/bots" class="nav-link" exact>Боты</router-link>
      <router-link to="/clients" class="nav-link">Покупатели</router-link>
      <router-link to="/settings" class="nav-link">Настройки</router-link>
    </div>

    <div class="right-section">
      <span class="company-name">{{ companyName }}</span>
      <button @click="logout" class="logout-button" title="Выйти">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
          <polyline points="16 17 21 12 16 7"></polyline>
          <line x1="21" y1="12" x2="9" y2="12"></line>
        </svg>
      </button>
    </div>
  </nav>
</template>

<script>
export default {
  name: "MainHeader",
  computed: {
    companyName() {
      return localStorage.getItem("company_title") || "Компания";
    }
  },
  methods: {
    logout() {
      localStorage.removeItem("company_id");
      localStorage.removeItem("company_title");
      localStorage.removeItem("active_bot_id");
      this.$router.push("/login");
      window.dispatchEvent(new Event("storage"));
    }
  }
};
</script>

<style scoped>
.main-header {
  background-color: #535af4;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px;
}

.left-section {
  display: flex;
  align-items: center;
}

.center-section {
  display: flex;
  gap: 30px;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-size: 16px;
}

.nav-link:hover {
  text-decoration: underline;
}

.right-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.company-name {
  font-size: 16px;
  font-weight: bold;
}

.logout-button {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.logo {
  height: 32px;
  width: 32px;
}
</style>
