// Core
import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import axios from './axios';

// Components
import BotEditor from './components/BotEditor.vue';
import BotList from './components/BotList.vue';
import UserRegister from './components/UserRegister.vue';
import UserLogin from './components/UserLogin.vue';
import SettingsPage from './components/SettingsPage.vue';
import ClientsPage from './components/ClientsPage.vue';
import ClientImport from './components/ClientImport.vue';
import ClientDetail from './components/ClientDetail.vue';

// Styles
import '@vue-flow/core/dist/style.css';
import '@vue-flow/core/dist/theme-default.css';


const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: UserLogin },
  { path: '/register', component: UserRegister },

  { path: '/bots', component: BotList },
  { path: '/edit/:id', component: BotEditor },
  { path: '/settings', component: SettingsPage },

  { path: '/clients', component: ClientsPage },
  { path: '/clients/import', component: ClientImport },
  { path: '/clients/:id', component: ClientDetail },
];

// Init app
const router = createRouter({
  history: createWebHistory(),
  routes,
});

const app = createApp(App);
app.provide('$axios', axios);
app.use(router);
app.mount('#app');