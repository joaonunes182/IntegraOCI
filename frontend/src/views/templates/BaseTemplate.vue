<template>
  <div class="integra-oci-shell flex min-h-screen bg-[#eceded] dark:bg-[#1b2c40]">

    <!-- Top Navigation Bar -->
    <div
      v-if="isAuthenticated"
      class="fixed top-0 left-0 right-0 z-50 border-b border-slate-200/80 bg-white/95 shadow-sm backdrop-blur-md dark:border-white/10 dark:bg-[#071d41]/95"
    >
      <div class="flex h-[3.75rem] items-center justify-between px-3 sm:h-[4.25rem] sm:px-5 md:px-8">

        <!-- Logo + nome do sistema -->
        <div class="flex min-w-0 flex-1 items-center gap-4">
          <img
            :src="logoSms"
            alt="SMS Rio"
            class="h-8 w-auto object-contain sm:h-9"
          />
          <div class="hidden h-6 w-px bg-gray-200 dark:bg-white/20 sm:block"></div>
          <div class="hidden sm:block">
            <span class="text-sm font-black uppercase tracking-wide text-[#071d41] dark:text-white">
              IntegraOCI
            </span>
            <span class="ml-2 hidden text-xs text-gray-400 dark:text-gray-400 md:inline">
              Faturamento SUS — BPA / APAC / OCI
            </span>
          </div>
        </div>

        <!-- Usuário + logout -->
        <div class="flex items-center gap-3">
          <div class="hidden flex-col items-end sm:flex">
            <span class="text-xs font-semibold text-[#071d41] dark:text-white">
              {{ userStore.nome || 'Usuário' }}
            </span>
            <span class="text-[10px] text-gray-400">SMS-Rio</span>
          </div>
          <button
            @click="handleLogout"
            title="Sair do sistema"
            class="flex items-center gap-1.5 rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs font-semibold text-gray-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600 dark:border-white/10 dark:bg-white/10 dark:text-gray-300 dark:hover:bg-red-500/10 dark:hover:text-red-400"
          >
            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            Sair
          </button>
        </div>

      </div>
    </div>

    <!-- Main content -->
    <main
      class="flex-1"
      :class="isAuthenticated ? 'mt-[3.75rem] sm:mt-[4.25rem]' : ''"
    >
      <slot name="content" />
    </main>

  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useUserStore } from '@/stores/userStore';
import { useRouter } from 'vue-router';
import api from '@/services/authService';
import logoSms from '@/assets/logo_sms_rio.png';

defineProps({
  pageTitle: { type: String, default: '' },
  appName: { type: String, default: 'IntegraOCI' },
});

const userStore = useUserStore();
const router = useRouter();

const isAuthenticated = computed(() => userStore.autenticado);

async function handleLogout() {
  try {
    await api.post('/api/v1/auth/logout/');
  } catch (_) {
    // ignora erro de rede no logout
  }
  userStore.logout();
  router.push('/login');
}
</script>
