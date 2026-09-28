<template>
  <div class="relative min-h-screen overflow-x-hidden">
    <!-- Background gradiente azul SMS -->
    <div class="fixed inset-0 overflow-hidden bg-[#f0f4f8] transition-colors duration-500">
      <div class="absolute -left-20 top-0 h-96 w-96 rounded-full bg-[#1351b4]/10 blur-3xl"></div>
      <div class="absolute right-0 top-24 h-80 w-80 rounded-full bg-[#1351b4]/08 blur-3xl"></div>
      <div class="absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-[#071d41]/08 blur-3xl"></div>
    </div>

    <div class="relative z-10 flex min-h-screen flex-col">

      <!-- Header com logo -->
      <header class="flex items-center justify-center border-b border-[#1351b4]/10 bg-white/80 px-6 py-4 backdrop-blur-sm shadow-sm">
        <img
          :src="logoSms"
          alt="Prefeitura do Rio — Secretaria Municipal de Saúde / SUS"
          class="h-10 w-auto object-contain sm:h-12"
        />
      </header>

      <!-- Conteúdo central -->
      <div class="flex flex-1 flex-col items-center justify-center px-4 py-10">
        <div class="w-full max-w-sm">

          <!-- Título do sistema -->
          <div class="mb-8 text-center">
            <div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#071d41] shadow-lg">
              <svg class="h-8 w-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 17H7A5 5 0 0 1 7 7h2"/>
                <path d="M15 7h2a5 5 0 1 1 0 10h-2"/>
                <line x1="8" y1="12" x2="16" y2="12"/>
              </svg>
            </div>
            <h1 class="text-3xl font-black uppercase tracking-wide text-[#071d41]">
              IntegraOCI
            </h1>
            <p class="mt-1 text-sm font-medium text-[#1351b4]">
              Faturamento SUS — BPA / APAC / OCI
            </p>
            <p class="mt-0.5 text-xs text-gray-400">
              Secretaria Municipal de Saúde · Rio de Janeiro
            </p>
          </div>

          <!-- Card de login -->
          <div class="rounded-2xl border border-[#1351b4]/10 bg-white px-8 py-8 shadow-xl">
            <h2 class="mb-5 text-base font-semibold text-gray-700">Acesse sua conta</h2>

            <form @submit.prevent="handleLogin" class="space-y-4">
              <div>
                <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Usuário
                </label>
                <input
                  v-model="form.username"
                  type="text"
                  autocomplete="username"
                  required
                  class="w-full rounded-lg border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-800 outline-none transition focus:border-[#1351b4] focus:bg-white focus:ring-2 focus:ring-[#1351b4]/15"
                  placeholder="seu.usuario"
                />
              </div>

              <div>
                <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Senha
                </label>
                <input
                  v-model="form.password"
                  type="password"
                  autocomplete="current-password"
                  required
                  class="w-full rounded-lg border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-800 outline-none transition focus:border-[#1351b4] focus:bg-white focus:ring-2 focus:ring-[#1351b4]/15"
                  placeholder="••••••••"
                />
              </div>

              <!-- Erro -->
              <div
                v-if="errorMsg"
                class="flex items-start gap-2 rounded-lg border border-red-100 bg-red-50 px-3.5 py-2.5 text-sm text-red-700"
              >
                <svg class="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                {{ errorMsg }}
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="mt-1 w-full rounded-lg bg-[#071d41] px-4 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-[#1351b4] active:scale-[0.98] disabled:opacity-60"
              >
                <span v-if="loading" class="flex items-center justify-center gap-2">
                  <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                    <path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="1"/>
                  </svg>
                  Entrando...
                </span>
                <span v-else>Entrar</span>
              </button>
            </form>
          </div>

          <!-- Rodapé -->
          <p class="mt-6 text-center text-xs text-gray-400">
            Sistema de uso interno · SMS-Rio
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import api from '@/services/authService';
import logoSms from '@/assets/logo_sms_rio.png';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const form = ref({ username: '', password: '' });
const loading = ref(false);
const errorMsg = ref('');

async function handleLogin() {
  errorMsg.value = '';
  loading.value = true;
  try {
    // 1. Autentica e obtém os cookies JWT
    const response = await api.post('/api/v1/auth/', form.value);
    const data = response.data;

    // 2. Login inicial no store (sem permissões ainda)
    userStore.login(data.first_name || data.username, {
      isStaff: data.is_staff,
      isSuperuser: data.is_superuser,
    });

    // 3. Busca permissões de módulo e aplica ao store
    try {
      const permResponse = await api.get('/api/v1/auth/permissions/');
      userStore.setPermissions(permResponse.data);
    } catch (_) {
      // Em caso de falha, o store já tem a lógica de fallback (acesso aberto)
    }

    const redirect = route.query.redirect || '/faturamento/bpa-apac';
    router.push(redirect);
  } catch (err) {
    const msg = err.response?.data?.error || 'Erro ao realizar login. Verifique suas credenciais.';
    errorMsg.value = msg;
  } finally {
    loading.value = false;
  }
}
</script>
