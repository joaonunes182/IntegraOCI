/**
 * Router do IntegraOCI standalone.
 *
 * Rotas disponíveis:
 * - /login     → LoginScreen (público)
 * - /          → BpaApacUpload (módulo principal, requer autenticação)
 */

import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/stores/userStore';

const LoginScreen = () => import('@/views/login/LoginScreen.vue');
const BpaApacUpload = () => import('@/views/faturamento/BpaApacUpload.vue');

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginScreen,
    meta: { title: 'IntegraOCI — Login', public: true },
  },
  {
    path: '/',
    redirect: '/faturamento/bpa-apac',
  },
  {
    path: '/faturamento/bpa-apac',
    name: 'BpaApacUpload',
    component: BpaApacUpload,
    meta: { title: 'IntegraOCI — Faturamento SUS', moduleKey: 'integra_oci' },
  },
  // Redireciona qualquer rota desconhecida para o módulo principal
  {
    path: '/:pathMatch(.*)*',
    redirect: '/faturamento/bpa-apac',
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// Guard global — exige autenticação para rotas não públicas
router.beforeEach((to, _from, next) => {
  document.title = to.meta?.title || 'IntegraOCI';

  const userStore = useUserStore();
  if (to.meta?.public) {
    next();
    return;
  }

  if (!userStore.autenticado) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
    return;
  }

  next();
});

export default router;
