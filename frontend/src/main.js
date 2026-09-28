import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createPersistedState } from 'pinia-plugin-persistedstate';
import App from './App.vue';
import router from './router';
import './assets/tailwind.css';

const pinia = createPinia();
pinia.use(createPersistedState());

createApp(App).use(pinia).use(router).mount('#app');
