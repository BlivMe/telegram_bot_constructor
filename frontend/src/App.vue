<template>
  <div id="app">
    <MainHeader v-if="isLoggedIn" />
    <header v-else>
      <img src="@/assets/logo.png" alt="Логотип" class="logo" />
      <h1>Конструктор чат-ботов</h1>
    </header>
    <router-view></router-view>
  </div>
</template>

<script>
import MainHeader from "@/components/MainHeader.vue";

export default {
  name: "App",
  components: {
    MainHeader,
  },
  data() {
    return {
      isLoggedIn: !!localStorage.getItem("company_id"),
    };
  },
  created() {
    window.addEventListener("storage", this.syncLoginStatus);
  },
  beforeUnmount() {
    window.removeEventListener("storage", this.syncLoginStatus);
  },
  methods: {
    syncLoginStatus() {
      this.isLoggedIn = !!localStorage.getItem("company_id");
    },
  },
};
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  width: 100%;
}

* {
  box-sizing: border-box;
}

#app {
  text-align: center;
  font-family: Roboto, sans-serif;
}

header {
  background-color: #535af4;
  color: black;
  padding: 20px 10px;
  width: 100%;
  text-align: center;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.logo {
  height: 40px;
  width: 40px;
}
</style>
