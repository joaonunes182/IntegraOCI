<template>
  <BaseTemplate :page-title="''" :app-name="'CCDTI'">
    <template #content>
      <div class="integra-oci-shell bg-[#eceded] px-2 pb-4 pt-0 dark:bg-gray-900 md:px-4 md:pb-6 lg:flex lg:h-[calc(100dvh-4rem)] lg:max-h-[calc(100dvh-4rem)] lg:min-h-0 lg:flex-col lg:overflow-hidden lg:px-6 lg:pl-0 lg:pr-8 lg:pb-0">
        <div
          class="grid min-h-0 flex-1 grid-cols-1 items-stretch gap-4 lg:gap-5"
          :class="isModuleMenuCollapsed ? 'lg:grid-cols-[4rem_minmax(0,1fr)]' : 'lg:grid-cols-[18rem_minmax(0,1fr)]'"
        >
          <aside class="min-h-0 shrink-0 lg:flex lg:h-full lg:max-h-full lg:flex-col">
            <section
              class="relative flex h-full min-h-0 flex-col bg-[#eceded] shadow-[2px_0_12px_0_rgba(0,0,0,0.10)] transition-all duration-300 ease-in-out dark:bg-gray-900 dark:shadow-[2px_0_16px_0_rgba(0,0,0,0.35)]"
            >
              <div class="border-b border-gray-200 px-3 py-3 dark:border-gray-700">
                <div class="flex items-center" :class="isModuleMenuCollapsed ? 'justify-center' : 'justify-between'">
                  <div v-if="!isModuleMenuCollapsed" class="min-w-0">
                    <p class="text-sm font-semibold text-gray-700 dark:text-gray-200">Central do módulo</p>
                    <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      Selecione um módulo para acompanhar importações, tratamento e histórico.
                    </p>
                  </div>
                  <button
                    type="button"
                    @click="isModuleMenuCollapsed = !isModuleMenuCollapsed"
                    class="rounded-md p-2 text-gray-500 transition-colors hover:bg-white/70 hover:text-[#13335a] dark:hover:bg-gray-800 dark:hover:text-[#42b9eb]"
                    :aria-label="isModuleMenuCollapsed ? 'Expandir menu lateral' : 'Recolher menu lateral'"
                  >
                    <ChevronLeft v-if="!isModuleMenuCollapsed" class="h-4 w-4" />
                    <ChevronRight v-else class="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div class="min-h-0 flex-1 overflow-y-auto p-2">

                <!-- Apresentação / Visão Geral -->
                <div>
                  <div class="flex items-center gap-2">
                    <button
                      type="button"
                      @click="selectModule('apresentacao')"
                      class="mb-2 w-full rounded-lg border px-3 py-2.5 text-left text-sm transition-all duration-300"
                      :class="[
                        isModuleMenuCollapsed ? 'flex items-center justify-center' : 'block',
                        activeTab === 'apresentacao'
                          ? 'border-[#13335a]/20 bg-[#13335a]/[0.06] text-[#13335a] shadow-sm dark:border-[#42b9eb]/30 dark:bg-[#42b9eb]/10 dark:text-[#42b9eb]'
                          : 'border-transparent text-gray-700 hover:border-gray-200 hover:bg-gray-50 dark:text-gray-300 dark:hover:border-gray-600 dark:hover:bg-gray-700'
                      ]"
                    >
                      <div class="w-full" :class="isModuleMenuCollapsed ? 'flex items-center justify-center' : 'grid grid-cols-[auto,1fr,auto] items-start gap-2'">
                        <div
                          v-if="!isModuleMenuCollapsed"
                          class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-gray-300/50 bg-white/80 dark:border-gray-600 dark:bg-gray-800"
                        >
                          <LayoutDashboard class="h-4 w-4" :class="activeTab === 'apresentacao' ? 'text-[#13335a] dark:text-[#42b9eb]' : 'text-gray-500 dark:text-gray-300'" />
                        </div>
                        <LayoutDashboard
                          v-else
                          class="h-4 w-4 shrink-0"
                          :class="activeTab === 'apresentacao' ? 'text-[#13335a] dark:text-[#42b9eb]' : 'text-gray-500 dark:text-gray-300'"
                        />
                        <div v-if="!isModuleMenuCollapsed" class="min-w-0">
                          <span class="block truncate text-sm font-medium">Visão Geral</span>
                        </div>
                      </div>
                    </button>
                  </div>
                </div>

                <div v-if="userStore.hasModuleItemAccess('integra_oci', 'bpa_limpo')">
                  <div class="flex items-center gap-2">
                    <button
                      type="button"
                      @click="selectModule('tratamento')"
                      class="mb-2 w-full rounded-lg border px-3 py-2.5 text-left text-sm transition-all duration-300"
                      :class="[
                        isModuleMenuCollapsed ? 'flex items-center justify-center' : 'block',
                        activeTab === 'tratamento'
                          ? 'border-[#13335a]/20 bg-[#13335a]/[0.06] text-[#13335a] shadow-sm dark:border-[#42b9eb]/30 dark:bg-[#42b9eb]/10 dark:text-[#42b9eb]'
                          : 'border-transparent text-gray-700 hover:border-gray-200 hover:bg-gray-50 dark:text-gray-300 dark:hover:border-gray-600 dark:hover:bg-gray-700'
                      ]"
                    >
                      <div class="w-full" :class="isModuleMenuCollapsed ? 'flex items-center justify-center' : 'grid grid-cols-[auto,1fr,auto] items-start gap-2'">
                        <div
                          v-if="!isModuleMenuCollapsed"
                          class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-gray-300/50 bg-white/80 dark:border-gray-600 dark:bg-gray-800"
                        >
                          <FileSearch class="h-4 w-4" :class="activeTab === 'tratamento' ? 'text-[#13335a] dark:text-[#42b9eb]' : 'text-gray-500 dark:text-gray-300'" />
                        </div>
                        <FileSearch
                          v-else
                          class="h-4 w-4 shrink-0"
                          :class="activeTab === 'tratamento' ? 'text-[#13335a] dark:text-[#42b9eb]' : 'text-gray-500 dark:text-gray-300'"
                        />
                        <div v-if="!isModuleMenuCollapsed" class="min-w-0">
                          <span class="block truncate text-sm font-medium">BPA Inteligente</span>
                        </div>
                    
                      </div>
                    </button>
                    <button
                      v-if="!isModuleMenuCollapsed"
                      type="button"
                      @click="toggleModuleSubmenu('tratamento')"
                      class="inline-flex h-9 w-9 items-center justify-center rounded-md text-gray-500 transition-colors hover:bg-gray-100 hover:text-[#13335a] dark:hover:bg-gray-700 dark:hover:text-[#42b9eb]"
                      aria-label="Mostrar ou esconder histórico de tratamento"
                    >
                      <ChevronDown v-if="isTratamentoMenuOpen" class="h-4.5 w-4.5" />
                      <ChevronRight v-else class="h-4.5 w-4.5" />
                    </button>
                  </div>
                  <div v-if="!isModuleMenuCollapsed && isTratamentoMenuOpen && userStore.hasModuleItemAccess('integra_oci', 'historico')" class="ml-4 mt-1 border-l border-gray-200 pl-3 dark:border-gray-600">
                    <button
                      type="button"
                      @click="selectModule('tratamento', 'history')"
                      class="flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-left text-xs font-medium transition-all duration-300"
                      :class="activeTab === 'tratamento' && activeSubtab === 'history'
                        ? 'bg-gray-50 text-[#13335a] shadow-sm dark:bg-gray-700/50 dark:text-[#42b9eb]'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-[#13335a] dark:text-gray-300 dark:hover:bg-gray-700/60 dark:hover:text-[#42b9eb]'"
                    >
                      <History class="h-4 w-4 shrink-0" />
                      <span class="flex-1">Histórico</span>
                 
                    </button>
                  </div>
                </div>

                <div v-if="userStore.hasModuleItemAccess('integra_oci', 'formar_combos')" class="mt-2">
                  <div class="flex items-center gap-2">
                    <button
                      type="button"
                      @click="selectModule('combos')"
                      class="mb-2 w-full rounded-lg border px-3 py-2.5 text-left text-sm transition-all duration-300"
                      :class="[
                        isModuleMenuCollapsed ? 'flex items-center justify-center' : 'block',
                        activeTab === 'combos'
                          ? 'border-[#13335a]/20 bg-[#13335a]/[0.06] text-[#13335a] shadow-sm dark:border-[#42b9eb]/30 dark:bg-[#42b9eb]/10 dark:text-[#42b9eb]'
                          : 'border-transparent text-gray-700 hover:border-gray-200 hover:bg-gray-50 dark:text-gray-300 dark:hover:border-gray-600 dark:hover:bg-gray-700'
                      ]"
                    >
                      <div class="w-full" :class="isModuleMenuCollapsed ? 'flex items-center justify-center' : 'grid grid-cols-[auto,1fr,auto] items-start gap-2'">
                        <div
                          v-if="!isModuleMenuCollapsed"
                          class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-gray-300/50 bg-white/80 dark:border-gray-600 dark:bg-gray-800"
                        >
                          <Files class="h-4 w-4" :class="activeTab === 'combos' ? 'text-[#13335a] dark:text-[#42b9eb]' : 'text-gray-500 dark:text-gray-300'" />
                        </div>
                        <Files
                          v-else
                          class="h-4 w-4 shrink-0"
                          :class="activeTab === 'combos' ? 'text-[#13335a] dark:text-[#42b9eb]' : 'text-gray-500 dark:text-gray-300'"
                        />
                        <div v-if="!isModuleMenuCollapsed" class="min-w-0">
                          <span class="block truncate text-sm font-medium">Validação de Combos</span>
                        </div>
                       
                      </div>
                    </button>
                    <button
                      v-if="!isModuleMenuCollapsed"
                      type="button"
                      @click="toggleModuleSubmenu('combos')"
                      class="inline-flex h-9 w-9 items-center justify-center rounded-md text-gray-500 transition-colors hover:bg-gray-100 hover:text-[#13335a] dark:hover:bg-gray-700 dark:hover:text-[#42b9eb]"
                      aria-label="Mostrar ou esconder histórico de combos"
                    >
                      <ChevronDown v-if="isCombosMenuOpen" class="h-4.5 w-4.5" />
                      <ChevronRight v-else class="h-4.5 w-4.5" />
                    </button>
                  </div>
                  <div v-if="!isModuleMenuCollapsed && isCombosMenuOpen && userStore.hasModuleItemAccess('integra_oci', 'historico')" class="ml-4 mt-1 border-l border-gray-200 pl-3 dark:border-gray-600">
                    <button
                      type="button"
                      @click="selectModule('combos', 'history')"
                      class="flex w-full items-center gap-2 rounded-lg px-2.5 py-1.5 text-left text-xs font-medium transition-all duration-300"
                      :class="activeTab === 'combos' && activeSubtab === 'history'
                        ? 'bg-gray-50 text-[#13335a] shadow-sm dark:bg-gray-700/50 dark:text-[#42b9eb]'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-[#13335a] dark:text-gray-300 dark:hover:bg-gray-700/60 dark:hover:text-[#42b9eb]'"
                    >
                      <History class="h-4 w-4 shrink-0" />
                      <span class="flex-1">Histórico</span>
                
                    </button>
                  </div>
                </div>
                <div v-if="userStore.hasModuleItemAccess('integra_oci', 'dashboard')" class="mt-2">
                  <div class="flex items-center gap-2">
                    <button
                      type="button"
                      @click="selectModule('dashboard')"
                      class="mb-2 w-full rounded-lg border px-3 py-2.5 text-left text-sm transition-all duration-300"
                      :class="[
                        isModuleMenuCollapsed ? 'flex items-center justify-center' : 'block',
                        activeTab === 'dashboard'
                          ? 'border-[#13335a]/20 bg-[#13335a]/[0.06] text-[#13335a] shadow-sm dark:border-[#42b9eb]/30 dark:bg-[#42b9eb]/10 dark:text-[#42b9eb]'
                          : 'border-transparent text-gray-700 hover:border-gray-200 hover:bg-gray-50 dark:text-gray-300 dark:hover:border-gray-600 dark:hover:bg-gray-700'
                      ]"
                    >
                      <div class="w-full" :class="isModuleMenuCollapsed ? 'flex items-center justify-center' : 'grid grid-cols-[auto,1fr,auto] items-start gap-2'">
                        <div
                          v-if="!isModuleMenuCollapsed"
                          class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-gray-300/50 bg-white/80 dark:border-gray-600 dark:bg-gray-800"
                        >
                          <BarChart3 class="h-4 w-4" :class="activeTab === 'dashboard' ? 'text-[#13335a] dark:text-[#42b9eb]' : 'text-gray-500 dark:text-gray-300'" />
                        </div>
                        <BarChart3
                          v-else
                          class="h-4 w-4 shrink-0"
                          :class="activeTab === 'dashboard' ? 'text-[#13335a] dark:text-[#42b9eb]' : 'text-gray-500 dark:text-gray-300'"
                        />
                        <div v-if="!isModuleMenuCollapsed" class="min-w-0">
                          <span class="block truncate text-sm font-medium">Dashboard Analítico</span>
                        </div>
                      </div>
                    </button>
                  </div>
                </div>
                <div v-if="userStore.hasModuleItemAccess('integra_oci', 'auditoria')" class="mt-2">
                  <button
                    type="button"
                    @click="selectModule('auditoria')"
                    class="mb-2 w-full rounded-lg border px-3 py-2.5 text-left text-sm transition-all duration-300"
                    :class="[
                      isModuleMenuCollapsed ? 'flex items-center justify-center' : 'block',
                      activeTab === 'auditoria'
                        ? 'border-[#13335a]/20 bg-[#13335a]/[0.06] text-[#13335a] shadow-sm dark:border-[#42b9eb]/30 dark:bg-[#42b9eb]/10 dark:text-[#42b9eb]'
                        : 'border-transparent text-gray-700 hover:border-gray-200 hover:bg-gray-50 dark:text-gray-300 dark:hover:border-gray-600 dark:hover:bg-gray-700'
                    ]"
                  >
                    <div class="w-full" :class="isModuleMenuCollapsed ? 'flex items-center justify-center' : 'grid grid-cols-[auto,1fr] items-start gap-2'">
                      <div
                        v-if="!isModuleMenuCollapsed"
                        class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-gray-300/50 bg-white/80 dark:border-gray-600 dark:bg-gray-800"
                      >
                        <ShieldCheck class="h-4 w-4" :class="activeTab === 'auditoria' ? 'text-[#13335a] dark:text-[#42b9eb]' : 'text-gray-500 dark:text-gray-300'" />
                      </div>
                      <ShieldCheck
                        v-else
                        class="h-4 w-4 shrink-0"
                        :class="activeTab === 'auditoria' ? 'text-[#13335a] dark:text-[#42b9eb]' : 'text-gray-500 dark:text-gray-300'"
                      />
                      <div v-if="!isModuleMenuCollapsed" class="min-w-0">
                        <span class="block truncate text-sm font-medium">Auditoria</span>
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              <div class="relative shrink-0 border-t border-gray-200 p-3 dark:border-gray-700">
                <button
                  type="button"
                  @click="showModuleInfo = !showModuleInfo"
                  class="inline-flex h-9 w-9 items-center justify-center rounded-full border border-gray-300/60 bg-white text-gray-600 shadow-sm transition-colors hover:text-[#13335a] dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:text-[#42b9eb]"
                  :class="isModuleMenuCollapsed ? 'mx-auto flex' : ''"
                  aria-label="Ver detalhes sobre o objetivo do módulo"
                >
                  <Info class="h-4 w-4" />
                </button>
                <div
                  v-if="showModuleInfo"
                  class="absolute z-50 rounded-lg border border-slate-200 bg-white p-3 text-xs leading-5 text-gray-700 shadow-xl dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                  :class="isModuleMenuCollapsed
                    ? 'left-full top-1/2 ml-2 w-[280px] -translate-y-1/2'
                    : 'bottom-full left-0 mb-2 w-[min(280px,calc(100vw-6rem))]'"
                >
                  O Integra OCI existe para validar combinações assistenciais OCI e depurar o BPA com base nos registros já autorizados em APAC, evitando duplicidade de produção, reduzindo inconsistências de conferência e apoiando o faturamento com mais segurança operacional.
                </div>
              </div>
            </section>
          </aside>

          <div class="min-h-0 min-w-0 lg:h-full lg:max-h-full lg:overflow-y-auto lg:overscroll-y-contain lg:pr-1">
            <Transition name="module-tab" mode="out-in">
              <!-- Tela de Apresentação / Visão Geral -->
              <div v-if="activeTab === 'apresentacao'" key="apresentacao" class="min-w-0 py-2 space-y-6">
                <!-- Hero Banner -->
                <div class="relative overflow-hidden rounded-2xl border border-[#13335a]/10 bg-gradient-to-br from-[#13335a] via-[#2a688f] to-[#42b9eb] p-6 text-white shadow-xl md:p-8">
                  <div class="absolute -right-12 -top-12 h-56 w-56 rounded-full bg-white/10 blur-3xl"></div>
                  <div class="absolute bottom-0 left-1/3 h-48 w-48 rounded-full bg-[#13335a]/30 blur-2xl"></div>
                  
                  <div class="relative z-10 max-w-3xl">
                    <div class="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3.5 py-1 text-xs font-semibold uppercase tracking-widest text-white/90 backdrop-blur-md">
                      <Sparkles class="h-3.5 w-3.5 text-[#42b9eb]" />
                      Módulo Especializado de Faturamento SUS
                    </div>
                    <h1 class="mt-4 text-2xl font-black uppercase tracking-tight sm:text-3xl md:text-4xl">
                      IntegraOCI — Apoio ao Faturamento SUS
                    </h1>
                    <p class="mt-3 text-sm leading-relaxed text-white/90 md:text-base">
                      Plataforma institucional desenvolvida para automatizar, validar e otimizar o tratamento de remessas ambulatoriais <strong>BPA</strong> e a formação de <strong>Combos OCI</strong> para o Super Centro Carioca de Saúde.
                    </p>
                  </div>
                </div>

                <!-- Cards de Funcionalidades Principais -->
                <div class="grid gap-5 md:grid-cols-2">
                  <!-- Card 1: BPA Inteligente -->
                  <div class="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
                    <div>
                      <div class="flex items-center justify-between">
                        <div class="flex h-12 w-12 items-center justify-center rounded-xl border border-[#13335a]/15 bg-[#13335a]/10 text-[#13335a] dark:border-[#42b9eb]/30 dark:bg-[#42b9eb]/10 dark:text-[#42b9eb]">
                          <FileSearch class="h-6 w-6" />
                        </div>
                        <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">Tratamento BPA</span>
                      </div>
                      
                      <h2 class="mt-4 text-lg font-bold text-gray-900 dark:text-white">
                        BPA Inteligente (BPA Limpo)
                      </h2>

                      <div class="mt-3 space-y-2.5 text-xs leading-relaxed text-gray-600 dark:text-gray-300">
                        <p>
                          <strong class="text-gray-900 dark:text-white">O que é:</strong> Módulo de higienização e validação automatizada dos arquivos do Boletim de Produção Ambulatorial (BPA).
                        </p>
                        <p>
                          <strong class="text-gray-900 dark:text-white">Para que serve:</strong> Cruza a produção com autorizações APAC e cadastros de CNES e CBO. Filtra registros duplicados, corrige inconsistências de preenchimento e gera o arquivo texto final auditado e pronto para o envio oficial ao DATASUS/SMS, eliminando glosas de faturamento.
                        </p>
                      </div>
                    </div>

                    <div class="mt-6 pt-4 border-t border-gray-100 dark:border-gray-700">
                      <button
                        type="button"
                        @click="selectModule('tratamento')"
                        class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#13335a] px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition hover:bg-[#2a688f] dark:bg-[#42b9eb] dark:text-[#13335a] dark:hover:bg-white"
                      >
                        Acessar BPA Inteligente
                        <ArrowRight class="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  <!-- Card 2: Formar Combos OCI -->
                  <div class="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
                    <div>
                      <div class="flex items-center justify-between">
                        <div class="flex h-12 w-12 items-center justify-center rounded-xl border border-[#2a688f]/15 bg-[#2a688f]/10 text-[#2a688f] dark:border-[#42b9eb]/30 dark:bg-[#42b9eb]/10 dark:text-[#42b9eb]">
                          <Files class="h-6 w-6" />
                        </div>
                        <span class="rounded-full bg-sky-50 px-3 py-1 text-xs font-bold text-[#2a688f] dark:bg-gray-700 dark:text-[#42b9eb]">Combos OCI</span>
                      </div>
                      
                      <h2 class="mt-4 text-lg font-bold text-gray-900 dark:text-white">
                        Formar Combos OCI
                      </h2>

                      <div class="mt-3 space-y-2.5 text-xs leading-relaxed text-gray-600 dark:text-gray-300">
                        <p>
                          <strong class="text-gray-900 dark:text-white">O que é:</strong> Módulo de agrupamento assistencial em Ofertas de Cuidados Integrados (OCI).
                        </p>
                        <p>
                          <strong class="text-gray-900 dark:text-white">Para que serve:</strong> Agrupa múltiplos procedimentos ambulatoriais correlatos (ex: consulta + exames pré-operatórios + cirurgia) sob um único regramento OCI. Evita fragmentação, garante o faturamento de linhas de cuidado completas e simplifica a auditoria.
                        </p>
                      </div>
                    </div>

                    <div class="mt-6 pt-4 border-t border-gray-100 dark:border-gray-700">
                      <button
                        type="button"
                        @click="selectModule('combos')"
                        class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#2a688f] px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition hover:bg-[#13335a] dark:bg-[#42b9eb] dark:text-[#13335a] dark:hover:bg-white"
                      >
                        Acessar Validação de Combos
                        <ArrowRight class="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Destaques de Benefícios -->
                <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                  <h3 class="text-xs font-bold uppercase tracking-wider text-[#13335a] dark:text-[#42b9eb]">
                    Principais Recursos e Benefícios
                  </h3>
                  <div class="mt-4 grid gap-4 sm:grid-cols-3">
                    <div class="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/50">
                      <div class="flex items-center gap-2 text-xs font-semibold text-gray-900 dark:text-white">
                        <CheckCircle2 class="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                        Redução de Glosas
                      </div>
                      <p class="mt-1.5 text-xs leading-relaxed text-gray-500 dark:text-gray-400">
                        Filtra erros antes da submissão à SMS, eliminando rejeições de faturamento por inconsistências.
                      </p>
                    </div>

                    <div class="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/50">
                      <div class="flex items-center gap-2 text-xs font-semibold text-gray-900 dark:text-white">
                        <Layers class="h-4 w-4 text-[#2a688f] dark:text-[#42b9eb]" />
                        Rastreabilidade Completa
                      </div>
                      <p class="mt-1.5 text-xs leading-relaxed text-gray-500 dark:text-gray-400">
                        Histórico auditável de envios com relatórios gerenciais e conferência detalhada em PDF.
                      </p>
                    </div>

                    <div class="rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/50">
                      <div class="flex items-center gap-2 text-xs font-semibold text-gray-900 dark:text-white">
                        <ShieldCheck class="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                        Padrão DATASUS
                      </div>
                      <p class="mt-1.5 text-xs leading-relaxed text-gray-500 dark:text-gray-400">
                        Totalmente alinhado aos padrões da Secretaria Municipal de Saúde e do Ministério da Saúde.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else-if="activeTab === 'tratamento' && userStore.hasModuleItemAccess('integra_oci', 'bpa_limpo')" key="tratamento" class="min-w-0">
        <section v-if="activeSubtab === 'main'" class="mt-4 space-y-4">
          <div class="rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-[#2a688f] dark:text-[#42b9eb]">Integra OCI</p>
                <h2 class="mt-1 text-xl font-semibold text-gray-900 dark:text-white">BPA Inteligente</h2>
                <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                  Valide APAC e BPA, confira a coerência da unidade e gere o arquivo tratado com rastreabilidade e menos ruído operacional.
                </p>
              </div>
              <div class="flex flex-wrap gap-2">
                <span class="rounded-md border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-200">
                  Importações: {{ summary.total_imports || 0 }}
                </span>
                <span class="rounded-md border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-200">
                  OCI removidos: {{ summary.total_removed_last_10 || 0 }}
                </span>
                <span class="rounded-md border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-slate-700 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-200">
                  Unidade líder: {{ summary.top_unit?.unit_cnes || '-' }}
                </span>
              </div>
            </div>
          </div>

          <div>
          <article class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div>
              <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Nova análise assistida</h3>
                  <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                    Selecione os arquivos de APAC e BPA para validar a unidade identificada, a competência, o volume de registros e a coerência entre as duas bases antes de gerar o BPA tratado.
                  </p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-600 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-300">
                  Fluxo guiado por consistência assistencial e depuração do BPA
                </div>
              </div>
              <div
                v-if="selectedUnitMatchStatus"
                :class="selectedUnitMatchStatus.classes"
                class="mt-4 rounded-xl px-4 py-3 text-sm font-medium"
              >
                {{ selectedUnitMatchStatus.label }}
              </div>
            </div>

            <form @submit.prevent="submitFiles" class="mt-6 space-y-5">
              <div class="grid grid-cols-1 gap-5 lg:grid-cols-2">
                <div>
                  <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-200">Arquivo APAC (.txt / .abr / Excel)</label>
                  <input
                    ref="apacInputRef"
                    type="file"
                    @change="handleFileChange('apac', $event)"
                    required
                    class="sr-only"
                  />
                  <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
                    <button
                      type="button"
                      @click="triggerApacInput"
                      class="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-[#13335a] transition hover:bg-[#eceded] dark:border-gray-600 dark:bg-gray-800 dark:text-[#42b9eb] dark:hover:bg-gray-700"
                    >
                      <Upload class="h-4 w-4" />
                      <span>Importar APAC</span>
                    </button>
                    <span class="text-sm text-gray-600 dark:text-gray-300">
                      {{ apacFile?.name || 'Nenhum arquivo selecionado' }}
                    </span>
                    <button
                      v-if="apacFile"
                      type="button"
                      @click="clearSelectedFile('apac')"
                      class="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
                      title="Remover arquivo APAC"
                    >
                      <Trash2 class="h-4 w-4" />
                    </button>
                  </div>
                  <div v-if="isAnalyzingApac" class="mt-2 space-y-1">
                    <p class="text-xs text-[#2a688f] dark:text-[#42b9eb]">Lendo APAC e detectando unidade...</p>
                    <p class="text-[11px] text-slate-500 dark:text-gray-400">Se ultrapassar {{ ANALYZE_FILE_TIMEOUT_LABEL }}, a análise será interrompida para proteger a conexão.</p>
                  </div>
                  <div v-if="apacFieldWarning" class="mt-3">
                    <OciAlert type="warn">{{ apacFieldWarning }}</OciAlert>
                  </div>
                  <div v-if="apacAnalysis" class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/50">
                    <div class="flex items-start justify-between gap-3">
                      <div>
                        <p class="text-sm font-semibold text-gray-900 dark:text-white">Arquivo APAC reconhecido</p>
                        <p class="text-xs text-gray-500 dark:text-gray-400">{{ apacAnalysis.file_name }}</p>
                      </div>
                      <OciFileBadge>{{ apacAnalysis.detected_format }}</OciFileBadge>
                    </div>
                    <dl class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                      <div v-for="item in buildAnalysisSummary(apacAnalysis)" :key="`apac-${item.label}`">
                        <dt class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">{{ item.label }}</dt>
                        <dd class="mt-1 text-sm font-medium text-gray-900 dark:text-gray-100">{{ item.value }}</dd>
                      </div>
                    </dl>
                  </div>
                  <div v-else class="mt-3 rounded-xl border border-dashed border-slate-300 bg-slate-50/80 p-4 dark:border-gray-600 dark:bg-gray-900/30">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">Aguardando arquivo APAC</p>
                    <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                      Assim que você selecionar o APAC, o sistema vai mostrar unidade, CNES, competência, quantidade de APACs, procedimentos e OCI identificados.
                    </p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">CNES</span>
                      <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">Competência</span>
                      <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">APACs</span>
                      <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">OCI</span>
                    </div>
                  </div>
                </div>

                <div>
                  <label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-200">Arquivo BPA (.txt / .abr / Excel)</label>
                  <input
                    ref="bpaInputRef"
                    type="file"
                    @change="handleFileChange('bpa', $event)"
                    required
                    class="sr-only"
                  />
                  <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
                    <button
                      type="button"
                      @click="triggerBpaInput"
                      class="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-[#13335a] transition hover:bg-[#eceded] dark:border-gray-600 dark:bg-gray-800 dark:text-[#42b9eb] dark:hover:bg-gray-700"
                    >
                      <Upload class="h-4 w-4" />
                      <span>Importar BPA</span>
                    </button>
                    <span class="text-sm text-gray-600 dark:text-gray-300">
                      {{ bpaFile?.name || 'Nenhum arquivo selecionado' }}
                    </span>
                    <button
                      v-if="bpaFile"
                      type="button"
                      @click="clearSelectedFile('bpa')"
                      class="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
                      title="Remover arquivo BPA"
                    >
                      <Trash2 class="h-4 w-4" />
                    </button>
                  </div>
                  <div v-if="isAnalyzingBpa" class="mt-2 space-y-1">
                    <p class="text-xs text-[#2a688f] dark:text-[#42b9eb]">Lendo BPA e detectando unidade...</p>
                    <p class="text-[11px] text-slate-500 dark:text-gray-400">Se ultrapassar {{ ANALYZE_FILE_TIMEOUT_LABEL }}, a análise será interrompida para proteger a conexão.</p>
                  </div>
                  <div v-if="bpaFieldWarning" class="mt-3">
                    <OciAlert type="warn">{{ bpaFieldWarning }}</OciAlert>
                  </div>
                  <div v-if="bpaAnalysis" class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/50">
                    <div class="flex items-start justify-between gap-3">
                      <div>
                        <p class="text-sm font-semibold text-gray-900 dark:text-white">Arquivo BPA reconhecido</p>
                        <p class="text-xs text-gray-500 dark:text-gray-400">{{ bpaAnalysis.file_name }}</p>
                      </div>
                      <OciFileBadge>{{ bpaAnalysis.detected_format }}</OciFileBadge>
                    </div>
                    <dl class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                      <div v-for="item in buildAnalysisSummary(bpaAnalysis)" :key="`bpa-${item.label}`">
                        <dt class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">{{ item.label }}</dt>
                        <dd class="mt-1 text-sm font-medium text-gray-900 dark:text-gray-100">{{ item.value }}</dd>
                      </div>
                    </dl>
                  </div>
                  <div v-else class="mt-3 rounded-xl border border-dashed border-slate-300 bg-slate-50/80 p-4 dark:border-gray-600 dark:bg-gray-900/30">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">Aguardando arquivo BPA</p>
                    <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                      Ao selecionar o BPA, a tela informa a unidade detectada, competência, volume de registros, procedimentos e a base que será usada para gerar o arquivo tratado.
                    </p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">Unidade</span>
                      <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">Linhas</span>
                      <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">Procedimentos</span>
                      <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">Quantidade</span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="!apacAnalysis && !bpaAnalysis && !isAnalyzingApac && !isAnalyzingBpa" class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-700 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-200">
                <p class="font-semibold">Como esta etapa funciona</p>
                <p class="mt-1">
                  Primeiro selecione os dois arquivos. A tela analisa automaticamente o conteúdo, identifica a unidade pelo CNES,
                  compara a coerência entre APAC e BPA e só depois segue para o processamento do arquivo tratado.
                </p>
              </div>

              <OciAlert v-if="selectedUnitMismatchWarning" type="warn" class="rounded-xl">
                {{ selectedUnitMismatchWarning }}
              </OciAlert>

              <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div class="text-sm text-gray-600 dark:text-gray-300">
                  <p>O sistema compara os registros OCI do APAC com o BPA para evitar duplicidade de produção e gerar um arquivo tratado pronto para conferência e download.</p>
                  <p v-if="resolvedSelectedUnit" class="mt-1 font-medium text-gray-800 dark:text-gray-100">
                    Importação preparada para {{ resolvedSelectedUnit.nome_unidade }}.
                  </p>
                </div>
                <button
                  type="submit"
                  :disabled="isLoading || isAnalyzingApac || isAnalyzingBpa"
                  class="inline-flex items-center justify-center gap-2 rounded-xl bg-[#13335a] px-5 py-3 text-sm font-semibold text-[#eceded] transition hover:bg-[#0f2a49] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-[#eceded] dark:text-[#13335a] dark:hover:bg-white"
                >
                  <span v-if="isLoading" class="mr-1 flex h-3.5 w-8 overflow-hidden rounded-sm bg-white/20 dark:bg-[#13335a]/20">
                    <span class="h-full w-1/2 animate-pulse rounded-sm bg-white dark:bg-[#13335a]"></span>
                  </span>
                  <Play v-else class="h-4 w-4" />
                  {{ isLoading ? `Processando arquivos... ${processingProgress}%` : 'Processar arquivos' }}
                </button>
              </div>
              <div v-if="isLoading" class="mt-4 rounded-xl border border-[#13335a]/10 bg-[#eceded]/70 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                <div class="flex items-center justify-between gap-3 text-xs font-semibold uppercase tracking-wide text-[#13335a] dark:text-[#42b9eb]">
                  <span>{{ processingProgressLabel }}</span>
                  <span>{{ processingProgress }}%</span>
                </div>
                <div class="mt-2 h-3 overflow-hidden rounded-md bg-white/80 dark:bg-gray-800">
                  <div
                    class="flex h-full items-center justify-end bg-[#2a688f] pr-2 text-[11px] font-semibold text-white transition-all duration-500 ease-out dark:bg-[#42b9eb]"
                    :style="{ width: `${Math.max(processingProgress, 8)}%` }"
                  >
                    {{ processingProgress }}%
                  </div>
                </div>
                <p class="mt-2 text-xs text-slate-600 dark:text-gray-300">
                  O processamento segue em andamento. Aguarde a conclusão da etapa atual.
                </p>
              </div>
            </form>

            <OciAlert v-if="errorMsg" type="error" class="mt-4">{{ errorMsg }}</OciAlert>
            <OciAlert v-if="successMsg" type="success" class="mt-4">
              <p class="font-semibold">{{ successMsg }}</p>
              <div v-if="lastProcessStats" class="mt-3 grid grid-cols-1 gap-2 text-xs sm:grid-cols-2 xl:grid-cols-7">
                <div class="rounded-lg border border-slate-200 bg-white p-2 dark:border-gray-600 dark:bg-gray-900/30">
                  <p class="font-medium text-gray-500 dark:text-gray-400">OCI no APAC</p>
                  <p class="mt-1 text-sm font-bold text-[#13335a] dark:text-[#eceded]">{{ lastProcessStats.apac_oci_count || 0 }}</p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-white p-2 dark:border-gray-600 dark:bg-gray-900/30">
                  <p class="font-medium text-gray-500 dark:text-gray-400">Linhas no BPA</p>
                  <p class="mt-1 text-sm font-bold text-[#13335a] dark:text-[#eceded]">
                    {{ lastProcessStats.bpa_lines_before || 0 }} -> {{ lastProcessStats.bpa_lines_after || 0 }}
                  </p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-white p-2 dark:border-gray-600 dark:bg-gray-900/30">
                  <p class="font-medium text-gray-500 dark:text-gray-400">Pacientes nao localizados</p>
                  <p class="mt-1 text-sm font-bold text-[#13335a] dark:text-[#eceded]">{{ notFoundPatients.length }}</p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-white p-2 dark:border-gray-600 dark:bg-gray-900/30">
                  <p class="font-medium text-gray-500 dark:text-gray-400">Procedimentos pendentes</p>
                  <p class="mt-1 text-sm font-bold text-[#13335a] dark:text-[#eceded]">{{ totalNotFoundProcedures + totalProcsNotFound }}</p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-white p-2 dark:border-gray-600 dark:bg-gray-900/30">
                  <p class="font-medium text-gray-500 dark:text-gray-400">Match por CPF</p>
                  <p class="mt-1 text-sm font-bold text-[#13335a] dark:text-[#eceded]">{{ lastProcessStats.matched_by_cpf || 0 }}</p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-white p-2 dark:border-gray-600 dark:bg-gray-900/30">
                  <p class="font-medium text-gray-500 dark:text-gray-400">Match por CNS</p>
                  <p class="mt-1 text-sm font-bold text-[#13335a] dark:text-[#eceded]">{{ lastProcessStats.matched_by_cns || 0 }}</p>
                </div>
                <div class="rounded-lg border border-slate-200 bg-white p-2 dark:border-gray-600 dark:bg-gray-900/30">
                  <p class="font-medium text-gray-500 dark:text-gray-400">Match por nome + nasc.</p>
                  <p class="mt-1 text-sm font-bold text-[#13335a] dark:text-[#eceded]">{{ lastProcessStats.matched_by_name_dob || 0 }}</p>
                </div>
              </div>
            </OciAlert>
          </article>

          </div>
        </section>

        <section v-if="activeSubtab === 'main' && hasCurrentResult" class="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Resultados da última importação carregada</h2>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                Veja o status do BPA tratado, pendências encontradas e detalhes da unidade processada.
              </p>
            </div>
            <div class="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
              <button
                v-if="lastGeneratedFileId"
                @click="downloadGeneratedFile"
                class="inline-flex items-center justify-center rounded-xl bg-[#13335a] px-4 py-2 text-sm font-semibold text-[#eceded] transition hover:opacity-90 dark:bg-[#eceded] dark:text-[#13335a]"
              >
                Baixar BPA limpo
              </button>
              <button
                v-if="lastRemovedOnlyFileId"
                @click="downloadRemovedOnlyFile"
                class="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-[#13335a] transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-[#42b9eb] dark:hover:bg-gray-700"
              >
                Baixar BPA removidos
              </button>
            </div>
          </div>

          <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            <article v-for="card in resultCards" :key="card.label" class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/50">
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">{{ card.label }}</p>
              <p class="mt-2 text-2xl font-bold text-gray-900 dark:text-white">{{ card.value }}</p>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">{{ card.helper }}</p>
            </article>
          </div>

          <div
            v-if="lastProcessStats"
            class="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-gray-800 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-200"
          >
            <p class="font-semibold">
              {{ lastProcessStats.oci_patients_removed ? 'O BPA tratado sofreu remocoes/ajustes a partir do cruzamento com o APAC.' : 'Nenhuma linha OCI foi removida nesta importacao.' }}
            </p>
            <p class="mt-2">
              {{ processOutcomeExplanation }}
            </p>
            <ul v-if="processOutcomeNotes.length" class="mt-3 list-disc space-y-1 pl-5">
              <li v-for="note in processOutcomeNotes" :key="note">{{ note }}</li>
            </ul>
          </div>

          <div class="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
            <div class="rounded-xl border border-slate-200 p-4 dark:border-gray-700">
              <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Distribuição do BPA tratado</h3>
              <div class="mt-4 h-72">
                <Doughnut v-if="latestStatusChartData" :data="latestStatusChartData" :options="latestStatusChartOptions" />
                <p v-else class="flex h-full items-center justify-center text-sm text-gray-500 dark:text-gray-400">Sem linhas processadas para consolidar.</p>
              </div>
            </div>

            <div class="rounded-xl border border-slate-200 p-4 dark:border-gray-700">
              <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Pendências e achados</h3>
              <div class="mt-4 h-72">
                <Bar v-if="latestPendingChartData" :data="latestPendingChartData" :options="latestPendingChartOptions" />
                <p v-else class="flex h-full items-center justify-center text-sm text-gray-500 dark:text-gray-400">Sem pendências registradas para esta importação.</p>
              </div>
            </div>
          </div>

          <div
            v-if="ociComboDetails.length"
            ref="ociComboDetailsSectionRef"
            class="mt-6 rounded-xl border border-slate-200 p-4 dark:border-gray-700"
          >
            <div class="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Combos assistenciais identificados</h3>
                <p class="text-sm text-gray-600 dark:text-gray-300">
                  Veja quais pacientes vieram com combinação assistencial no APAC, qual foi o procedimento principal e quais procedimentos compõem esse conjunto para confronto com o BPA.
                </p>
              </div>
              <div class="text-sm text-gray-600 dark:text-gray-300">
                {{ ociComboDetails.length }} paciente(s) | {{ totalOciComboProcedures }} procedimento(s) vinculados | {{ totalOciComboRemoved }} removido(s)
              </div>
            </div>

            <div class="mt-4 space-y-4">
              <div class="grid gap-3 md:grid-cols-3">
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Pacientes identificados</p>
                  <p class="mt-1 text-lg font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ ociComboDetails.length }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Procedimentos vinculados</p>
                  <p class="mt-1 text-lg font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ totalOciComboProcedures }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Faixa exibida</p>
                  <p class="mt-1 text-sm font-semibold text-gray-700 dark:text-gray-200">{{ ociComboDetailsRangeLabel }}</p>
                </div>
              </div>

              <div ref="ociComboDetailsListRef" class="max-h-[62vh] space-y-4 overflow-y-auto pr-1">
                <article
                  v-for="(patient, index) in paginatedOciComboDetails"
                  :key="`combo-${patient.name}-${patient.dob}-${index}`"
                  class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/40"
                >
                <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-white">
                      <span>{{ getPatientDisplayName(patient) }} | Nasc. {{ formatPatientDob(patient.dob) }}</span>
                      <button @click.stop="togglePatientMask(patient)" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" title="Mostrar/Ocultar dados (LGPD)">
                        <svg v-if="isPatientMasked(patient)" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.478 0-8.268-2.943-9.542-7z" /></svg>
                        <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.978 9.978 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                      </button>
                    </div>
                    <p v-if="formatMaskedPatientIdentifiers(patient)" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      {{ formatMaskedPatientIdentifiers(patient) }}
                    </p>
                    <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                      APAC {{ patient.apac_num || '-' }} | Procedimento principal OCI:
                      <span class="font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ formatProcedureCodeWithName(patient.principal_proc, patient.principal_proc_name) }}</span>
                    </p>
                  </div>
                  <div class="flex flex-wrap gap-2 text-xs font-semibold">
                    <span class="rounded-full bg-slate-100 px-2.5 py-1 text-slate-700 dark:bg-gray-700 dark:text-gray-200">
                      {{ patient.total_procedures || 0 }} proc. no combo
                    </span>
                    <span class="rounded-full bg-slate-100 px-2.5 py-1 text-slate-700 dark:bg-gray-700 dark:text-gray-200">
                      {{ patient.total_removed || 0 }} removido(s)
                    </span>
                    <span
                      class="rounded-full px-2.5 py-1"
                      :class="patient.total_remaining ? 'bg-slate-200 text-slate-800 dark:bg-slate-600 dark:text-slate-100' : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'"
                    >
                      {{ patient.total_remaining || 0 }} pendente(s)
                    </span>
                  </div>
                </div>

                <div class="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-3">
                  <div class="rounded-xl border border-slate-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-800/70">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Procedimentos do combo assistencial</p>
                    <div v-if="patient.procedure_details?.length" class="mt-3 flex flex-col gap-1">
                      <span
                        v-for="item in patient.procedure_details"
                        :key="`${patient.name}-proc-${item.code}`"
                        class="text-xs text-gray-700 dark:text-gray-200"
                      >
                        {{ formatProcedureDisplay(item) }}
                      </span>
                    </div>
                    <p v-else class="mt-3 text-sm text-gray-500 dark:text-gray-400">Sem procedimentos detalhados para este combo.</p>
                  </div>

                  <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Procedimentos removidos do BPA</p>
                    <div v-if="patient.removed_procedure_details?.length" class="mt-3 flex flex-col gap-1">
                      <span
                        v-for="item in patient.removed_procedure_details"
                        :key="`${patient.name}-removed-${item.code}`"
                        class="text-xs text-gray-600 dark:text-gray-300"
                      >
                        {{ formatProcedureDisplay(item) }}
                      </span>
                    </div>
                    <p v-else class="mt-3 text-sm text-gray-600 dark:text-gray-300">Nenhum procedimento deste combo foi removido do BPA.</p>
                  </div>

                  <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Procedimentos ainda pendentes</p>
                    <div v-if="patient.remaining_procedure_details?.length" class="mt-3 flex flex-col gap-1">
                      <span
                        v-for="item in patient.remaining_procedure_details"
                        :key="`${patient.name}-remaining-${item.code}`"
                        class="text-xs text-gray-600 dark:text-gray-300"
                      >
                        {{ formatProcedureDisplay(item) }}
                      </span>
                    </div>
                    <p v-else class="mt-3 text-sm text-gray-600 dark:text-gray-300">Todos os procedimentos do combo tiveram correspondencia no BPA.</p>
                  </div>
                </div>
                </article>
              </div>

              <div v-if="ociComboDetailsTotalPages > 1" class="flex flex-col gap-3 border-t border-slate-200 pt-4 md:flex-row md:items-center md:justify-between dark:border-gray-700">
                <div class="text-sm text-gray-600 dark:text-gray-300">
                  Exibindo {{ ociComboDetailsRangeLabel }} de {{ ociComboDetails.length }} paciente(s) com combo identificado.
                </div>
                <div class="flex flex-wrap items-center gap-2 text-sm">
                  <button
                    type="button"
                    @click="goToPreviousOciComboDetailsPage"
                    class="rounded-lg border px-3 py-1.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
                    style="border-color: #13335a; color: #13335a;"
                    :disabled="ociComboDetailsPage === 1"
                  >
                    Anterior
                  </button>
                  <span class="rounded-lg px-3 py-1.5 font-semibold text-white" style="background-color: #13335a;">
                    Página {{ ociComboDetailsPage }} de {{ ociComboDetailsTotalPages }}
                  </span>
                  <button
                    type="button"
                    @click="goToNextOciComboDetailsPage"
                    class="rounded-lg border px-3 py-1.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
                    style="border-color: #13335a; color: #13335a;"
                    :disabled="ociComboDetailsPage >= ociComboDetailsTotalPages"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2" v-if="notFoundPatients.length || procsNotFoundPatients.length">
            <div v-if="notFoundPatients.length" class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-gray-800 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-200">
              <p class="font-semibold">Pacientes do APAC não encontrados no BPA</p>
              <p class="mt-1 text-xs uppercase tracking-wide">Total de pacientes: {{ notFoundPatients.length }} | Procedimentos pendentes: {{ totalNotFoundProcedures }}</p>
              <ul class="mt-3 max-h-44 list-disc space-y-1 overflow-y-auto pl-5">
                <li v-for="(patient, index) in notFoundPatients" :key="`nf-${index}`">
                  <div class="flex items-center gap-2 font-medium">
                    <span>{{ getPatientDisplayName(patient) }} | Nasc. {{ formatPatientDob(patient.dob) }} | {{ patient.total_procs || 0 }} proc.</span>
                    <button @click.stop="togglePatientMask(patient)" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" title="Mostrar/Ocultar dados (LGPD)">
                      <svg v-if="isPatientMasked(patient)" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.478 0-8.268-2.943-9.542-7z" /></svg>
                      <svg v-else class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.978 9.978 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                    </button>
                  </div>
                  <div v-if="formatMaskedPatientIdentifiers(patient)" class="text-xs text-gray-500 dark:text-gray-400">
                    {{ formatMaskedPatientIdentifiers(patient) }}
                  </div>
                  <div v-if="patient.procedure_details?.length" class="mt-1 flex flex-col gap-1">
                    <span
                      v-for="item in patient.procedure_details"
                      :key="`${patient.name}-${item.code}`"
                      class="text-xs"
                    >
                      {{ formatProcedureDisplay(item) }}
                    </span>
                  </div>
                </li>
              </ul>
            </div>

            <div v-if="procsNotFoundPatients.length" class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-gray-800 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-200">
              <p class="font-semibold">Pacientes encontrados com procedimentos pendentes</p>
              <p class="mt-1 text-xs uppercase tracking-wide">Total de pacientes: {{ procsNotFoundPatients.length }} | Procedimentos pendentes: {{ totalProcsNotFound }}</p>
              <ul class="mt-3 max-h-44 list-disc space-y-1 overflow-y-auto pl-5">
                <li v-for="(patient, index) in procsNotFoundPatients" :key="`pnf-${index}`">
                  <div class="flex items-center gap-2 font-medium">
                    <span>{{ getPatientDisplayName(patient) }} | Nasc. {{ formatPatientDob(patient.dob) }} | {{ patient.total_leftover || 0 }} proc.</span>
                    <button @click.stop="togglePatientMask(patient)" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" title="Mostrar/Ocultar dados (LGPD)">
                      <svg v-if="isPatientMasked(patient)" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.478 0-8.268-2.943-9.542-7z" /></svg>
                      <svg v-else class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.978 9.978 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                    </button>
                  </div>
                  <div v-if="formatMaskedPatientIdentifiers(patient)" class="text-xs text-gray-500 dark:text-gray-400">
                    {{ formatMaskedPatientIdentifiers(patient) }}
                  </div>
                  <div v-if="patient.leftover_details?.length" class="mt-1 flex flex-col gap-1">
                    <span
                      v-for="item in patient.leftover_details"
                      :key="`${patient.name}-${item.code}`"
                      class="text-xs"
                    >
                      {{ formatProcedureDisplay(item) }}
                    </span>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          <div class="mt-6">
            <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Linhas afetadas do BPA</h3>
                <p class="text-sm text-gray-600 dark:text-gray-300">
                  As linhas permanecem coloridas por status: excluído, quantidade alterada ou mantido.
                </p>
              </div>
              <div class="relative w-full md:w-72">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Pesquisar resultados..."
                  class="w-full rounded-xl border border-gray-300 bg-white py-2 pl-10 pr-4 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#13335a] dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 dark:focus:ring-[#42b9eb]"
                />
                <svg class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
            </div>

            <div class="mt-4 max-h-[520px] overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="sticky top-0 bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Status</th>
                    <th v-for="col in affectedColumns" :key="col" class="whitespace-nowrap px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">
                      {{ col }}
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-800">
                  <tr
                    v-for="(row, idx) in filteredAffectedRows"
                    :key="idx"
                    :class="rowClass(row._status)"
                  >
                    <td class="whitespace-nowrap px-3 py-2 text-xs font-semibold" :class="rowStatusClass(row._status)">
                      {{ rowStatusLabel(row._status) }}
                    </td>
                    <td v-for="col in affectedColumns" :key="col" class="whitespace-nowrap px-3 py-2 text-xs text-gray-900 dark:text-gray-200">
                      {{ row[col] }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section v-if="activeSubtab === 'history' && userStore.hasModuleItemAccess('integra_oci', 'historico')" class="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Histórico por arquivos</h2>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                Expanda uma linha para inspecionar usuário, unidade, competência e carregar novamente os detalhes da importação.
              </p>
            </div>
          </div>

          <div v-if="historyData.length" class="mt-6 overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Data</th>
                  <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Usuário</th>
                  <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Unidade</th>
                  <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">CNES</th>
                  <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">APAC</th>
                  <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">BPA</th>
                  <th class="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">OCI removidos</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-800">
                <template v-for="item in reversedHistoryData" :key="item.id">
                  <tr @click="toggleRow(item.id)" class="cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-900 dark:text-gray-200">
                      <div class="flex items-center">
                        <svg :class="{ 'rotate-90': expandedRows.includes(item.id) }" class="mr-2 h-4 w-4 transition-transform duration-200 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                        {{ formatDateTime(item.created_at) }}
                      </div>
                    </td>
                    <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-900 dark:text-gray-200">{{ item.user || '-' }}</td>
                    <td class="max-w-[240px] truncate px-4 py-3 text-sm text-gray-900 dark:text-gray-200" :title="item.unit_name">{{ item.unit_name }}</td>
                    <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-900 dark:text-gray-200">{{ item.unit_cnes || '-' }}</td>
                    <td class="max-w-[180px] truncate px-4 py-3 text-sm text-gray-900 dark:text-gray-200" :title="item.apac_filename">{{ item.apac_filename }}</td>
                    <td class="max-w-[180px] truncate px-4 py-3 text-sm text-gray-900 dark:text-gray-200" :title="item.bpa_filename">{{ item.bpa_filename }}</td>
                    <td class="whitespace-nowrap px-4 py-3 text-center text-sm font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ item.oci_patients_removed }}</td>
                  </tr>
                  <tr v-if="expandedRows.includes(item.id)" class="bg-gray-50 dark:bg-gray-700/30">
                    <td colspan="7" class="border-b border-gray-100 px-6 py-4 dark:border-gray-600">
                      <div class="grid grid-cols-2 gap-4 text-sm md:grid-cols-5">
                        <div>
                          <p class="mb-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Usuário</p>
                          <p class="text-gray-900 dark:text-gray-200">{{ item.user }}</p>
                        </div>
                        <div>
                          <p class="mb-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">OCI no APAC</p>
                          <p class="text-gray-900 dark:text-gray-200">{{ item.apac_oci_count }}</p>
                        </div>
                        <div>
                          <p class="mb-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Linhas BPA antes</p>
                          <p class="text-gray-900 dark:text-gray-200">{{ item.bpa_lines_before }}</p>
                        </div>
                        <div>
                          <p class="mb-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Linhas BPA depois</p>
                          <p class="text-gray-900 dark:text-gray-200">{{ item.bpa_lines_after }}</p>
                        </div>
                        <div>
                          <p class="mb-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Competências</p>
                          <p class="text-gray-900 dark:text-gray-200">{{ formatCompetencias(item.competencias) }}</p>
                        </div>
                      </div>
                      <div class="mt-4 flex justify-end">
                        <button @click.stop="loadHistoryDetails(item)" class="text-sm font-medium text-[#13335a] hover:underline dark:text-[#42b9eb]">
                          Ver resultados dessa importação
                        </button>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>

          <div v-else class="flex h-40 items-center justify-center text-sm text-gray-500 dark:text-gray-400">
            Nenhuma importação registrada ainda.
          </div>
        </section>

              </div>
              <div v-else-if="activeTab === 'combos' && userStore.hasModuleItemAccess('integra_oci', 'formar_combos')" key="combos" class="min-w-0">
        <section class="mt-4 rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div class="flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
            <div class="max-w-4xl">
              <p class="text-xs font-semibold uppercase tracking-wide text-[#2a688f] dark:text-[#42b9eb]">Integra OCI</p>
              <h2 class="mt-1 text-xl font-semibold text-gray-900 dark:text-white">Validação de Combos</h2>
              <p class="mt-2 max-w-3xl text-sm leading-5 text-gray-600 dark:text-gray-300">
                Estruture a análise por competência com um BPA único ou base consolidada de múltiplos BPAs, adicionando planilhas complementares apenas quando a regra exigir reforço assistencial.
              </p>
              <div class="mt-3 flex flex-wrap gap-2">
                <span class="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-300">1 ou vários BPAs</span>
                <span class="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-300">Planilha opcional</span>
                <span class="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-300">Validação por regra</span>
              </div>
            </div>
            <div v-if="ociComboResolvedUnit" class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-900/40">
              <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-gray-400">Base consolidada</p>
              <p class="mt-1 text-sm font-semibold text-gray-900 dark:text-white">{{ ociComboResolvedUnit.nome_unidade }}</p>
              <p v-if="ociComboResolvedUnit.cnes" class="text-xs text-slate-500 dark:text-gray-400">CNES {{ ociComboResolvedUnit.cnes }}</p>
            </div>
          </div>
        </section>

        <section v-if="activeSubtab === 'main'" class="mt-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <form @submit.prevent="submitOciComboFiles" class="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.5fr)_320px]">
            <div class="space-y-4">
              <div class="rounded-xl border border-slate-200 bg-[#eceded]/55 p-4 dark:border-gray-700 dark:bg-gray-900/30">
                <div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-[#2a688f] dark:text-[#42b9eb]">Etapa 1</p>
                    <h3 class="mt-1 text-base font-semibold text-[#13335a] dark:text-white">Base BPA da análise</h3>
                    <p class="mt-1 text-xs text-gray-600 dark:text-gray-300">
                      Selecione os BPAs da competência. O sistema identifica unidade, CNES e competência para formar a base assistencial do combo.
                    </p>
                  </div>
                  <span class="rounded-md bg-white px-3 py-1 text-xs font-semibold text-[#13335a] shadow-sm dark:bg-gray-800 dark:text-[#42b9eb]">
                    Obrigatório
                  </span>
                </div>

                <label class="mt-3 block text-sm font-medium text-gray-700 dark:text-gray-200">Arquivo(s) BPA para validação de combos</label>
                <input
                  ref="ociComboBpaInputRef"
                  type="file"
                  multiple
                  @change="handleOciComboBpaFileChange"
                  class="sr-only"
                />
                <div class="mt-2 flex flex-col gap-2 sm:flex-row sm:items-center">
                  <button
                    type="button"
                    @click="triggerOciComboBpaInput"
                    class="inline-flex items-center justify-center gap-2 rounded-lg border border-[#13335a]/15 bg-[#13335a] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#0f2a49] dark:border-[#42b9eb]/20 dark:bg-[#13335a] dark:text-[#eceded]"
                  >
                    <Upload class="h-4 w-4" />
                    <span>Importar BPA</span>
                  </button>
                  <span class="text-sm text-gray-600 dark:text-gray-300">
                    {{ ociComboBpaFiles.length ? `${ociComboBpaFiles.length} arquivo(s) selecionado(s)` : 'Nenhum arquivo selecionado' }}
                  </span>
                  <button
                    v-if="ociComboBpaFiles.length"
                    type="button"
                    @click="clearOciComboBpaFiles"
                    class="inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
                  >
                    <Trash2 class="h-4 w-4" />
                    <span>Limpar BPAs</span>
                  </button>
                </div>
                <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Voce pode adicionar um BPA agora e incluir outros depois, mesmo em pastas diferentes. O seletor abre com todos os arquivos visiveis.
                </p>
                <p v-if="isAnalyzingOciComboBpa" class="mt-2 text-xs font-medium text-[#2a688f] dark:text-[#42b9eb]">Lendo BPA para consolidar procedimentos por paciente...</p>
                <OciAlert v-if="ociComboBpaFieldWarning" type="warn" class="mt-3">{{ ociComboBpaFieldWarning }}</OciAlert>

                <div v-if="ociComboBpaFiles.length" class="mt-3 rounded-xl border border-slate-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-800">
                  <div class="flex items-start justify-between gap-3">
                    <div>
                      <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ ociComboBpaFiles.length > 1 ? 'Arquivos BPA selecionados' : 'Arquivo BPA selecionado' }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">{{ ociComboBpaFiles.length }} arquivo(s) pronto(s) para análise</p>
                    </div>
                    <OciFileBadge>{{ ociComboBpaFiles.length > 1 ? 'Multi-BPA' : 'BPA único' }}</OciFileBadge>
                  </div>
                  <div class="mt-2 space-y-2">
                    <div
                      v-for="file in ociComboBpaFiles"
                      :key="`oci-bpa-selected-${file.name}-${file.size}`"
                      class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 dark:border-gray-700 dark:bg-gray-900/40"
                    >
                      <div class="flex items-start justify-between gap-3">
                        <p class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ file.name }}</p>
                        <button
                          type="button"
                          @click="removeOciComboBpaFile(file)"
                          :class="ociClasses.btnClearIcon"
                          title="Excluir este BPA"
                        >
                          <Trash2 class="h-3.5 w-3.5" />
                        </button>
                      </div>
                      <p
                        v-if="getOciSelectedBpaFileMeta(file)"
                        class="mt-2 text-xs text-gray-600 dark:text-gray-300"
                      >
                        {{ formatOciSelectedBpaFileMeta(getOciSelectedBpaFileMeta(file)) }}
                      </p>
                      <p
                        v-else-if="isAnalyzingOciComboBpa"
                        class="mt-2 text-xs text-[#2a688f] dark:text-[#42b9eb]"
                      >
                        Identificando unidade, CNES e competência...
                      </p>
                    </div>
                  </div>
                </div>

                <div v-if="ociComboBpaAnalysis" class="mt-3 rounded-xl border border-slate-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-800">
                  <div class="flex items-start justify-between gap-3">
                    <div>
                      <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ ociComboBpaAnalysis.file_count > 1 ? 'BPAs reconhecidos' : 'BPA reconhecido' }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">{{ ociComboBpaAnalysis.file_name }}</p>
                    </div>
                    <OciFileBadge>{{ ociComboAnalysisModeLabel }}</OciFileBadge>
                  </div>
                  <dl class="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
                    <div v-for="item in buildAnalysisSummary(ociComboBpaAnalysis)" :key="`oci-bpa-${item.label}`">
                      <dt class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">{{ item.label }}</dt>
                      <dd class="mt-1 text-sm font-medium text-gray-900 dark:text-gray-100">{{ item.value }}</dd>
                    </div>
                  </dl>
                  <div v-if="ociComboBpaAnalyses.length > 1" class="mt-3 space-y-2">
                    <div
                      v-for="fileAnalysis in ociComboBpaAnalyses"
                      :key="`oci-bpa-file-${fileAnalysis.file_name}`"
                      class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 dark:border-gray-700 dark:bg-gray-900/40"
                    >
                      <div class="flex flex-wrap items-center justify-between gap-2">
                        <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ fileAnalysis.file_name }}</p>
                        <OciFileBadge>{{ fileAnalysis.detected_format }}</OciFileBadge>
                      </div>
                      <p class="mt-2 text-xs text-gray-600 dark:text-gray-300">
                        {{ formatAnalysisUnitsSummary(fileAnalysis) }}
                        <span> | Competência {{ formatCompetencias(fileAnalysis.competencias) }}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="hasCnes2970643" class="rounded-xl border border-slate-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
                <div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-wide text-[#2a688f] dark:text-[#42b9eb]">Etapa 2</p>
                    <h3 class="mt-1 text-base font-semibold text-[#13335a] dark:text-white">Planilha complementar</h3>
                    <p class="mt-1 text-xs text-gray-600 dark:text-gray-300">
                      Use uma ou mais planilhas apenas quando a regra do combo exigir reforço por procedimentos complementares.
                    </p>
                  </div>
                  <span class="rounded-md bg-[#eceded] px-3 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">
                    Opcional
                  </span>
                </div>

                <label class="mt-3 block text-sm font-medium text-gray-700 dark:text-gray-200">Planilha complementar de procedimentos</label>
                <input
                  ref="ociComboProceduresInputRef"
                  type="file"
                  multiple
                  accept=".xls, .xlsx"
                  @change="handleOciComboProceduresFileChange"
                  class="sr-only"
                />
                <div class="mt-2 flex flex-col gap-2 sm:flex-row sm:items-center">
                  <button
                    type="button"
                    @click="triggerOciComboProceduresInput"
                    class="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-[#13335a] transition hover:bg-[#eceded] dark:border-gray-600 dark:bg-gray-800 dark:text-[#42b9eb] dark:hover:bg-gray-700"
                  >
                    <Upload class="h-4 w-4" />
                    <span>Importar planilha</span>
                  </button>
                  <span class="text-sm text-gray-600 dark:text-gray-300">
                    {{ ociComboProceduresFiles.length ? `${ociComboProceduresFiles.length} arquivo(s) selecionado(s)` : 'Nenhum arquivo selecionado' }}
                  </span>
                  <button
                    v-if="ociComboProceduresFiles.length"
                    type="button"
                    @click="clearOciComboProcedureFiles"
                    class="inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
                  >
                    <Trash2 class="h-4 w-4" />
                    <span>Limpar planilhas</span>
                  </button>
                </div>
                <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  As planilhas entram como fonte adicional de procedimentos OCI quando a regra operacional exigir complemento assistencial, aceitando tanto o layout analítico tradicional quanto arquivos com <span class="font-semibold">procedimento_id</span>, e nunca substituem os BPAs.
                </p>

                <div v-if="ociComboProceduresFiles.length" class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <div class="flex items-start justify-between gap-3">
                    <div>
                      <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ ociComboProceduresFiles.length > 1 ? 'Planilhas complementares selecionadas' : 'Planilha complementar selecionada' }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">{{ ociComboProceduresFiles.length }} arquivo(s) pronto(s) para análise</p>
                    </div>
                    <span class="rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-800 dark:text-[#42b9eb]">
                      {{ ociComboProceduresFiles.length > 1 ? 'Múltiplas planilhas' : 'Planilha complementar' }}
                    </span>
                  </div>
                  <div class="mt-2 grid grid-cols-1 gap-2 lg:grid-cols-2">
                    <div
                      v-for="file in ociComboProceduresFiles"
                      :key="`oci-procedures-${file.name}-${file.size}`"
                      class="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-gray-900 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                    >
                      <span class="min-w-0 break-all">{{ file.name }}</span>
                      <button
                        type="button"
                        @click="removeOciComboProcedureFile(file)"
                        class="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white p-1.5 text-slate-600 transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
                        title="Excluir esta planilha"
                      >
                        <Trash2 class="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <aside class="space-y-3">
              <div class="rounded-xl border border-[#13335a]/10 bg-[#eceded] p-4 text-[#13335a] dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-200">
                <div class="flex items-start gap-3">
                  <div class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#13335a] text-sm font-bold text-white dark:bg-[#42b9eb] dark:text-[#13335a]">
                    i
                  </div>
                  <div class="min-w-0">
                    <div class="flex items-center justify-between gap-2">
                    <p class="text-sm font-semibold">Regra de validação assistencial</p>
                    </div>
                    <p class="mt-1.5 text-xs leading-5">
                      O combo assistencial só é validado quando os procedimentos obrigatórios da regra são encontrados para o mesmo paciente dentro da base analisada.
                    </p>
                  </div>
                </div>

              </div>

              <div class="rounded-xl border border-slate-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
                <p class="text-xs font-semibold uppercase tracking-wide text-[#2a688f] dark:text-[#42b9eb]">Resumo operacional</p>
                <div class="mt-3 space-y-2">
                  <div class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 dark:border-gray-700 dark:bg-gray-900/40">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Modo da análise</p>
            <p class="mt-1 text-sm font-semibold text-gray-900 dark:text-white">
              {{
                ociComboBpaFiles.length
                  ? (ociComboBpaFiles.length > 1 ? 'Consolidação multi-BPA por paciente' : 'Análise com BPA único')
                  : (ociComboProceduresFiles.length ? 'Análise por planilha complementar' : 'Aguardando arquivos')
              }}
            </p>
                  </div>
                  <div v-if="hasCnes2970643" class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 dark:border-gray-700 dark:bg-gray-900/40">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Planilha complementar</p>
                    <p class="mt-1 text-sm font-semibold text-gray-900 dark:text-white">{{ ociComboProceduresFiles.length ? `${ociComboProceduresFiles.length} arquivo(s) selecionado(s)` : 'Não informada' }}</p>
                  </div>
                  <div class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 dark:border-gray-700 dark:bg-gray-900/40">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Base detectada</p>
                    <p class="mt-1 text-sm font-semibold text-gray-900 dark:text-white">{{ ociComboResolvedUnit?.nome_unidade || 'Aguardando leitura dos arquivos' }}</p>
                    <p v-if="ociComboResolvedUnit?.cnes" class="mt-1 text-xs text-gray-500 dark:text-gray-400">CNES {{ ociComboResolvedUnit.cnes }}</p>
                  </div>
                </div>
              </div>

              <div class="rounded-xl border border-slate-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
                <p class="text-sm font-semibold text-[#13335a] dark:text-white">Pronto para analisar</p>
                <p class="mt-1.5 text-xs leading-5 text-gray-600 dark:text-gray-300">
                  Esta validação do Integra OCI mantém a rastreabilidade dos arquivos usados na consolidação e, quando localizar o BPA do CCE (CNES 2970643), já gera o BPA tratado em sequência.
                </p>
                <button
                  type="submit"
                  :disabled="isOciComboLoading || isAnalyzingOciComboBpa"
                  class="mt-3 inline-flex w-full items-center justify-center rounded-xl bg-[#13335a] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#0f2a49] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-[#2a688f] dark:hover:bg-[#13335a]"
                >
                  <span v-if="isOciComboLoading" class="mr-2 flex h-3.5 w-8 overflow-hidden rounded-sm bg-white/20">
                    <span class="h-full w-1/2 animate-pulse rounded-sm bg-white"></span>
                  </span>
                  {{ `Processar` }}
                </button>
                <div v-if="isOciComboLoading" class="mt-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 dark:border-gray-600 dark:bg-gray-900/40">
                  <div class="flex items-center justify-between gap-3 text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-600 dark:text-gray-300">
                    <span>{{ ociComboProgressLabel }}</span>
                    <span>{{ ociComboProgress }}%</span>
                  </div>
                  <div class="mt-2 h-2 overflow-hidden rounded-md bg-slate-200 dark:bg-gray-700">
                    <div
                      class="h-full bg-[#2a688f] transition-all duration-500 ease-out dark:bg-[#42b9eb]"
                      :style="{ width: `${Math.max(ociComboProgress, 8)}%` }"
                    ></div>
                  </div>
                  <p class="mt-2 text-xs leading-5 text-slate-500 dark:text-gray-400">
                    O processamento segue em andamento. Aguarde a conclusão da etapa atual.
                  </p>
                </div>
              </div>
            </aside>
          </form>

          <OciAlert v-if="ociCompetenceWarning" type="warn" class="mt-4">{{ ociCompetenceWarning }}</OciAlert>
          <OciAlert v-if="ociComboErrorMsg" type="error" class="mt-4">{{ ociComboErrorMsg }}</OciAlert>
          <OciAlert v-if="ociComboSuccessMsg" type="success" class="mt-4">{{ ociComboSuccessMsg }}</OciAlert>
          <div v-if="ociGeneratedTreatedBpas.length" class="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
            <div
              v-for="treatedBpa in ociGeneratedTreatedBpas"
              :key="`${treatedBpa.target_code || treatedBpa.target_cnes}-${treatedBpa.file_id || 'nao-gerado'}`"
              class="rounded-xl border p-4"
              :class="treatedBpa.generated
                ? 'border-[#13335a]/20 bg-[#eceded] text-[#13335a] dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-100'
                : 'border-slate-200 bg-slate-50 text-gray-800 dark:border-gray-600 dark:bg-gray-900/30 dark:text-gray-200'"
            >
              <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p class="text-sm font-semibold">
                    {{ treatedBpa.generated
                      ? `BPA tratado do ${treatedBpa.target_code || treatedBpa.target_display_name || treatedBpa.target_cnes} gerado junto da validacao`
                      : `BPA tratado do ${treatedBpa.target_code || treatedBpa.target_display_name || treatedBpa.target_cnes} nao gerado nesta validacao` }}
                  </p>
                  <p class="mt-1 text-xs">
                    <template v-if="treatedBpa.generated">
                      Arquivo base: {{ treatedBpa.source_bpa_file_name }} | CNES alvo {{ treatedBpa.target_cnes }}
                    </template>
                    <template v-else>
                      {{ treatedBpa.notice }}
                    </template>
                  </p>
                </div>
                <div class="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
                  <button
                    v-if="treatedBpa.generated"
                    type="button"
                    @click="downloadGeneratedFileById(treatedBpa.file_id, treatedBpa.file_name)"
                    class="inline-flex items-center justify-center rounded-xl bg-[#13335a] px-4 py-2 text-sm font-semibold text-[#eceded] transition hover:opacity-90 dark:bg-[#eceded] dark:text-[#13335a]"
                  >
                    Baixar BPA limpo ({{ treatedBpa.target_code || treatedBpa.target_cnes }})
                  </button>
                  <button
                    v-if="treatedBpa.removed_only_file_id"
                    type="button"
                    @click="downloadGeneratedFileById(treatedBpa.removed_only_file_id, treatedBpa.removed_only_file_name)"
                    class="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-[#13335a] transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-[#42b9eb] dark:hover:bg-gray-700"
                  >
                    Baixar BPA removidos ({{ treatedBpa.target_code || treatedBpa.target_cnes }})
                  </button>
                </div>
              </div>
              <div v-if="treatedBpa.generated" class="mt-4 grid grid-cols-1 gap-3 md:grid-cols-4">
                <div class="rounded-xl border border-slate-200 bg-white px-3 py-3 dark:border-gray-700 dark:bg-gray-800/70">
                  <p class="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Linhas no BPA</p>
                  <p class="mt-1 text-sm font-semibold text-gray-900 dark:text-white">
                    {{ treatedBpa.stats?.bpa_lines_before || 0 }} -> {{ treatedBpa.stats?.bpa_lines_after || 0 }}
                  </p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-white px-3 py-3 dark:border-gray-700 dark:bg-gray-800/70">
                  <p class="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Remoções / ajustes</p>
                  <p class="mt-1 text-sm font-semibold text-gray-900 dark:text-white">{{ treatedBpa.stats?.oci_patients_removed || 0 }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-white px-3 py-3 dark:border-gray-700 dark:bg-gray-800/70">
                  <p class="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Pacientes de combo encontrados</p>
                  <p class="mt-1 text-sm font-semibold text-gray-900 dark:text-white">{{ treatedBpa.stats?.combo_patients_found_in_bpa || 0 }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-white px-3 py-3 dark:border-gray-700 dark:bg-gray-800/70">
                  <p class="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Ocorrências consideradas</p>
                  <p class="mt-1 text-sm font-semibold text-gray-900 dark:text-white">{{ treatedBpa.stats?.combo_occurrences_considered || 0 }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section v-if="activeSubtab === 'main' && ociComboResult" class="mt-4">
          <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div class="mb-4 flex items-center gap-3">
              <span class="inline-flex h-3 w-3 shrink-0 rounded-full bg-[#2a688f]"></span>
              <div class="h-px flex-1 border-t border-dashed border-[#2a688f]/50 dark:border-[#42b9eb]/40"></div>
              <span class="rounded-full bg-[#eceded] px-3 py-1 text-xs font-semibold uppercase tracking-wide text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">
                Análise concluída
              </span>
            </div>

            <div class="mb-3 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Resultado atual da validação</h2>
                <p class="mt-1 text-xs text-gray-600 dark:text-gray-300">
                  Veja com clareza quantos combos foram identificados, quantos validaram a regra final e quantos ficaram pendentes por CID ou por falta de procedimento.
                </p>
                <p v-if="ociComboResult?.summary?.supplemental_sheet_used" class="mt-2 text-xs font-semibold text-[#2a688f] dark:text-[#42b9eb]">
                  {{ formatSupplementalSheetSummary(ociComboResult?.summary) }}
                </p>
              </div>
              <div class="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  @click="openOciExportModal"
                  class="inline-flex items-center justify-center gap-2 rounded-xl border border-[#13335a]/15 bg-[#13335a] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#0f2a49] dark:border-[#42b9eb]/20 dark:bg-[#13335a] dark:text-[#eceded]"
                >
                  <Files class="h-4 w-4" />
                  <span>Central de exportação</span>
                </button>
                <span class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-600 dark:border-gray-700 dark:bg-gray-900/50 dark:text-gray-300">
                  Modo atual: {{ getOciExportModeLabel(ociExportMode) }}
                </span>
              </div>
            </div>

            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-12">
              <div
                v-for="card in ociComboOverviewCards"
                :key="card.label"
                class="xl:col-span-3"
              >
                <OciStatCard v-bind="card" />
              </div>
            </div>

            <div class="mt-3">
              <article
                v-if="ociComboInputFilesForDisplay.length"
                class="rounded-2xl border border-slate-200 bg-slate-50 p-3.5 dark:border-gray-700 dark:bg-gray-900/40"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">
                      {{ ociComboInputFilesForDisplay.length > 1 ? 'Arquivos usados na análise' : 'Arquivo usado na análise' }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                      Unidade e CNES identificados para cada BPA enviado
                    </p>
                  </div>
                  <span class="rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-800 dark:text-[#42b9eb]">
                    {{ ociComboInputFilesForDisplay.length }} arquivo(s)
                  </span>
                </div>
                <div class="mt-3 space-y-2">
                  <div
                    v-for="fileInfo in ociComboInputFilesForDisplay"
                    :key="`oci-current-bpa-${fileInfo.file_name}`"
                    class="rounded-xl border border-slate-200 bg-white px-3 py-2.5 dark:border-gray-700 dark:bg-gray-800"
                  >
                    <div class="flex flex-wrap items-center justify-between gap-2">
                      <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ fileInfo.file_name }}</p>
                      <span class="rounded-full bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">
                        {{ fileInfo.detected_format || 'BPA' }}
                      </span>
                    </div>
                    <p class="mt-2 text-xs text-gray-600 dark:text-gray-300">
                      {{ formatOciCurrentInputFileMeta(fileInfo) }}
                    </p>
                  </div>
                </div>
              </article>
            </div>
          </div>
        </section>

        <section
          v-if="activeSubtab === 'history' && userStore.hasModuleItemAccess('integra_oci', 'historico')"
          class="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800"
        >
          <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Histórico de análises BPA</h2>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                Acompanhe as validações de combos já realizadas, com a unidade identificada, a quantidade de ocorrências formadas e o desempenho por período.
              </p>
            </div>
            <div class="flex flex-wrap items-center gap-3">
              <!-- Filtro de tipo de exportação -->
              <div class="inline-flex items-center gap-2 rounded-xl border border-[#13335a]/20 bg-[#eceded] px-3 py-2 text-xs font-semibold text-[#13335a] dark:border-gray-600 dark:bg-gray-800 dark:text-[#42b9eb]">
                <span>Filtro export:</span>
                <select
                  v-model="ociExportMode"
                  class="rounded-lg border border-[#13335a]/30 bg-white px-2 py-1 text-xs font-semibold text-[#13335a] outline-none focus:border-[#13335a] focus:ring-2 focus:ring-[#13335a]/20 dark:border-gray-600 dark:bg-gray-800 dark:text-[#42b9eb]"
                >
                  <option value="all">Todos</option>
                  <option value="validated">Somente validados</option>
                  <option value="missing_procedure">Somente falta de procedimento</option>
                  <option value="invalid_cid">Somente CID incompatível</option>
                  <option value="invalid_auth">Somente autorização inválida</option>
                </select>
              </div>
              <button
                type="button"
                @click="showOciComboCharts = !showOciComboCharts"
                class="inline-flex items-center rounded-xl border border-[#13335a]/20 bg-[#eceded] px-4 py-2 text-sm font-semibold text-[#13335a] transition hover:bg-[#dfe3e3] dark:border-gray-600 dark:bg-gray-700 dark:text-[#42b9eb] dark:hover:bg-gray-600"
              >
                {{ showOciComboCharts ? 'Ocultar gráficos' : 'Gráficos' }}
              </button>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-200" for="oci-history-period">Período</label>
              <select
                id="oci-history-period"
                v-model="ociComboHistoryPeriod"
                @change="fetchOciComboHistory"
                class="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm focus:border-[#13335a] focus:outline-none dark:border-gray-600 dark:bg-gray-900 dark:text-gray-200"
              >
                <option value="7d">7 dias</option>
                <option value="30d">30 dias</option>
                <option value="90d">90 dias</option>
                <option value="180d">180 dias</option>
                <option value="365d">365 dias</option>
                <option value="all">Todo o histórico</option>
              </select>
            </div>
          </div>

          <div v-if="isFetchingOciComboHistory" class="flex h-72 items-center justify-center">
            <svg class="h-8 w-8 animate-spin text-[#13335a]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>

          <div v-else class="mt-6 space-y-6">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
              <article v-for="card in ociComboHistoryCards" :key="card.label" class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/40">
                <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">{{ card.label }}</p>
                <p class="mt-2 text-2xl font-bold text-[#13335a] dark:text-[#42b9eb]">{{ card.value }}</p>
                <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">{{ card.helper }}</p>
              </article>
            </div>

            <div v-if="showOciComboCharts" class="rounded-xl border border-slate-200 p-4 dark:border-gray-700">
              <div class="h-80">
                <Bar v-if="ociComboHistoryUnitChartData" :data="ociComboHistoryUnitChartData" :options="ociComboHistoryUnitChartOptions" />
                <p v-else class="flex h-full items-center justify-center text-sm text-gray-500 dark:text-gray-400">Sem dados suficientes para o gráfico de validações por unidade neste período.</p>
              </div>
            </div>

            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-[#eceded] dark:bg-gray-700">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Data</th>
                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Unidade</th>
                    <th class="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Formados</th>
                    <th class="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Não formados</th>
                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Motivo</th>
                    <th class="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Pacientes</th>
                    <th class="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Avaliados</th>
                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Competência</th>
                    <th class="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Ações</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-800">
                  <tr v-if="!ociComboHistoryData.length">
                    <td colspan="9" class="px-4 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
                      Nenhuma validação de combos registrada para o período selecionado.
                    </td>
                  </tr>
                  <tr v-for="item in ociComboHistoryData" :key="`oci-history-${item.id}`">
                    <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-900 dark:text-gray-200">{{ formatDateTime(item.created_at) }}</td>
                    <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-200">
                      <p class="font-semibold">{{ item.unit_name || 'Unidade não identificada' }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">CNES {{ item.unit_cnes || '-' }}</p>
              <p v-if="item.supplemental_sheet_used" class="text-xs font-semibold text-[#2a688f] dark:text-[#42b9eb]">
                {{ item.supplemental_sheet_file_count > 1 ? `${item.supplemental_sheet_file_count} planilhas complementares` : 'Planilha complementar' }}
                      </p>
                    </td>
                    <td class="whitespace-nowrap px-4 py-3 text-center text-sm font-semibold text-[#13335a] dark:text-[#eceded]">{{ item.combo_occurrences }}</td>
                    <td class="whitespace-nowrap px-4 py-3 text-center text-sm font-semibold text-gray-700 dark:text-gray-300">{{ item.invalid_cid_combo_occurrences || 0 }}</td>
                    <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-200">{{ item.non_formed_reason || '-' }}</td>
                    <td class="whitespace-nowrap px-4 py-3 text-center text-sm text-gray-900 dark:text-gray-200">{{ item.patients_with_combos }}</td>
                    <td class="whitespace-nowrap px-4 py-3 text-center text-sm text-gray-900 dark:text-gray-200">{{ item.total_patients_analyzed }}</td>
                    <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-200">{{ formatCompetencias(item.competencias) }}</td>
                    <td class="whitespace-nowrap px-4 py-3 text-center text-sm">
                      <div class="flex items-center justify-center">
                        <button
                          type="button"
                          @click="selectedOciHistoryItem = item; showOciHistoryDownloadModal = true"
                          :disabled="isExportingDetailedHistoryPdf(item.id) || isExportingSummaryHistoryPdf(item.id) || isExportingHistoryCsv(item.id)"
                          class="inline-flex items-center justify-center gap-1.5 rounded-lg border border-[#13335a]/20 bg-[#13335a] px-3 py-2 text-xs font-semibold text-white transition hover:bg-[#1a4070] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-[#42b9eb] dark:text-gray-900 dark:hover:bg-[#2da0cc]"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                          {{ (isExportingDetailedHistoryPdf(item.id) || isExportingSummaryHistoryPdf(item.id) || isExportingHistoryCsv(item.id)) ? 'Gerando...' : 'Baixar' }}
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section v-if="activeSubtab === 'main' && ociComboResult" class="mt-6 space-y-6">
          <div class="rounded-xl border border-slate-200 bg-white px-4 pt-2 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <OciTabNav v-model="ociResultDetailTab" :tabs="ociResultTabs" />
          </div>

          <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div class="flex-1">
                <label for="oci-patient-search" class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Pesquisa nos pacientes
                </label>
                <input
                  id="oci-patient-search"
                  v-model="ociPatientSearchQuery"
                  @input="resetOciResultPagination"
                  type="text"
                  :placeholder="ociPatientSearchPlaceholder"
                  class="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-gray-700 shadow-sm outline-none transition focus:border-[#13335a] focus:ring-2 focus:ring-[#13335a]/20 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-200"
                />
              </div>
              <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-gray-700 dark:bg-gray-900/40">
                <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Resultado da busca</p>
                <p class="mt-1 font-semibold text-[#13335a] dark:text-[#42b9eb]">
                  {{ ociActivePatientSearchCount }} de {{ ociActivePatientTotalCount }} paciente(s)
                </p>
              </div>
            </div>
          </div>

          <article class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Resumo dos combos formados</h2>
                <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                  Cada linha representa uma regra validada e quantos pacientes tiveram todos os procedimentos obrigatórios encontrados nas bases importadas.
                </p>
              </div>
              <span class="rounded-md bg-[#eceded] px-3 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">
                {{ ociComboResult.combo_summary?.length || 0 }} combo(s)
              </span>
            </div>

            <div v-if="ociComboResult.summary?.notes?.length" class="mt-4 rounded-xl border border-[#13335a]/10 bg-[#eceded] px-4 py-4 text-sm text-[#13335a] dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-200">
              <p class="font-semibold">Observações das regras</p>
              <ul class="mt-2 list-disc space-y-1 pl-5">
                <li v-for="note in (ociComboResult.summary?.notes || [])" :key="note">{{ note }}</li>
              </ul>
            </div>

            <div class="mt-4 overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead class="bg-[#eceded] dark:bg-gray-700">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Combo OCI</th>
                    <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Descrição</th>
                    <th class="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-[#13335a] dark:text-gray-200">Combos</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-800">
                  <tr v-for="combo in (ociComboResult.combo_summary || [])" :key="combo.combo_code">
                    <td class="whitespace-nowrap px-4 py-3 text-sm font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ combo.combo_code }}</td>
                    <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-200">{{ combo.combo_name }}</td>
                    <td class="whitespace-nowrap px-4 py-3 text-center text-sm font-semibold text-gray-900 dark:text-white">{{ combo.patients_count }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>

          <article
            v-if="ociResultDetailTab === 'missing_procedure'"
            ref="ociMissingProcedureSectionRef"
            class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Pendências por falta de procedimento</h2>
                <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                  Esta lista mostra os pacientes que já têm parte da regra atendida, mas ainda não fecharam o combo porque faltam procedimentos obrigatórios.
                </p>
              </div>
              <span class="rounded-md bg-[#eceded] px-3 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">
                {{ ociComboDecisionSummary.missingProcedureCombos }} ocorrência(s) pendente(s)
              </span>
            </div>

            <div
              v-if="!filteredOciAlmostComboPatients.length"
              class="mt-6 rounded-xl border border-dashed border-slate-300 bg-[#eceded] p-6 text-sm text-[#13335a] dark:border-gray-700 dark:bg-gray-900/30 dark:text-gray-300"
            >
              {{ ociPatientSearchQuery ? 'Nenhum paciente com pendência por procedimento foi encontrado para a pesquisa informada.' : 'Nenhum paciente ficou pendente apenas por falta de procedimento nesta análise.' }}
            </div>

            <div v-else class="mt-4 space-y-4">
              <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-gray-800 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-200">
                <p class="font-semibold">Resumo operacional</p>
                <p class="mt-1">
                  {{ ociComboDecisionSummary.missingProcedurePatients }} paciente(s) tiveram parte da regra encontrada, gerando {{ ociComboDecisionSummary.missingProcedureCombos }} ocorrência(s) pendente(s) por falta de procedimento obrigatório.
                </p>
              </div>

              <div class="grid gap-3 md:grid-cols-3">
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Pacientes pendentes</p>
                  <p class="mt-1 text-lg font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ filteredOciAlmostComboPatients.length }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Ocorrências pendentes</p>
                  <p class="mt-1 text-lg font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ ociComboDecisionSummary.missingProcedureCombos }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Faixa exibida</p>
                  <p class="mt-1 text-sm font-semibold text-gray-700 dark:text-gray-200">{{ ociAlmostComboRangeLabel }}</p>
                </div>
              </div>

              <div ref="ociMissingProcedureListRef" class="max-h-[62vh] space-y-4 overflow-y-auto pr-1">
                <article
                  v-for="patient in paginatedOciAlmostComboPatients"
                  :key="`oci-missing-procedure-${patient.name}-${patient.dob}`"
                  class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/40"
                >
                  <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-white">
                      <span>{{ getPatientDisplayName(patient) }} | Nasc. {{ formatPatientDob(patient.dob) }}</span>
                      <button @click.stop="togglePatientMask(patient)" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" title="Mostrar/Ocultar dados (LGPD)">
                        <svg v-if="isPatientMasked(patient)" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.478 0-8.268-2.943-9.542-7z" /></svg>
                        <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.978 9.978 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                      </button>
                    </div>
                      <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                        Base analisada: {{ describeOciPatientSources(patient) }}
                      </p>
                    </div>
                    <span class="rounded-md bg-[#13335a] px-3 py-1 text-xs font-semibold text-white dark:bg-[#2a688f]">
                      {{ patient.almost_combo_count }} combo(s) pendente(s)
                    </span>
                  </div>

                  <div class="mt-4 space-y-3">
                    <div
                      v-for="combo in patient.almost_combos"
                      :key="`${patient.name}-${combo.combo_code}-missing-procedure`"
                    class="rounded-xl border border-slate-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800"
                    >
                      <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                        <div>
                          <p class="text-sm font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ combo.combo_code }}</p>
                          <p class="text-sm text-gray-900 dark:text-white">{{ combo.combo_name }}</p>
                          <div class="mt-2 flex flex-wrap gap-2">
                            <span class="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">
                              CBO valido: {{ formatComboMatchedCbos(combo.matched_cbos, combo.required_cbo_prefixes) }}
                            </span>
                            <span class="rounded-md bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">
                              CBO esperado: {{ formatComboRequiredCbos(combo.required_cbo_prefixes) }}
                            </span>
                          </div>
                          <p v-if="combo.notes" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                            {{ combo.notes }}
                          </p>
                        </div>
                        <span class="rounded-md bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">
                          {{ combo.matched_required_count }}/{{ combo.required_count }} obrigatório(s)
                        </span>
                      </div>

                      <div class="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-3">
                        <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Procedimentos encontrados</p>
                          <ul v-if="combo.matched_required?.length" class="mt-2 space-y-2 text-sm text-gray-700 dark:text-gray-200">
                            <li v-for="item in combo.matched_required" :key="`${combo.combo_code}-matched-${item.label}`">
                              <span class="font-semibold">{{ item.label }}</span>
                              <span class="block text-xs text-gray-500 dark:text-gray-400">{{ Array.isArray(item.matched_codes) && item.matched_codes.length ? item.matched_codes.join(', ') : 'Sem código consolidado.' }}</span>
                            </li>
                          </ul>
                          <p v-else class="mt-2 text-sm text-gray-500 dark:text-gray-400">Nenhum obrigatório encontrado.</p>
                        </div>

                        <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Procedimentos faltantes</p>
                          <div v-if="combo.missing_required?.length" class="mt-3 flex flex-wrap gap-2">
                            <span
                              v-for="item in combo.missing_required"
                              :key="`${combo.combo_code}-missing-${item}`"
                              class="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200"
                            >
                              {{ item }}
                            </span>
                          </div>
                          <p v-else class="mt-2 text-sm text-gray-500 dark:text-gray-400">Nenhuma pendência de procedimento identificada.</p>
                        </div>

                        <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Procedimentos consolidados do paciente</p>
                          <p class="mt-2 text-sm text-gray-700 dark:text-gray-200">
                            {{ formatProcedureMap(patient.procedures) }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </article>
              </div>

              <div v-if="ociAlmostComboTotalPages > 1" class="flex flex-col gap-3 border-t border-slate-200 pt-4 md:flex-row md:items-center md:justify-between dark:border-gray-700">
                <div class="text-sm text-gray-600 dark:text-gray-300">
                  Exibindo {{ ociAlmostComboRangeLabel }} de {{ filteredOciAlmostComboPatients.length }} paciente(s) com pendência por procedimento.
                </div>
                <div class="flex flex-wrap items-center gap-2 text-sm">
                  <button
                    type="button"
                    @click="goToPreviousOciAlmostComboPage"
                    class="rounded-lg border px-3 py-1.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
                    style="border-color: #13335a; color: #13335a;"
                    :disabled="ociAlmostComboPage === 1"
                  >
                    Anterior
                  </button>
                  <span class="rounded-lg px-3 py-1.5 font-semibold text-white" style="background-color: #13335a;">
                    Página {{ ociAlmostComboPage }} de {{ ociAlmostComboTotalPages }}
                  </span>
                  <button
                    type="button"
                    @click="goToNextOciAlmostComboPage"
                    class="rounded-lg border px-3 py-1.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
                    style="border-color: #13335a; color: #13335a;"
                    :disabled="ociAlmostComboPage >= ociAlmostComboTotalPages"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            </div>
          </article>

          <article
            v-if="ociResultDetailTab === 'invalid_cid'"
            ref="ociInvalidCidSectionRef"
            class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Combos com CID incorreto</h2>
                <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                  Esta lista mostra quantos combos deixaram de ser formados por CID incompatível e quais pacientes fecharam os procedimentos, mas não validaram a regra final.
                </p>
              </div>
              <span class="rounded-md bg-[#eceded] px-3 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">
                {{ ociComboDecisionSummary.invalidCidCombos }} combo(s) não validados
              </span>
            </div>

            <div
              v-if="!filteredOciInvalidCidPatients.length"
              class="mt-6 rounded-xl border border-dashed border-slate-300 bg-[#eceded] p-6 text-sm text-[#13335a] dark:border-gray-700 dark:bg-gray-900/30 dark:text-gray-300"
            >
              {{ ociPatientSearchQuery ? 'Nenhum paciente com CID incompatível foi encontrado para a pesquisa informada.' : 'Nenhum paciente fechou os procedimentos de combo com CID incompatível nesta análise.' }}
            </div>

            <div v-else class="mt-4 space-y-4">
              <div class="rounded-xl border border-[#13335a]/10 bg-[#eceded] px-4 py-4 text-sm text-[#13335a] dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-200">
                <p class="font-semibold">Resumo da inconsistência</p>
                <p class="mt-1">
                  {{ ociComboDecisionSummary.invalidCidPatients }} paciente(s) tiveram procedimento(s) suficientes para combo, gerando {{ ociComboDecisionSummary.invalidCidCombos }} ocorrência(s) de combo não formado por CID incompatível com a regra aplicada.
                </p>
              </div>

              <div class="grid gap-3 md:grid-cols-3">
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Pacientes com CID incompatível</p>
                  <p class="mt-1 text-lg font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ filteredOciInvalidCidPatients.length }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Ocorrências não validadas</p>
                  <p class="mt-1 text-lg font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ ociComboDecisionSummary.invalidCidCombos }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Faixa exibida</p>
                  <p class="mt-1 text-sm font-semibold text-gray-700 dark:text-gray-200">{{ ociInvalidCidRangeLabel }}</p>
                </div>
              </div>

              <div ref="ociInvalidCidListRef" class="max-h-[62vh] space-y-4 overflow-y-auto pr-1">
                <article
                  v-for="patient in paginatedOciInvalidCidPatients"
                  :key="`oci-invalid-cid-${patient.name}-${patient.dob}`"
                  class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/40"
                >
                <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-white">
                      <span>{{ getPatientDisplayName(patient) }} | Nasc. {{ formatPatientDob(patient.dob) }}</span>
                      <button @click.stop="togglePatientMask(patient)" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" title="Mostrar/Ocultar dados (LGPD)">
                        <svg v-if="isPatientMasked(patient)" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.478 0-8.268-2.943-9.542-7z" /></svg>
                        <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.978 9.978 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                      </button>
                    </div>
                    <p v-if="formatMaskedPatientIdentifiers(patient)" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      {{ formatMaskedPatientIdentifiers(patient) }}
                    </p>
                    <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                      Base analisada: {{ describeOciPatientSources(patient) }} | {{ getOciCidSourceLabel(patient.cid_sources) }}: {{ patient.cids?.length ? patient.cids.join(', ') : getOciCidMissingLabel(patient.cid_sources) }}
                    </p>
                    <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      Encontrado em: {{ describeOciPatientOriginSummary(patient) }}
                    </p>
                  </div>
                  <span class="rounded-md bg-[#2a688f] px-3 py-1 text-xs font-semibold text-white">
                    {{ patient.invalid_cid_combo_count }} combo(s) com CID incorreto
                  </span>
                </div>

                <div v-if="getOciPatientBpaFiles(patient).length || getOciPatientSupplementalFiles(patient).length" class="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-2">
                  <div v-if="getOciPatientBpaFiles(patient).length" class="rounded-xl border border-slate-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-800/70">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">BPAs em que o paciente foi encontrado</p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <span
                        v-for="fileName in getOciPatientBpaFiles(patient)"
                        :key="`invalid-bpa-${patient.name}-${fileName}`"
                        class="rounded-md bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]"
                      >
                        {{ fileName }}
                      </span>
                    </div>
                  </div>
                  <div v-if="getOciPatientSupplementalFiles(patient).length" class="rounded-xl border border-slate-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-800/70">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Planilha complementar em que o paciente foi encontrado</p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <span
                        v-for="fileName in getOciPatientSupplementalFiles(patient)"
                        :key="`invalid-sheet-${patient.name}-${fileName}`"
                        class="rounded-md bg-[#2a688f] px-2.5 py-1 text-xs font-semibold text-white"
                      >
                        {{ fileName }}
                      </span>
                    </div>
                  </div>
                </div>

                <div class="mt-4 space-y-3">
                  <div
                    v-for="combo in patient.invalid_cid_combos"
                    :key="`${patient.name}-${combo.combo_code}-invalid-cid`"
                    class="rounded-xl border border-[#13335a]/10 bg-white p-4 dark:border-gray-700 dark:bg-gray-800/70"
                  >
                    <div>
                      <p class="text-sm font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ combo.combo_code }}</p>
                      <p class="text-sm text-gray-900 dark:text-white">{{ combo.combo_name }}</p>
                      <div class="mt-2 flex flex-wrap gap-2">
                        <span class="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">
                          CBO valido: {{ formatComboMatchedCbos(combo.matched_cbos, combo.required_cbo_prefixes) }}
                        </span>
                        <span class="rounded-md bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">
                          CBO esperado: {{ formatComboRequiredCbos(combo.required_cbo_prefixes) }}
                        </span>
                      </div>
                      <p v-if="combo.context_source_combo_code || combo.context_source_combo_name" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        Regra CID vinculada a {{ combo.context_source_combo_code || combo.combo_code }}{{ combo.context_source_combo_name ? ` - ${combo.context_source_combo_name}` : '' }}
                      </p>
                    </div>

                    <div class="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-3">
                      <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Procedimentos localizados</p>
                        <div v-if="combo.matched_procedure_details?.length || procedureEntries(combo.matched_procedures).length" class="mt-3 flex flex-wrap gap-2">
                          <span
                            v-for="item in procedureDisplayEntries(combo.matched_procedure_details, combo.matched_procedures)"
                            :key="`${combo.combo_code}-invalid-proc-${item.code}`"
                            class="rounded-md bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]"
                          >
                            {{ formatProcedureDisplay(item) }}
                          </span>
                        </div>
                        <p v-else class="mt-2 text-sm text-gray-500 dark:text-gray-400">Sem procedimentos consolidados para exibir.</p>
                      </div>

                      <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">{{ getOciCidSourceLabel(combo.patient_cid_sources) }}</p>
                        <div v-if="combo.patient_cids?.length" class="mt-3 flex flex-wrap gap-2">
                          <span
                            v-for="cid in combo.patient_cids"
                            :key="`${combo.combo_code}-patient-cid-${cid}`"
                            class="rounded-full bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]"
                          >
                            {{ cid }}
                          </span>
                        </div>
                        <p v-else class="mt-2 text-sm text-gray-500 dark:text-gray-400">{{ getOciCidMissingLabel(combo.patient_cid_sources) }}</p>
                      </div>

                      <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">CID esperado pela regra</p>
                        <div v-if="combo.required_cid_prefixes?.length" class="mt-3 flex flex-wrap gap-2">
                          <span
                            v-for="cidPrefix in combo.required_cid_prefixes"
                            :key="`${combo.combo_code}-required-cid-${cidPrefix}`"
                            class="rounded-md bg-[#2a688f] px-2.5 py-1 text-xs font-semibold text-white"
                          >
                            {{ cidPrefix }}
                          </span>
                        </div>
                        <p v-else class="mt-2 text-sm text-gray-500 dark:text-gray-400">Esta regra não trouxe prefixos de CID esperados.</p>
                      </div>
                    </div>
                  </div>
                </div>
                </article>
              </div>

              <div v-if="ociInvalidCidTotalPages > 1" class="flex flex-col gap-3 border-t border-slate-200 pt-4 md:flex-row md:items-center md:justify-between dark:border-gray-700">
                <div class="text-sm text-gray-600 dark:text-gray-300">
                  Exibindo {{ ociInvalidCidRangeLabel }} de {{ filteredOciInvalidCidPatients.length }} paciente(s) com CID incompatível.
                </div>
                <div class="flex flex-wrap items-center gap-2 text-sm">
                  <button
                    type="button"
                    @click="goToPreviousOciInvalidCidPage"
                    class="rounded-lg border px-3 py-1.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
                    style="border-color: #13335a; color: #13335a;"
                    :disabled="ociInvalidCidPage === 1"
                  >
                    Anterior
                  </button>
                  <span class="rounded-lg px-3 py-1.5 font-semibold text-white" style="background-color: #13335a;">
                    Página {{ ociInvalidCidPage }} de {{ ociInvalidCidTotalPages }}
                  </span>
                  <button
                    type="button"
                    @click="goToNextOciInvalidCidPage"
                    class="rounded-lg border px-3 py-1.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
                    style="border-color: #13335a; color: #13335a;"
                    :disabled="ociInvalidCidPage >= ociInvalidCidTotalPages"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            </div>
          </article>

          <article
            v-if="ociResultDetailTab === 'invalid_auth'"
            ref="ociInvalidAuthSectionRef"
            class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Combos com autorização inválida</h2>
                <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                  Esta lista mostra quantos combos deixaram de ser formados por número de autorização inválido (exatamente 9 dígitos e não iniciando com "0").
                </p>
              </div>
              <span class="rounded-md bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">
                {{ ociComboDecisionSummary.invalidAuthCombos }} combo(s) bloqueado(s)
              </span>
            </div>

            <div
              v-if="!filteredOciInvalidAuthPatients.length"
              class="mt-6 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-gray-600 dark:border-gray-600 dark:bg-gray-900/30 dark:text-gray-300"
            >
              {{ ociPatientSearchQuery ? 'Nenhum paciente com autorização inválida foi encontrado para a pesquisa informada.' : 'Nenhum paciente fechou os procedimentos de combo com número de autorização inválido nesta análise.' }}
            </div>

            <div v-else class="mt-4 space-y-4">
              <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-gray-800 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-200">
                <p class="font-semibold">Resumo da inconsistência</p>
                <p class="mt-1">
                  {{ ociComboDecisionSummary.invalidAuthPatients }} paciente(s) tiveram procedimento(s) suficientes para combo, gerando {{ ociComboDecisionSummary.invalidAuthCombos }} ocorrência(s) de combo bloqueado por número de autorização inválido.
                </p>
              </div>

              <div class="grid gap-3 md:grid-cols-3">
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Pacientes com autorização inválida</p>
                  <p class="mt-1 text-lg font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ filteredOciInvalidAuthPatients.length }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Ocorrências bloqueadas</p>
                  <p class="mt-1 text-lg font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ ociComboDecisionSummary.invalidAuthCombos }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Faixa exibida</p>
                  <p class="mt-1 text-sm font-semibold text-gray-700 dark:text-gray-200">{{ ociInvalidAuthRangeLabel }}</p>
                </div>
              </div>

              <div ref="ociInvalidAuthListRef" class="max-h-[62vh] space-y-4 overflow-y-auto pr-1">
                <article
                  v-for="patient in paginatedOciInvalidAuthPatients"
                  :key="`oci-invalid-auth-${patient.name}-${patient.dob}`"
                  class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/40"
                >
                  <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                    <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-white">
                      <span>{{ getPatientDisplayName(patient) }} | Nasc. {{ formatPatientDob(patient.dob) }}</span>
                      <button @click.stop="togglePatientMask(patient)" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" title="Mostrar/Ocultar dados (LGPD)">
                        <svg v-if="isPatientMasked(patient)" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.478 0-8.268-2.943-9.542-7z" /></svg>
                        <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.978 9.978 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                      </button>
                    </div>
                      <p v-if="formatMaskedPatientIdentifiers(patient)" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        {{ formatMaskedPatientIdentifiers(patient) }}
                      </p>
                      <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                        Base analisada: {{ describeOciPatientSources(patient) }} | CIDs identificados: {{ patient.cids?.length ? patient.cids.join(', ') : 'Nenhum' }}
                      </p>
                      <div class="mt-2 flex flex-wrap items-center gap-1.5 text-xs">
                        <span class="text-gray-500 dark:text-gray-400 font-medium">Autorizações:</span>
                        <template v-if="getValidAuths(patient.autorizacoes).length">
                          <span
                            v-for="auth in getValidAuths(patient.autorizacoes)"
                            :key="auth"
                            :class="ociClasses.tagMono"
                            title="Autorização válida"
                          >
                            {{ auth }}
                          </span>
                        </template>
                        <span v-else class="text-gray-400 italic">Nenhuma autorização válida informada</span>
                      </div>
                      <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        Encontrado em: {{ describeOciPatientOriginSummary(patient) }}
                      </p>
                    </div>
                    <span class="rounded-md bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">
                      {{ patient.invalid_auth_combo_count }} combo(s) bloqueado(s)
                    </span>
                  </div>

                  <div v-if="getOciPatientBpaFiles(patient).length || getOciPatientSupplementalFiles(patient).length" class="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-2">
                    <div v-if="getOciPatientBpaFiles(patient).length" class="rounded-xl border border-slate-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-800/70">
                      <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">BPAs em que o paciente foi encontrado</p>
                      <div class="mt-3 flex flex-wrap gap-2">
                        <span
                          v-for="fileName in getOciPatientBpaFiles(patient)"
                          :key="`invalid-auth-bpa-${patient.name}-${fileName}`"
                          class="rounded-md bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]"
                        >
                          {{ fileName }}
                        </span>
                      </div>
                    </div>
                    <div v-if="getOciPatientSupplementalFiles(patient).length" class="rounded-xl border border-slate-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-800/70">
                      <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Planilha complementar em que o paciente foi encontrado</p>
                      <div class="mt-3 flex flex-wrap gap-2">
                        <span
                          v-for="fileName in getOciPatientSupplementalFiles(patient)"
                          :key="`invalid-auth-sheet-${patient.name}-${fileName}`"
                          class="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200"
                        >
                          {{ fileName }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div class="mt-4 space-y-3">
                    <div
                      v-for="combo in patient.invalid_auth_combos"
                      :key="`${patient.name}-${combo.combo_code}-invalid-auth`"
                      class="rounded-xl border border-slate-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800/70"
                    >
                      <div>
                        <p class="text-sm font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ combo.combo_code }}</p>
                        <p class="text-sm text-gray-900 dark:text-white">{{ combo.combo_name }}</p>
                        <div class="mt-2 flex flex-wrap gap-2">
                          <span class="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">
                            CBO valido: {{ formatComboMatchedCbos(combo.matched_cbos, combo.required_cbo_prefixes) }}
                          </span>
                          <span class="rounded-md bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">
                            CBO esperado: {{ formatComboRequiredCbos(combo.required_cbo_prefixes) }}
                          </span>
                        </div>
                        <p v-if="combo.context_source_combo_code || combo.context_source_combo_name" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                          Regra vinculada a {{ combo.context_source_combo_code || combo.combo_code }}{{ combo.context_source_combo_name ? ` - ${combo.context_source_combo_name}` : '' }}
                        </p>
                      </div>

                      <div class="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-2">
                        <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Procedimentos localizados</p>
                          <div v-if="combo.matched_procedure_details?.length || procedureEntries(combo.matched_procedures).length" class="mt-3 flex flex-wrap gap-2">
                            <span
                              v-for="item in procedureDisplayEntries(combo.matched_procedure_details, combo.matched_procedures)"
                              :key="`${combo.combo_code}-invalid-auth-proc-${item.code}`"
                              class="rounded-md bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]"
                            >
                              {{ formatProcedureDisplay(item) }}
                            </span>
                          </div>
                          <p v-else class="mt-2 text-sm text-gray-500 dark:text-gray-400">Sem procedimentos consolidados para exibir.</p>
                        </div>

                        <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">CIDs validados no combo</p>
                          <div v-if="combo.matched_cids?.length" class="mt-3 flex flex-wrap gap-2">
                            <span
                              v-for="cid in combo.matched_cids"
                              :key="`${combo.combo_code}-matched-cid-${cid}`"
                              class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200"
                            >
                              {{ cid }}
                            </span>
                          </div>
                          <p v-else class="mt-2 text-sm text-gray-500 dark:text-gray-400">Nenhum CID compatível associado.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </article>
              </div>

              <div v-if="ociInvalidAuthTotalPages > 1" class="flex flex-col gap-3 border-t border-slate-200 pt-4 md:flex-row md:items-center md:justify-between dark:border-gray-700">
                <div class="text-sm text-gray-600 dark:text-gray-300">
                  Exibindo {{ ociInvalidAuthRangeLabel }} de {{ filteredOciInvalidAuthPatients.length }} paciente(s) com autorização inválida.
                </div>
                <div class="flex flex-wrap items-center gap-2 text-sm">
                  <button
                    type="button"
                    @click="goToPreviousOciInvalidAuthPage"
                    class="rounded-lg border px-3 py-1.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
                    style="border-color: #13335a; color: #13335a;"
                    :disabled="ociInvalidAuthPage === 1"
                  >
                    Anterior
                  </button>
                  <span class="rounded-lg px-3 py-1.5 font-semibold text-white" style="background-color: #13335a;">
                    Página {{ ociInvalidAuthPage }} de {{ ociInvalidAuthTotalPages }}
                  </span>
                  <button
                    type="button"
                    @click="goToNextOciInvalidAuthPage"
                    class="rounded-lg border px-3 py-1.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
                    style="border-color: #13335a; color: #13335a;"
                    :disabled="ociInvalidAuthPage >= ociInvalidAuthTotalPages"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            </div>
          </article>

          <article
            v-if="ociResultDetailTab === 'formed'"
            ref="ociComboPatientsSectionRef"
            class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800"
          >
            <div class="flex flex-col gap-4">
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Pacientes que formam combos</h2>
                <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                  A lista mostra quais combos cada paciente formou e os procedimentos localizados para justificar a classificação.
                </p>
              </div>
            </div>

            <div v-if="!filteredOciComboPatients.length" class="mt-6 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-gray-600 dark:border-gray-700 dark:bg-gray-900/30 dark:text-gray-300">
              {{ ociPatientSearchQuery ? 'Nenhum paciente com combo foi encontrado para a pesquisa informada.' : 'Nenhum paciente formou combo com os arquivos informados.' }}
            </div>

            <div v-else class="mt-4 space-y-4">
              <div class="grid gap-3 md:grid-cols-3">
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Pacientes com combo</p>
                  <p class="mt-1 text-lg font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ filteredOciComboPatients.length }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Ocorrências formadas</p>
                  <p class="mt-1 text-lg font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ ociComboDecisionSummary.formedCombos }}</p>
                </div>
                <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-900/40">
                  <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Faixa exibida</p>
                  <p class="mt-1 text-sm font-semibold text-gray-700 dark:text-gray-200">{{ ociComboPatientRangeLabel }}</p>
                </div>
              </div>
              <div ref="ociComboPatientsListRef" class="max-h-[62vh] space-y-4 overflow-y-auto pr-1">
                <article
                  v-for="patient in paginatedOciComboPatients"
                  :key="`oci-patient-${patient.name}-${patient.dob}`"
                  class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/40"
                >
                <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <div class="flex items-center gap-2 text-base font-semibold text-gray-900 dark:text-white">
                      <span>{{ getPatientDisplayName(patient) }} | Nasc. {{ formatPatientDob(patient.dob) }}</span>
                      <button @click.stop="togglePatientMask(patient)" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" title="Mostrar/Ocultar dados (LGPD)">
                        <svg v-if="isPatientMasked(patient)" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.478 0-8.268-2.943-9.542-7z" /></svg>
                        <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.978 9.978 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                      </button>
                    </div>
                    <p v-if="formatMaskedPatientIdentifiers(patient)" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      {{ formatMaskedPatientIdentifiers(patient) }}
                    </p>
                    <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                      Base analisada: {{ describeOciPatientSources(patient) }}
                    </p>
                    <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      Encontrado em: {{ describeOciPatientOriginSummary(patient) }}
                    </p>
                    <div class="mt-2 flex flex-wrap items-center gap-1.5 text-xs">
                      <span class="text-gray-500 dark:text-gray-400 font-medium">Autorização:</span>
                      <template v-if="getValidAuths(patient.autorizacoes).length">
                        <span
                          v-for="auth in getValidAuths(patient.autorizacoes)"
                          :key="auth"
                          :class="ociClasses.tagMono"
                          title="Autorização válida"
                        >
                          {{ auth }}
                        </span>
                      </template>
                      <span v-else class="text-gray-400 italic">Nenhuma</span>
                    </div>
                  </div>
                  <span class="rounded-md bg-[#13335a] px-3 py-1 text-xs font-semibold text-[#eceded]">
                    {{ patient.formed_combo_count }} combo(s)
                  </span>
                </div>

                <div v-if="getOciPatientBpaFiles(patient).length || getOciPatientSupplementalFiles(patient).length" class="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-2">
                  <div v-if="getOciPatientBpaFiles(patient).length" class="rounded-xl border border-slate-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-800/70">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">BPAs em que o paciente foi encontrado</p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <span
                        v-for="fileName in getOciPatientBpaFiles(patient)"
                        :key="`formed-bpa-${patient.name}-${fileName}`"
                        class="rounded-md bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]"
                      >
                        {{ fileName }}
                      </span>
                    </div>
                  </div>
                  <div v-if="getOciPatientSupplementalFiles(patient).length" class="rounded-xl border border-slate-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-800/70">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Planilha complementar em que o paciente foi encontrado</p>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <span
                        v-for="fileName in getOciPatientSupplementalFiles(patient)"
                        :key="`formed-sheet-${patient.name}-${fileName}`"
                        class="rounded-md bg-[#2a688f] px-2.5 py-1 text-xs font-semibold text-white"
                      >
                        {{ fileName }}
                      </span>
                    </div>
                  </div>
                </div>

                <div class="mt-4 space-y-3">
                  <div
                    v-for="combo in patient.formed_combos"
                    :key="`${patient.name}-${combo.combo_code}`"
                    class="rounded-xl border border-[#13335a]/10 bg-white p-4 dark:border-gray-700 dark:bg-gray-800/70"
                  >
                    <div>
                      <p class="text-sm font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ combo.combo_code }}</p>
                      <p class="text-sm text-gray-900 dark:text-white">{{ combo.combo_name }}</p>
                      <div class="mt-2 flex flex-wrap gap-2">
                        <span class="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-gray-700 dark:text-gray-200">
                          CBO valido: {{ formatComboMatchedCbos(combo.matched_cbos, combo.required_cbo_prefixes) }}
                        </span>
                        <span class="rounded-md bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]">
                          CBO esperado: {{ formatComboRequiredCbos(combo.required_cbo_prefixes) }}
                        </span>
                      </div>
                    </div>

                    <div class="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-3">
                      <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Obrigatórios localizados</p>
                        <ul class="mt-2 space-y-2 text-sm text-gray-700 dark:text-gray-200">
                          <li v-for="item in combo.matched_required" :key="`${combo.combo_code}-${item.label}`">
                            <span class="font-semibold">{{ item.label }}</span>
                            <span class="block text-xs text-gray-500 dark:text-gray-400">{{ formatProcedureMap(item.matched_codes) }}</span>
                          </li>
                        </ul>
                      </div>

                      <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Opcionais encontrados</p>
                        <ul v-if="combo.matched_optional?.length" class="mt-2 space-y-2 text-sm text-gray-700 dark:text-gray-200">
                          <li v-for="item in combo.matched_optional" :key="`${combo.combo_code}-opt-${item.label}`">
                            <span class="font-semibold">{{ item.label }}</span>
                            <span class="block text-xs text-gray-500 dark:text-gray-400">{{ formatProcedureMap(item.matched_codes) }}</span>
                          </li>
                        </ul>
                        <p v-else class="mt-2 text-sm text-gray-500 dark:text-gray-400">Nenhum opcional localizado para este combo.</p>
                      </div>

                      <div class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-900/40">
                        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Procedimentos consolidados do combo</p>
                        <div v-if="combo.matched_procedure_details?.length || procedureEntries(combo.matched_procedures).length" class="mt-3 flex flex-wrap gap-2">
                          <span
                            v-for="item in procedureDisplayEntries(combo.matched_procedure_details, combo.matched_procedures)"
                            :key="`${combo.combo_code}-${item.code}`"
                            class="rounded-md bg-[#eceded] px-2.5 py-1 text-xs font-semibold text-[#13335a] dark:bg-gray-700 dark:text-[#42b9eb]"
                          >
                            {{ formatProcedureDisplay(item) }}
                          </span>
                        </div>
                        <p v-else class="mt-2 text-sm text-gray-500 dark:text-gray-400">Sem procedimentos consolidados para exibir.</p>
                      </div>
                    </div>
                  </div>
                </div>
                </article>
              </div>

              <div v-if="filteredOciComboPatients.length && ociComboPatientTotalPages > 1" class="flex flex-col gap-3 border-t border-slate-200 pt-4 md:flex-row md:items-center md:justify-between dark:border-gray-700">
                <div class="text-sm text-gray-600 dark:text-gray-300">
                  Exibindo {{ ociComboPatientRangeLabel }} de {{ filteredOciComboPatients.length }} paciente(s) com combo.
                </div>
                <div class="flex flex-wrap items-center gap-2 text-sm">
                  <button
                    type="button"
                    @click="goToPreviousOciComboPatientPage"
                    class="rounded-lg border px-3 py-1.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
                    style="border-color: #13335a; color: #13335a;"
                    :disabled="ociComboPatientPage === 1"
                  >
                    Anterior
                  </button>
                  <span class="rounded-lg px-3 py-1.5 font-semibold text-white" style="background-color: #13335a;">
                    Página {{ ociComboPatientPage }} de {{ ociComboPatientTotalPages }}
                  </span>
                  <button
                    type="button"
                    @click="goToNextOciComboPatientPage"
                    class="rounded-lg border px-3 py-1.5 font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
                    style="border-color: #13335a; color: #13335a;"
                    :disabled="ociComboPatientPage >= ociComboPatientTotalPages"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            </div>
          </article>
        </section>

              </div>

              <!-- DASHBOARD TAB -->
              <div v-else-if="activeTab === 'dashboard' && userStore.hasModuleItemAccess('integra_oci', 'dashboard')" key="dashboard" class="min-w-0">
                <section class="mt-4 space-y-4">
                  <div class="rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                    <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                      <div>
                        <p class="text-xs font-semibold uppercase tracking-wide text-[#2a688f] dark:text-[#42b9eb]">Visão Geral</p>
                        <h2 class="mt-1 text-xl font-semibold text-gray-900 dark:text-white">Dashboard Analítico - Integra OCI</h2>
                        <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                          Acompanhe os resultados consolidados de BPA Inteligente e Validação de Combos.
                        </p>
                      </div>
                      <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
                        <select
                          v-model="dashboardPeriodFilter"
                          class="rounded-lg border-gray-300 bg-gray-50 text-sm focus:border-[#2a688f] focus:ring-[#2a688f] dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                        >
                          <option value="7d">Últimos 7 dias</option>
                          <option value="30d">Últimos 30 dias</option>
                          <option value="90d">Últimos 90 dias</option>
                          <option value="180d">Últimos 180 dias</option>
                          <option value="365d">Últimos 365 dias</option>
                          <option value="all">Todo o período</option>
                          <option value="custom">Período específico</option>
                        </select>
                        <div v-if="dashboardPeriodFilter === 'custom'" class="flex items-center gap-2">
                          <input
                            type="date"
                            v-model="dashboardStartDate"
                            class="rounded-lg border-gray-300 bg-gray-50 text-sm focus:border-[#2a688f] focus:ring-[#2a688f] dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                          />
                          <span class="text-sm text-gray-500">até</span>
                          <input
                            type="date"
                            v-model="dashboardEndDate"
                            class="rounded-lg border-gray-300 bg-gray-50 text-sm focus:border-[#2a688f] focus:ring-[#2a688f] dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                          />
                          <button
                            @click="applyCustomDateFilter"
                            class="rounded-lg bg-[#13335a] px-3 py-2 text-sm font-semibold text-white hover:bg-[#2a688f] dark:bg-[#42b9eb] dark:text-[#13335a]"
                          >
                            Buscar
                          </button>
                        </div>
                        <select
                          v-model="dashboardUnitFilter"
                          class="rounded-lg border-gray-300 bg-gray-50 text-sm focus:border-[#2a688f] focus:ring-[#2a688f] dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                        >
                          <option value="">Todas as unidades</option>
                          <option v-for="unit in dashboardAvailableUnits" :key="unit.cnes" :value="unit.cnes">
                            {{ unit.name }}
                          </option>
                        </select>
                      </div>
                    </div>

                    <div class="mt-4 border-b border-gray-200 dark:border-gray-700">
                      <nav class="-mb-px flex space-x-6" aria-label="Tabs do Dashboard">
                        <button
                          @click="dashboardActiveTab = 'bpa'"
                          :class="[
                            dashboardActiveTab === 'bpa'
                              ? 'border-[#13335a] text-[#13335a] dark:border-[#42b9eb] dark:text-[#42b9eb]'
                              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:border-gray-600 dark:hover:text-gray-300',
                            'whitespace-nowrap border-b-2 py-3 px-1 text-sm font-medium transition-colors'
                          ]"
                        >
                          BPA Inteligente
                        </button>
                        <button
                          @click="dashboardActiveTab = 'combos'"
                          :class="[
                            dashboardActiveTab === 'combos'
                              ? 'border-[#13335a] text-[#13335a] dark:border-[#42b9eb] dark:text-[#42b9eb]'
                              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:border-gray-600 dark:hover:text-gray-300',
                            'whitespace-nowrap border-b-2 py-3 px-1 text-sm font-medium transition-colors'
                          ]"
                        >
                          Validação de Combos OCI
                        </button>
                      </nav>
                    </div>
                  </div>

                  <div v-if="isFetchingHistory || isFetchingOciComboHistory" class="flex h-64 flex-col items-center justify-center rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                    <RefreshCw class="h-8 w-8 animate-spin text-[#13335a] dark:text-[#42b9eb]" />
                    <p class="mt-4 text-sm font-medium text-gray-600 dark:text-gray-300">Carregando dados do dashboard...</p>
                  </div>
                  
                  <div v-else>
                    <!-- ABA BPA -->
                    <div v-if="dashboardActiveTab === 'bpa'" class="space-y-4">
                      <!-- Insights BPA -->
                      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/40">
                        <div class="flex items-start gap-3">
                          <div class="rounded-lg bg-slate-100 p-2 text-slate-600 dark:bg-gray-700 dark:text-gray-300">
                            <Lightbulb class="h-5 w-5" />
                          </div>
                          <div>
                            <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100">Insights do BPA Inteligente</h4>
                            <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                              O BPA Inteligente já atuou em <span class="font-semibold text-[#13335a] dark:text-[#eceded]">{{ dashboardFilteredBpaSummary?.total_patients_with_combos || 0 }}</span> pacientes analisados, garantindo que o cruzamento remova os registros do BPA já presentes nas APACs.
                            </p>
                          </div>
                        </div>
                      </div>

                      <div class="grid grid-cols-1 gap-4">
                        <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                          <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">OCI Removidos (Top Unidades)</h3>
                          <div class="mt-4 h-80">
                            <Bar v-if="dashboardBpaChartData" :data="dashboardBpaChartData" :options="dashboardBpaChartOptions" />
                            <div v-else class="flex h-full flex-col items-center justify-center text-gray-400">
                              <BarChart3 class="mb-2 h-8 w-8 opacity-20" />
                              <p class="text-sm">Sem dados suficientes no período</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- ABA COMBOS -->
                    <div v-else-if="dashboardActiveTab === 'combos'" class="space-y-4">
                      <!-- Insights Combos -->
                      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/40">
                        <div class="flex items-start gap-3">
                          <div class="rounded-lg bg-slate-100 p-2 text-slate-600 dark:bg-gray-700 dark:text-gray-300">
                            <Lightbulb class="h-5 w-5" />
                          </div>
                          <div>
                            <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100">Insights de Validação de Combos</h4>
                            <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                              De <span class="font-semibold text-[#13335a] dark:text-[#eceded]">{{ dashboardFilteredComboSummary?.total_patients_with_combos || 0 }}</span> pacientes analisados, formamos com sucesso <span class="font-semibold text-[#13335a] dark:text-[#eceded]">{{ dashboardFilteredComboSummary?.total_combo_occurrences || 0 }}</span> combos. A maior causa de glosa evitada foi a falta de autorização prévia (<span class="font-semibold text-[#13335a] dark:text-[#eceded]">{{ dashboardFilteredComboSummary?.total_invalid_auth_combo_occurrences || 0 }}</span> registros não formados).
                            </p>
                          </div>
                        </div>
                      </div>

                      <div class="grid grid-cols-1 gap-4 xl:grid-cols-2">
                        <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                          <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Validação de Combos</h3>
                          <div class="mt-4 h-72">
                            <Bar v-if="dashboardComboChartData" :data="dashboardComboChartData" :options="dashboardComboChartOptions" />
                            <div v-else class="flex h-full flex-col items-center justify-center text-gray-400">
                              <BarChart3 class="mb-2 h-8 w-8 opacity-20" />
                              <p class="text-sm">Sem dados suficientes no período</p>
                            </div>
                          </div>
                        </div>

                        <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                          <h3 class="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Rank: Média de Combos Inválidos por Unidade</h3>
                          <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                              <thead class="bg-gray-50 dark:bg-gray-700/50">
                                <tr>
                                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Posição</th>
                                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Unidade</th>
                                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400">Média (Não formados/Análise)</th>
                                </tr>
                              </thead>
                              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                                <tr v-for="(item, index) in dashboardComboRankData" :key="item.unit_cnes">
                                  <td class="px-3 py-2 text-sm text-gray-900 dark:text-gray-200">{{ index + 1 }}º</td>
                                  <td class="px-3 py-2 text-sm text-gray-900 dark:text-gray-200">{{ item.unit_name }}</td>
                                  <td class="px-3 py-2 text-right text-sm font-semibold text-gray-800 dark:text-gray-200">{{ item.avg_invalid }}</td>
                                </tr>
                                <tr v-if="!dashboardComboRankData.length">
                                  <td colspan="3" class="px-3 py-4 text-center text-sm text-gray-500">Sem dados no período</td>
                                </tr>
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>

                      <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                        <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Detalhamento Geral de Combos</h3>
                        <dl class="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
                          <div class="rounded-lg bg-[#eceded] p-3 dark:bg-gray-700/50">
                            <dt class="text-xs font-medium text-gray-500 dark:text-gray-400">Pacientes com combo possível</dt>
                            <dd class="mt-1 text-xl font-semibold text-[#13335a] dark:text-[#42b9eb]">{{ dashboardFilteredComboSummary?.total_patients_with_combos || 0 }}</dd>
                          </div>
                          <div class="rounded-lg bg-slate-50 p-3 dark:bg-gray-900/40">
                            <dt class="text-xs font-medium text-gray-500 dark:text-gray-400">Combos formados</dt>
                            <dd class="mt-1 text-xl font-semibold text-[#13335a] dark:text-[#eceded]">{{ dashboardFilteredComboSummary?.total_combo_occurrences || 0 }}</dd>
                          </div>
                          <div class="rounded-lg bg-slate-50 p-3 dark:bg-gray-900/40">
                            <dt class="text-xs font-medium text-gray-500 dark:text-gray-400">Não formados (CID)</dt>
                            <dd class="mt-1 text-xl font-semibold text-gray-800 dark:text-gray-200">{{ dashboardFilteredComboSummary?.total_invalid_cid_combo_occurrences || 0 }}</dd>
                          </div>
                          <div class="rounded-lg bg-slate-50 p-3 dark:bg-gray-900/40">
                            <dt class="text-xs font-medium text-gray-500 dark:text-gray-400">Não formados (Autorização)</dt>
                            <dd class="mt-1 text-xl font-semibold text-gray-800 dark:text-gray-200">{{ dashboardFilteredComboSummary?.total_invalid_auth_combo_occurrences || 0 }}</dd>
                          </div>
                        </dl>
                      </div>
                    </div>
                  </div>
                </section>
              </div>

              <!-- AUDITORIA TAB -->
              <div v-else-if="activeTab === 'auditoria' && userStore.hasModuleItemAccess('integra_oci', 'auditoria')" key="auditoria" class="min-w-0">
                <section class="mt-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                  <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                    <div>
                      <p class="text-xs font-semibold uppercase tracking-wide text-[#2a688f] dark:text-[#42b9eb]">Integra OCI</p>
                      <h2 class="mt-1 text-xl font-semibold text-gray-900 dark:text-white">Auditoria de operações</h2>
                      <p class="mt-2 max-w-3xl text-sm text-gray-600 dark:text-gray-300">
                        Trilha completa de logins, processamentos, validações e downloads realizados no módulo.
                      </p>
                    </div>
                    <button
                      type="button"
                      @click="fetchAuditLogs()"
                      :disabled="isFetchingAuditLogs"
                      class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-[#13335a] transition hover:bg-slate-50 disabled:opacity-60 dark:border-gray-600 dark:bg-gray-900/40 dark:text-[#42b9eb] dark:hover:bg-gray-900/60"
                    >
                      <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': isFetchingAuditLogs }" />
                      Atualizar
                    </button>
                  </div>

                  <div class="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                    <div>
                      <label class="mb-1 block text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Evento</label>
                      <select
                        v-model="auditFilters.event_type"
                        class="w-full rounded-lg border-gray-300 bg-gray-50 text-sm focus:border-[#2a688f] focus:ring-[#2a688f] dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      >
                        <option value="">Todos</option>
                        <option v-for="eventType in auditEventTypes" :key="eventType" :value="eventType">
                          {{ auditEventTypeLabel(eventType) }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="mb-1 block text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">CNES</label>
                      <input
                        v-model="auditFilters.unit_cnes"
                        type="text"
                        maxlength="7"
                        placeholder="Ex: 2970627"
                        class="w-full rounded-lg border-gray-300 bg-gray-50 text-sm focus:border-[#2a688f] focus:ring-[#2a688f] dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                    <div>
                      <label class="mb-1 block text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Usuário</label>
                      <input
                        v-model="auditFilters.performed_by"
                        type="text"
                        placeholder="Nome ou login"
                        class="w-full rounded-lg border-gray-300 bg-gray-50 text-sm focus:border-[#2a688f] focus:ring-[#2a688f] dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                    <div>
                      <label class="mb-1 block text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Data inicial</label>
                      <input
                        v-model="auditFilters.start_date"
                        type="date"
                        class="w-full rounded-lg border-gray-300 bg-gray-50 text-sm focus:border-[#2a688f] focus:ring-[#2a688f] dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                    <div>
                      <label class="mb-1 block text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Data final</label>
                      <input
                        v-model="auditFilters.end_date"
                        type="date"
                        class="w-full rounded-lg border-gray-300 bg-gray-50 text-sm focus:border-[#2a688f] focus:ring-[#2a688f] dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                    <div class="flex items-end gap-2">
                      <button
                        type="button"
                        @click="applyAuditFilters"
                        class="rounded-lg bg-[#13335a] px-4 py-2 text-sm font-semibold text-white hover:bg-[#2a688f] dark:bg-[#42b9eb] dark:text-[#13335a]"
                      >
                        Filtrar
                      </button>
                      <button
                        type="button"
                        @click="clearAuditFilters"
                        class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
                      >
                        Limpar
                      </button>
                    </div>
                  </div>

                  <p v-if="auditError" class="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-900/20 dark:text-red-300">
                    {{ auditError }}
                  </p>

                  <div v-if="isFetchingAuditLogs" class="mt-8 flex h-40 items-center justify-center text-sm text-gray-500 dark:text-gray-400">
                    Carregando registros de auditoria...
                  </div>

                  <div v-else-if="auditLogs.length" class="mt-6 overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                      <thead class="bg-gray-50 dark:bg-gray-700">
                        <tr>
                          <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Data</th>
                          <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Usuário</th>
                          <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Evento</th>
                          <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Unidade / CNES</th>
                          <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Arquivos</th>
                          <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Resultado</th>
                          <th class="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-300">Status</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-800">
                        <template v-for="item in auditLogs" :key="item.id">
                          <tr @click="toggleAuditRow(item.id)" class="cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-700/50">
                            <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-900 dark:text-gray-200">
                              <div class="flex items-center">
                                <svg :class="{ 'rotate-90': expandedAuditRows.includes(item.id) }" class="mr-2 h-4 w-4 transition-transform duration-200 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                                </svg>
                                {{ item.created_at_label || formatDateTime(item.created_at) }}
                              </div>
                            </td>
                            <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-900 dark:text-gray-200">
                              <div>{{ item.performed_by || '-' }}</div>
                              <div v-if="item.username" class="text-xs text-gray-500 dark:text-gray-400">{{ item.username }}</div>
                            </td>
                            <td class="whitespace-nowrap px-4 py-3 text-sm text-gray-900 dark:text-gray-200">{{ auditEventTypeLabel(item.event_type) }}</td>
                            <td class="max-w-[220px] px-4 py-3 text-sm text-gray-900 dark:text-gray-200">
                              <div class="truncate" :title="item.unit_name">{{ item.unit_name || '-' }}</div>
                              <div v-if="item.unit_cnes" class="text-xs text-gray-500 dark:text-gray-400">CNES {{ item.unit_cnes }}</div>
                            </td>
                            <td class="max-w-[240px] px-4 py-3 text-sm text-gray-900 dark:text-gray-200">
                              <div v-if="item.apac_filename" class="truncate" :title="item.apac_filename">APAC: {{ item.apac_filename }}</div>
                              <div v-if="item.bpa_filename" class="truncate" :title="item.bpa_filename">BPA: {{ item.bpa_filename }}</div>
                              <div v-if="item.extra_files?.length" class="truncate text-xs text-gray-500 dark:text-gray-400" :title="item.extra_files.join(', ')">
                                +{{ item.extra_files.length }} arquivo(s)
                              </div>
                              <span v-if="!item.apac_filename && !item.bpa_filename && !(item.extra_files?.length)">-</span>
                            </td>
                            <td class="max-w-[280px] truncate px-4 py-3 text-sm text-gray-900 dark:text-gray-200" :title="item.result_message">
                              {{ item.result_message || '-' }}
                            </td>
                            <td class="whitespace-nowrap px-4 py-3 text-center text-sm">
                              <span
                                class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold"
                                :class="item.success
                                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                                  : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'"
                              >
                                {{ item.success ? 'Sucesso' : 'Falha' }}
                              </span>
                            </td>
                          </tr>
                          <tr v-if="expandedAuditRows.includes(item.id)" class="bg-gray-50 dark:bg-gray-700/30">
                            <td colspan="7" class="border-b border-gray-100 px-6 py-4 dark:border-gray-600">
                              <div class="grid gap-4 text-sm md:grid-cols-2 xl:grid-cols-4">
                                <div>
                                  <p class="mb-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Módulo</p>
                                  <p class="text-gray-900 dark:text-gray-200">{{ auditModuleItemLabel(item.module_item) }}</p>
                                </div>
                                <div>
                                  <p class="mb-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Competências</p>
                                  <p class="text-gray-900 dark:text-gray-200">{{ formatCompetencias(item.competencias) }}</p>
                                </div>
                                <div>
                                  <p class="mb-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">IP</p>
                                  <p class="text-gray-900 dark:text-gray-200">{{ item.ip_address || '-' }}</p>
                                </div>
                                <div>
                                  <p class="mb-1 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Histórico</p>
                                  <p class="text-gray-900 dark:text-gray-200">
                                    <span v-if="item.history_id">#{{ item.history_id }} ({{ item.history_type || 'registro' }})</span>
                                    <span v-else>-</span>
                                  </p>
                                </div>
                              </div>
                              <div v-if="item.error_message" class="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-900/20 dark:text-red-300">
                                {{ item.error_message }}
                              </div>
                              <div v-if="item.result_summary && Object.keys(item.result_summary).length" class="mt-4">
                                <p class="mb-2 text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Resumo retornado</p>
                                <pre class="max-h-64 overflow-auto rounded-lg border border-slate-200 bg-white p-3 text-xs text-gray-800 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-200">{{ formatAuditSummary(item.result_summary) }}</pre>
                              </div>
                            </td>
                          </tr>
                        </template>
                      </tbody>
                    </table>

                    <div class="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <p class="text-sm text-gray-600 dark:text-gray-400">
                        {{ auditTotal }} registro(s) · página {{ auditPage }} de {{ auditTotalPages }}
                      </p>
                      <div class="flex items-center gap-2">
                        <button
                          type="button"
                          @click="changeAuditPage(auditPage - 1)"
                          :disabled="auditPage <= 1"
                          class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-semibold text-slate-600 disabled:opacity-50 dark:border-gray-600 dark:text-gray-300"
                        >
                          Anterior
                        </button>
                        <button
                          type="button"
                          @click="changeAuditPage(auditPage + 1)"
                          :disabled="auditPage >= auditTotalPages"
                          class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-semibold text-slate-600 disabled:opacity-50 dark:border-gray-600 dark:text-gray-300"
                        >
                          Próxima
                        </button>
                      </div>
                    </div>
                  </div>

                  <div v-else class="mt-8 flex h-40 items-center justify-center text-sm text-gray-500 dark:text-gray-400">
                    Nenhum registro de auditoria encontrado para os filtros selecionados.
                  </div>
                </section>
              </div>
            </Transition>
          </div>
        </div>
      </div>

      <div
        v-if="showOciExportModal"
        class="fixed inset-0 z-[120] flex items-center justify-center bg-[#13335a]/45 px-4 py-6 backdrop-blur-[2px]"
        @click.self="closeOciExportModal"
      >
        <div class="w-full max-w-2xl overflow-hidden rounded-xl border border-[#13335a]/10 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-800">
          <div class="border-b border-slate-200 px-6 py-5 dark:border-gray-700">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-[#2a688f] dark:text-[#42b9eb]">Integra OCI</p>
                <h3 class="mt-1 text-xl font-semibold text-gray-900 dark:text-white">Central de exportação da análise atual</h3>
                <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                  Escolha o recorte da exportação e o formato do arquivo sem poluir a tela principal.
                </p>
              </div>
              <button
                type="button"
                @click="closeOciExportModal"
                class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                Fechar
              </button>
            </div>
          </div>

          <div class="space-y-5 px-6 py-6">
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-900/40">
              <label for="oci-export-mode-modal" class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-gray-400">
                Escopo da exportação
              </label>
              <select
                id="oci-export-mode-modal"
                v-model="ociExportMode"
                class="mt-2 w-full rounded-xl border border-slate-300 bg-white px-3 py-3 text-sm font-medium text-slate-700 outline-none transition focus:border-[#13335a] focus:ring-2 focus:ring-[#13335a]/15 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
              >
                <option value="all">Todos os resultados da análise</option>
                <option value="validated">Somente combos validados</option>
                <option value="missing_procedure">Somente falta de procedimento</option>
                <option value="invalid_cid">Somente CID incompatível</option>
                <option value="invalid_auth">Somente autorização inválida</option>
              </select>
              <p class="mt-2 text-xs text-slate-500 dark:text-gray-400">
                Seleção atual: {{ getOciExportModeLabel(ociExportMode) }}
              </p>
            </div>

            <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
              <button
                type="button"
                @click="handleOciExportAction('csv')"
                :disabled="isExportingOciComboCsv"
                class="rounded-xl border border-slate-200 bg-white p-4 text-left transition hover:border-[#13335a]/20 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-gray-600 dark:bg-gray-900/40 dark:hover:bg-gray-900/60"
              >
                <p class="text-sm font-semibold text-gray-900 dark:text-gray-100">
                  {{ isExportingOciComboCsv ? 'Gerando CSV...' : 'Exportar CSV/planilha' }}
                </p>
                <p class="mt-1 text-xs leading-5 text-gray-600 dark:text-gray-300">
                  Gera arquivo tabular para filtro, conferência de glosas e trabalho operacional do faturamento.
                </p>
              </button>

              <button
                type="button"
                @click="handleOciExportAction('summary_pdf')"
                :disabled="isExportingOciComboSummaryPdf"
                class="rounded-xl border border-slate-200 bg-white p-4 text-left transition hover:border-[#13335a]/20 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-gray-600 dark:bg-gray-900/40 dark:hover:bg-gray-900/60"
              >
                <p class="text-sm font-semibold text-gray-900 dark:text-gray-100">
                  {{ isExportingOciComboSummaryPdf ? 'Gerando PDF...' : 'Exportar PDF resumido' }}
                </p>
                <p class="mt-1 text-xs leading-5 text-gray-600 dark:text-gray-300">
                  Traz visão executiva com totais, recortes e síntese dos resultados da análise.
                </p>
              </button>

              <button
                type="button"
                @click="handleOciExportAction('detailed_pdf')"
                :disabled="isExportingOciComboPdf"
                class="rounded-xl border border-[#13335a]/15 bg-[#13335a] p-4 text-left transition hover:bg-[#0f2a49] disabled:cursor-not-allowed disabled:opacity-60"
              >
                <p class="text-sm font-semibold text-white">
                  {{ isExportingOciComboPdf ? 'Gerando PDF...' : 'Exportar PDF detalhado' }}
                </p>
                <p class="mt-1 text-xs leading-5 text-white/80">
                  Consolida pacientes, procedimentos, CID e CBO avaliados para conferência detalhada.
                </p>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- MODAL: Download do Histórico OCI -->
      <div
        v-if="showOciHistoryDownloadModal && selectedOciHistoryItem"
        class="fixed inset-0 z-[130] flex items-center justify-center bg-[#13335a]/45 px-4 py-6 backdrop-blur-[2px]"
        @click.self="showOciHistoryDownloadModal = false"
      >
        <div class="w-full max-w-xl overflow-hidden rounded-xl border border-[#13335a]/10 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-800">
          <!-- Header -->
          <div class="border-b border-slate-200 px-6 py-5 dark:border-gray-700">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-[#2a688f] dark:text-[#42b9eb]">Histórico OCI</p>
                <h3 class="mt-1 text-lg font-semibold text-gray-900 dark:text-white">Exportar análise</h3>
                <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                  {{ selectedOciHistoryItem.unit_name || 'Unidade não identificada' }}
                  <span v-if="selectedOciHistoryItem.unit_cnes"> · CNES {{ selectedOciHistoryItem.unit_cnes }}</span>
                </p>
                <p class="mt-0.5 text-xs text-slate-500 dark:text-gray-400">{{ formatCompetencias(selectedOciHistoryItem.competencias) }} · {{ formatDateTime(selectedOciHistoryItem.created_at) }}</p>
              </div>
              <button
                type="button"
                @click="showOciHistoryDownloadModal = false"
                class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                Fechar
              </button>
            </div>
          </div>

          <!-- Opções de download -->
          <div class="space-y-3 px-6 py-5">
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
              Todos os dados são exportados sem máscara — CPF e CNS completos para conferência.
              Os downloads são registrados em auditoria.
            </p>

            <!-- CSV / Planilha -->
            <button
              type="button"
              @click="handleHistoryDownload('csv')"
              :disabled="isExportingHistoryCsv(selectedOciHistoryItem.id)"
              class="w-full rounded-xl border border-slate-200 bg-white p-4 text-left transition hover:border-[#13335a]/20 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-gray-600 dark:bg-gray-900/40 dark:hover:bg-gray-900/60"
            >
              <div class="flex items-center gap-3">
                <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-600 dark:bg-gray-700 dark:text-gray-300">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-semibold text-gray-900 dark:text-gray-100">
                    {{ isExportingHistoryCsv(selectedOciHistoryItem.id) ? 'Gerando CSV...' : 'CSV / Planilha' }}
                  </p>
                  <p class="mt-0.5 text-xs text-gray-600 dark:text-gray-300">
                    Arquivo tabular com CPF, CNS e todos os dados dos combos. Ideal para conferência em Excel, filtragem de glosas e trabalho operacional do faturamento.
                  </p>
                </div>
              </div>
            </button>

            <!-- PDF Resumido -->
            <button
              type="button"
              @click="handleHistoryDownload('pdf_summary')"
              :disabled="isExportingSummaryHistoryPdf(selectedOciHistoryItem.id)"
              class="w-full rounded-xl border border-[#2a688f]/20 bg-[#eceded] p-4 text-left transition hover:bg-[#dfe3e3] disabled:cursor-not-allowed disabled:opacity-60 dark:border-[#42b9eb]/20 dark:bg-gray-900/40 dark:hover:bg-gray-900/60"
            >
              <div class="flex items-center gap-3">
                <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#2a688f] text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-semibold text-[#13335a] dark:text-[#42b9eb]">
                    {{ isExportingSummaryHistoryPdf(selectedOciHistoryItem.id) ? 'Gerando PDF...' : 'PDF Resumido' }}
                  </p>
                  <p class="mt-0.5 text-xs text-slate-600 dark:text-gray-300">
                    Visão executiva com totais, recortes por motivo e síntese dos combos formados e não formados. Ideal para reuniões e envio a gestores.
                  </p>
                </div>
              </div>
            </button>

            <!-- PDF Detalhado -->
            <button
              type="button"
              @click="handleHistoryDownload('pdf_detailed')"
              :disabled="isExportingDetailedHistoryPdf(selectedOciHistoryItem.id)"
              class="w-full rounded-xl border border-[#13335a]/15 bg-[#13335a] p-4 text-left transition hover:bg-[#0f2a49] disabled:cursor-not-allowed disabled:opacity-60"
            >
              <div class="flex items-center gap-3">
                <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/20 text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-semibold text-white">
                    {{ isExportingDetailedHistoryPdf(selectedOciHistoryItem.id) ? 'Gerando PDF...' : 'PDF Detalhado (para conferência)' }}
                  </p>
                  <p class="mt-0.5 text-xs text-[#eceded]/85">
                    Consolida pacientes, procedimentos, CID e CBO avaliados. Exibe CPF e CNS completos sem máscara para verificação e conferência item a item.
                  </p>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>

    </template>
  </BaseTemplate>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import BaseTemplate from '../templates/BaseTemplate.vue';
import OciAlert from './oci/OciAlert.vue';
import OciFileBadge from './oci/OciFileBadge.vue';
import OciStatCard from './oci/OciStatCard.vue';
import OciTabNav from './oci/OciTabNav.vue';
import { ociRowClass, ociRowStatusClass, ociUnitMatchClasses, ociClasses, OCI_COLORS } from './oci/ociTheme';
import api, { fetchCSRFToken } from '@/services/authService';
import jsPDF from 'jspdf';
import logoCcdti from '@/assets/logo_ccdti.png';
import { ChevronDown, ChevronLeft, ChevronRight, FileSearch, Files, History, Info, Play, Trash2, Upload, BarChart3, RefreshCw, Lightbulb, LayoutDashboard, Sparkles, ArrowRight, CheckCircle2, Layers, ShieldCheck } from 'lucide-vue-next';
import { Bar, Doughnut } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
} from 'chart.js';

import { useUserStore } from '@/stores/userStore';

const userStore = useUserStore();
const MAX_FILE_SIZE = 50 * 1024 * 1024;
const MAX_FILE_SIZE_LABEL = '50MB';

ChartJS.register(Title, Tooltip, Legend, BarElement, ArcElement, CategoryScale, LinearScale, PointElement, LineElement);

const activeTab = ref('apresentacao');
const activeSubtab = ref('main');
const dashboardActiveTab = ref('bpa');

onMounted(() => {
  if (!userStore.hasModuleItemAccess('integra_oci', 'bpa_limpo')) {
    if (userStore.hasModuleItemAccess('integra_oci', 'formar_combos')) {
      activeTab.value = 'combos';
    } else if (userStore.hasModuleItemAccess('integra_oci', 'dashboard')) {
      activeTab.value = 'dashboard';
    } else if (userStore.hasModuleItemAccess('integra_oci', 'auditoria')) {
      activeTab.value = 'auditoria';
    }
  }
  
  if (userStore.hasModuleItemAccess('integra_oci', 'historico') || userStore.hasModuleItemAccess('integra_oci', 'dashboard')) {
    fetchHistory('30d');
    fetchOciComboHistory('30d');
  }

  if (userStore.hasModuleItemAccess('integra_oci', 'auditoria')) {
    fetchAuditEventTypes();
    if (activeTab.value === 'auditoria') {
      fetchAuditLogs();
    }
  }
});

watch(activeTab, (tab) => {
  if (tab === 'auditoria' && userStore.hasModuleItemAccess('integra_oci', 'auditoria')) {
    fetchAuditLogs();
  }
});
const isModuleMenuCollapsed = ref(false);
const isTratamentoMenuOpen = ref(true);
const isCombosMenuOpen = ref(true);
const apacInputRef = ref(null);
const bpaInputRef = ref(null);
const ociComboBpaInputRef = ref(null);
const ociComboProceduresInputRef = ref(null);
const ociComboDetailsSectionRef = ref(null);
const ociComboDetailsListRef = ref(null);
const ociComboPatientsSectionRef = ref(null);
const ociComboPatientsListRef = ref(null);
const ociMissingProcedureSectionRef = ref(null);
const ociMissingProcedureListRef = ref(null);
const ociInvalidCidSectionRef = ref(null);
const ociInvalidCidListRef = ref(null);
const ociInvalidAuthSectionRef = ref(null);
const ociInvalidAuthListRef = ref(null);

const apacFile = ref(null);
const bpaFile = ref(null);
const apacAnalysis = ref(null);
const bpaAnalysis = ref(null);
const currentMetadata = ref(null);
const lastProcessStats = ref(null);

const isAnalyzingApac = ref(false);
const isAnalyzingBpa = ref(false);
const isLoading = ref(false);
const processingProgress = ref(0);
const processingProgressLabel = ref('Preparando arquivos...');
const isFetchingHistory = ref(false);
const showModuleInfo = ref(false);
const apacFieldWarning = ref('');
const bpaFieldWarning = ref('');

const errorMsg = ref('');
const successMsg = ref('');
const searchQuery = ref('');
const ANALYZE_FILE_TIMEOUT_MS = 120000;
const ANALYZE_FILE_TIMEOUT_LABEL = '2 minutos';

const ociComboBpaFiles = ref([]);
const ociComboProceduresFiles = ref([]);
const ociComboBpaAnalysis = ref(null);
const ociComboBpaAnalyses = ref([]);
const isAnalyzingOciComboBpa = ref(false);
const isOciComboLoading = ref(false);
const ociComboProgress = ref(0);
const ociComboProgressLabel = ref('Preparando base da analise...');
const ociComboBpaFieldWarning = ref('');
const ociComboErrorMsg = ref('');
const ociComboSuccessMsg = ref('');
const ociComboResult = ref(null);
const ociGeneratedTreatedBpas = ref([]);
const ociResultDetailTab = ref('formed');
const ociPatientSearchQuery = ref('');
const isExportingOciComboPdf = ref(false);
const isExportingOciComboSummaryPdf = ref(false);
const isExportingOciComboCsv = ref(false);
const ociExportMode = ref('all');
const showOciExportModal = ref(false);
const exportingOciHistoryState = ref({ id: null, mode: null });
const showOciHistoryDownloadModal = ref(false);
const selectedOciHistoryItem = ref(null);
const ociComboDetailsPage = ref(1);
const ociComboDetailsPageSize = 5;
const ociComboPatientPage = ref(1);
const ociComboPageSize = 5;
const ociAlmostComboPage = ref(1);
const ociAlmostComboPageSize = 5;
const ociInvalidCidPage = ref(1);
const ociInvalidCidPageSize = 5;
const ociInvalidAuthPage = ref(1);
const ociInvalidAuthPageSize = 5;

const unmaskedPatients = ref(new Set());
function togglePatientMask(patient) {
  const key = `${patient.name}-${patient.dob}`;
  if (unmaskedPatients.value.has(key)) {
    unmaskedPatients.value.delete(key);
  } else {
    unmaskedPatients.value.add(key);
  }
}
function isPatientMasked(patient) {
  if (!patient || !patient.name) return true;
  return !unmaskedPatients.value.has(`${patient.name}-${patient.dob}`);
}
function getPatientDisplayName(patient) {
  const raw = patient.name || 'Paciente';
  if (!isPatientMasked(patient)) return raw;
  const parts = raw.split(' ');
  if (parts.length <= 1) return raw;
  return `${parts[0]} *** ${parts[parts.length - 1]}`;
}
const isFetchingOciComboHistory = ref(false);
const ociComboHistoryPeriod = ref('30d');
const showOciComboCharts = ref(false);
const ociComboHistoryData = ref([]);
const ociComboHistorySummary = ref({
  total_analyses: 0,
  total_combo_occurrences: 0,
  total_patients_with_combos: 0,
  total_patients_analyzed: 0,
  unit_breakdown: [],
  top_unit: null,
  series: [],
});

let processingProgressTimer = null;
let ociComboProgressTimer = null;

const notFoundPatients = ref([]);
const procsNotFoundPatients = ref([]);
const ociComboDetails = ref([]);
const affectedRows = ref([]);
const expandedRows = ref([]);
const expandedAuditRows = ref([]);
const auditLogs = ref([]);
const auditEventTypes = ref([]);
const isFetchingAuditLogs = ref(false);
const auditError = ref('');
const auditPage = ref(1);
const auditPageSize = ref(20);
const auditTotal = ref(0);
const auditTotalPages = ref(1);
const auditFilters = ref({
  event_type: '',
  unit_cnes: '',
  performed_by: '',
  username: '',
  start_date: '',
  end_date: '',
});
const historyData = ref([]);
const lastGeneratedFileId = ref(null);
const lastRemovedOnlyFileId = ref(null);

const lastGeneratedFileName = ref('');
const lastRemovedOnlyFileName = ref('');

const summary = ref({
  total_removed_last_10: 0,
  avg_removed_per_import: 0,
  total_imports: 0,
  unit_breakdown: [],
  removal_series: [],
  top_unit: null,
});

function formatFileSize(bytes) {
  const size = Number(bytes || 0);
  return `${(size / 1024 / 1024).toFixed(1)}MB`;
}

function validateSelectedFileSize(file, target = 'main') {
  if (!file || Number(file.size || 0) <= MAX_FILE_SIZE) return true;
  const message = `Arquivo muito grande (${formatFileSize(file.size)}). Máximo permitido: ${MAX_FILE_SIZE_LABEL}.`;
  if (target === 'oci') {
    ociComboErrorMsg.value = message;
  } else {
    errorMsg.value = message;
  }
  return false;
}

function filterFilesBySize(files, target = 'main') {
  const validFiles = [];
  for (const file of files || []) {
    if (validateSelectedFileSize(file, target)) {
      validFiles.push(file);
    }
  }
  return validFiles;
}

function buildAnalyzeTimeoutMessage(fileName = 'o arquivo') {
  return `A pré-análise de ${fileName} demorou mais do que o esperado (${ANALYZE_FILE_TIMEOUT_LABEL}) e foi interrompida para proteger a conexão. Tente novamente. Se persistir, contacte o suporte técnico para revisar a base enviada.`;
}

function resolveAnalyzeErrorMessage(error, fallback, fileName = 'o arquivo') {
  const detail = error?.response?.data?.detail;
  const message = String(error?.message || '').toLowerCase();
  const code = String(error?.code || '').toUpperCase();

  if (code === 'ECONNABORTED' || code === 'ETIMEDOUT' || message.includes('timeout')) {
    return buildAnalyzeTimeoutMessage(fileName);
  }

  if (message.includes('network error') && !error?.response) {
    return 'A conexão com o servidor foi interrompida durante a pré-análise. Tente novamente. Se continuar ocorrendo, contacte o suporte técnico.';
  }

  return detail || fallback;
}

let csrfBootstrapPromise = null;

function getCookieValue(name) {
  const cookies = document.cookie.split('; ');
  for (const cookie of cookies) {
    const [key, value] = cookie.split('=');
    if (key === name) return decodeURIComponent(value || '');
  }
  return '';
}

async function ensureCsrfReady() {
  if (getCookieValue('csrftoken')) return;
  if (!csrfBootstrapPromise) {
    csrfBootstrapPromise = fetchCSRFToken().finally(() => {
      csrfBootstrapPromise = null;
    });
  }
  await csrfBootstrapPromise;
}

const reversedHistoryData = computed(() => [...historyData.value].reverse());

const affectedColumns = computed(() => {
  if (!affectedRows.value.length) return [];
  return Object.keys(affectedRows.value[0]).filter((key) => key !== '_status');
});

const totalNotFoundProcedures = computed(() =>
  notFoundPatients.value.reduce((sum, patient) => sum + Number(patient.total_procs || 0), 0)
);

const totalProcsNotFound = computed(() =>
  procsNotFoundPatients.value.reduce((sum, patient) => sum + Number(patient.total_leftover || 0), 0)
);

const totalOciComboProcedures = computed(() =>
  ociComboDetails.value.reduce((sum, patient) => sum + Number(patient.total_procedures || 0), 0)
);

const totalOciComboRemoved = computed(() =>
  ociComboDetails.value.reduce((sum, patient) => sum + Number(patient.total_removed || 0), 0)
);

const ociComboDetailsTotalPages = computed(() => {
  const total = ociComboDetails.value.length || 0;
  return Math.max(1, Math.ceil(total / ociComboDetailsPageSize));
});

const paginatedOciComboDetails = computed(() => {
  const start = (ociComboDetailsPage.value - 1) * ociComboDetailsPageSize;
  return ociComboDetails.value.slice(start, start + ociComboDetailsPageSize);
});

const ociComboDetailsRangeLabel = computed(() => {
  const total = ociComboDetails.value.length || 0;
  if (!total) return '0 a 0';
  const start = (ociComboDetailsPage.value - 1) * ociComboDetailsPageSize + 1;
  const end = Math.min(start + ociComboDetailsPageSize - 1, total);
  return `${start} a ${end}`;
});

const processOutcomeNotes = computed(() => {
  if (!lastProcessStats.value) return [];

  const notes = [];
  const apacOciCount = Number(lastProcessStats.value.apac_oci_count || 0);
  const removedCount = Number(lastProcessStats.value.oci_patients_removed || 0);
  const bpaBefore = Number(lastProcessStats.value.bpa_lines_before || 0);
  const bpaAfter = Number(lastProcessStats.value.bpa_lines_after || 0);

  if (apacOciCount === 0) {
    notes.push('O arquivo APAC nao apresentou registros OCI para confronto nesta importacao.');
  }
  if (removedCount === 0 && apacOciCount > 0) {
    notes.push('Os registros OCI do APAC nao encontraram correspondencia direta nas linhas elegiveis do BPA para remocao.');
  }
  if (notFoundPatients.value.length) {
    notes.push(`${notFoundPatients.value.length} paciente(s) do APAC nao foram localizados no BPA selecionado.`);
  }
  if (procsNotFoundPatients.value.length) {
    notes.push(`${procsNotFoundPatients.value.length} paciente(s) foram localizados, mas ainda restaram procedimentos ou quantidades sem correspondencia exata no BPA.`);
  }
  const matchedByCpf = Number(lastProcessStats.value.matched_by_cpf || 0);
  const matchedByCns = Number(lastProcessStats.value.matched_by_cns || 0);
  const matchedByNameDob = Number(lastProcessStats.value.matched_by_name_dob || 0);
  const apacWithCpf = Number(lastProcessStats.value.apac_with_cpf || 0);
  const apacWithCns = Number(lastProcessStats.value.apac_with_cns || 0);
  const bpaWithCpf = Number(lastProcessStats.value.bpa_with_cpf || 0);
  const bpaWithCns = Number(lastProcessStats.value.bpa_with_cns || 0);
  if (matchedByCpf || matchedByCns || matchedByNameDob) {
    notes.push(`Critérios de cruzamento usados: CPF ${matchedByCpf}, CNS ${matchedByCns} e nome/data de nascimento ${matchedByNameDob}.`);
  }
  if (!matchedByCpf && (!apacWithCpf || !bpaWithCpf)) {
    notes.push(`Cruzamento por CPF não foi aplicado nesta importação porque o identificador não esteve disponível dos dois lados. APAC com CPF: ${apacWithCpf}; BPA com CPF: ${bpaWithCpf}.`);
  }
  if (!matchedByCns && (!apacWithCns || !bpaWithCns)) {
    notes.push(`Cruzamento por CNS não foi aplicado nesta importação porque o identificador não esteve disponível dos dois lados. APAC com CNS: ${apacWithCns}; BPA com CNS: ${bpaWithCns}.`);
  }
  if (removedCount === 0 && apacOciCount > 0 && !notFoundPatients.value.length && !procsNotFoundPatients.value.length) {
    notes.push('Nesse cenario, o BPA provavelmente ja estava limpo para os registros OCI dessa competencia, ou as linhas ja nao estavam mais presentes no arquivo informado.');
  }
  notes.push(`BPA analisado com ${bpaBefore} linha(s) antes do tratamento e ${bpaAfter} linha(s) apos o processamento.`);
  return notes;
});

const processOutcomeExplanation = computed(() => {
  if (!lastProcessStats.value) return '';

  const removedCount = Number(lastProcessStats.value.oci_patients_removed || 0);
  const apacOciCount = Number(lastProcessStats.value.apac_oci_count || 0);

  if (removedCount > 0) {
    return `Foram removidas ${removedCount} linha(s) OCI do BPA tratado a partir de ${apacOciCount} registro(s) OCI identificados no APAC, preservando apenas o que permaneceu valido para faturamento e conferencia.`;
  }
  if (apacOciCount === 0) {
    return 'O processamento terminou sem remocoes porque o APAC informado nao trouxe registros OCI para limpar no BPA.';
  }
  return `O processamento terminou sem remocoes porque, embora o APAC tenha trazido ${apacOciCount} registro(s) OCI, nao houve correspondencia suficiente para excluir ou reduzir linhas no BPA informado.`;
});

const filteredAffectedRows = computed(() => {
  if (!searchQuery.value) return affectedRows.value;
  const query = searchQuery.value.toLowerCase();
  return affectedRows.value.filter((row) => Object.values(row).some((value) => String(value).toLowerCase().includes(query)));
});

const resolvedSelectedUnit = computed(() => {
  const apacUnit = apacAnalysis.value?.cnes_summary?.primary_unit;
  const bpaUnit = bpaAnalysis.value?.cnes_summary?.primary_unit;
  if (apacUnit && bpaUnit && apacUnit.cnes === bpaUnit.cnes) return apacUnit;
  return apacUnit || bpaUnit || currentMetadata.value?.resolved_unit || null;
});

const ociComboResolvedUnit = computed(() => {
  const bpaUnit = ociComboBpaAnalysis.value?.cnes_summary?.primary_unit;
  return ociComboResult.value?.resolved_unit || bpaUnit || null;
});

const hasCnes2970643 = computed(() => {
  if (ociComboResult.value?.resolved_unit?.cnes === '2970643') return true;
  if (ociComboBpaAnalysis.value?.cnes_summary?.primary_unit?.cnes === '2970643') return true;
  if (Array.isArray(ociComboBpaAnalyses.value)) {
    return ociComboBpaAnalyses.value.some(analysis => 
      analysis?.cnes_summary?.primary_unit?.cnes === '2970643' ||
      (Array.isArray(analysis?.cnes_summary?.units) && analysis.cnes_summary.units.some(u => u.cnes === '2970643'))
    );
  }
  return false;
});

const ociCompetenceWarning = computed(() => {
  const comp = ociComboResult.value?.competencias?.[0] || ociComboBpaAnalysis.value?.competencias?.[0];
  if (!comp || comp.length !== 6) return null;
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1;
  const currentComp = `${currentYear}${String(currentMonth).padStart(2, '0')}`;
  if (comp < currentComp) {
    return `Atenção: Os dados pertencem a uma competência passada (${comp}). O faturamento está sujeito a glosa por fora de prazo.`;
  }
  return null;
});

const ociComboAnalysisModeLabel = computed(() =>
  Number(ociComboBpaAnalysis.value?.file_count || 0) > 1 ? 'BPA consolidado' : 'BPA único'
);

const ociComboInputFilesForDisplay = computed(() => {
  const summaryFiles = Array.isArray(ociComboResult.value?.summary?.input_files)
    ? ociComboResult.value.summary.input_files.filter(Boolean)
    : [];
  if (summaryFiles.length) return summaryFiles;
  return Array.isArray(ociComboBpaAnalyses.value) ? ociComboBpaAnalyses.value.filter(Boolean) : [];
});

const selectedUnitMatchStatus = computed(() => {
  const apacUnit = apacAnalysis.value?.cnes_summary?.primary_unit;
  const bpaUnit = bpaAnalysis.value?.cnes_summary?.primary_unit;
  if (!apacUnit && !bpaUnit) return null;
  if (apacUnit && bpaUnit && apacUnit.cnes === bpaUnit.cnes) {
    return {
      label: 'CNES coerente entre APAC e BPA',
      classes: ociUnitMatchClasses('match'),
    };
  }
  if (apacUnit && bpaUnit && apacUnit.cnes !== bpaUnit.cnes) {
    return {
      label: 'Atenção: CNES principal divergente',
      classes: ociUnitMatchClasses('mismatch'),
    };
  }
  return {
    label: 'Unidade detectada parcialmente',
    classes: ociUnitMatchClasses('partial'),
  };
});

const selectedUnitMismatchWarning = computed(() => {
  const apacUnit = apacAnalysis.value?.cnes_summary?.primary_unit;
  const bpaUnit = bpaAnalysis.value?.cnes_summary?.primary_unit;
  if (apacUnit && bpaUnit && apacUnit.cnes !== bpaUnit.cnes) {
    return `O APAC foi identificado como ${apacUnit.nome_unidade} (${apacUnit.cnes}) e o BPA como ${bpaUnit.nome_unidade} (${bpaUnit.cnes}). Revise os arquivos antes de processar.`;
  }
  return '';
});

const hasCurrentResult = computed(() =>
  Boolean(lastProcessStats.value) || affectedRows.value.length > 0 || notFoundPatients.value.length > 0 || procsNotFoundPatients.value.length > 0
);

const resultStatusCounts = computed(() => {
  const statsCounts = lastProcessStats.value?.status_counts;
  if (statsCounts) {
    return {
      removed: Number(statsCounts.removed || 0),
      altered: Number(statsCounts.altered || 0),
      kept: Number(statsCounts.kept || 0),
    };
  }

  return affectedRows.value.reduce(
    (acc, row) => {
      const status = row._status || 'kept';
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    },
    { removed: 0, altered: 0, kept: 0 }
  );
});



const ociComboOverviewCards = computed(() => {
  const summaryData = ociComboResult.value?.summary || {};

  return [
    {
      accentBarClass: 'bg-slate-300 dark:bg-slate-600',
      label: 'Pacientes avaliados',
      value: summaryData.total_patients_analyzed || 0,
      helper: 'Total consolidado a partir dos arquivos importados para a validação do Integra OCI.',
      badge: 'Base',
      panelLabel: 'Origem consolidada',
      panelValue: `${summaryData.total_input_files || 0} arquivo(s) analisado(s)`,
    },
    {
      accentBarClass: 'bg-[#2a688f] dark:bg-[#42b9eb]',
      label: 'Combos validados',
      value: summaryData.combo_occurrences || 0,
      helper: `${summaryData.patients_with_combos || 0} paciente(s) concluíram a regra completa do combo.`,
      badge: 'Conforme',
      panelLabel: 'Pacientes com combo',
      panelValue: `${summaryData.patients_with_combos || 0} paciente(s)`,
    },
    {
      accentBarClass: 'bg-slate-400 dark:bg-slate-500',
      label: 'CID incompatível',
      value: summaryData.invalid_cid_combo_occurrences || 0,
      helper: `${summaryData.patients_with_invalid_cid_combos || 0} paciente(s) com divergência de CID (${summaryData.patients_with_combos || 0} com CID compatível).`,
      badge: 'Conferir',
      panelLabel: 'Pacientes com divergência',
      panelValue: `${summaryData.patients_with_invalid_cid_combos || 0} paciente(s) (${summaryData.patients_with_combos || 0} válidos)`,
    },
    {
      accentBarClass: 'bg-slate-500 dark:bg-slate-600',
      label: 'Autorização inválida',
      value: summaryData.invalid_auth_combo_occurrences || 0,
      helper: `${summaryData.patients_with_invalid_auth_combos || 0} paciente(s) com autorização inválida (${summaryData.patients_with_combos || 0} com autorização válida).`,
      badge: 'Bloqueado',
      panelLabel: 'Pacientes com autorização inválida',
      panelValue: `${summaryData.patients_with_invalid_auth_combos || 0} paciente(s) (${summaryData.patients_with_combos || 0} válidos)`,
    },
    {
      accentBarClass: 'bg-[#13335a] dark:bg-[#2a688f]',
      label: 'Tipos identificados',
      value: summaryData.combo_types_identified || 0,
      helper: `Entre ${summaryData.rules_catalog_size || 0} regra(s) catalogada(s) no sistema.`,
      badge: 'Catálogo',
      panelLabel: 'Cobertura de regras',
      panelValue: `${summaryData.rules_catalog_size || 0} regra(s) no catálogo`,
    },
  ];
});

const ociResultTabs = computed(() => [
  {
    key: 'formed',
    label: 'Pacientes que formam combos',
    count: ociComboResult.value?.patient_details?.length || 0,
  },
  {
    key: 'missing_procedure',
    label: 'Falta de procedimento',
    count: ociAlmostComboPatients.value.length,
  },
  {
    key: 'invalid_cid',
    label: 'CID incompatível',
    count: ociInvalidCidPatients.value.length,
  },
  {
    key: 'invalid_auth',
    label: 'Autorização inválida',
    count: ociInvalidAuthPatients.value.length,
  },
]);

const ociComboDecisionSummary = computed(() => {
  const summaryData = ociComboResult.value?.summary || {};
  return {
    formedCombos: Number(summaryData.combo_occurrences || 0),
    formedPatients: Number(summaryData.patients_with_combos || 0),
    missingProcedureCombos: Number(summaryData.almost_combo_occurrences || 0),
    missingProcedurePatients: Number(summaryData.patients_almost_with_combos || 0),
    invalidCidCombos: Number(summaryData.invalid_cid_combo_occurrences || 0),
    invalidCidPatients: Number(summaryData.patients_with_invalid_cid_combos || 0),
    invalidAuthCombos: Number(summaryData.invalid_auth_combo_occurrences || 0),
    invalidAuthPatients: Number(summaryData.patients_with_invalid_auth_combos || 0),
  };
});

function normalizeOciSearchText(value) {
  return String(value ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();
}

function collectOciSearchValues(value, values = []) {
  if (value == null) return values;
  if (Array.isArray(value)) {
    value.forEach((item) => collectOciSearchValues(item, values));
    return values;
  }
  if (typeof value === 'object') {
    Object.values(value).forEach((item) => collectOciSearchValues(item, values));
    return values;
  }
  const normalizedValue = normalizeOciSearchText(value);
  if (normalizedValue) values.push(normalizedValue);
  return values;
}

function matchesOciPatientSearch(record) {
  const normalizedQuery = normalizeOciSearchText(ociPatientSearchQuery.value);
  if (!normalizedQuery) return true;
  return collectOciSearchValues(record).some((value) => value.includes(normalizedQuery));
}

const filteredOciComboPatients = computed(() =>
  (ociComboResult.value?.patient_details || []).filter(matchesOciPatientSearch)
);

const ociAlmostComboPatients = computed(() => ociComboResult.value?.almost_combo_patients || []);
const filteredOciAlmostComboPatients = computed(() => ociAlmostComboPatients.value.filter(matchesOciPatientSearch));

const ociInvalidCidPatients = computed(() => ociComboResult.value?.invalid_cid_combo_patients || []);
const filteredOciInvalidCidPatients = computed(() => ociInvalidCidPatients.value.filter(matchesOciPatientSearch));

const ociInvalidAuthPatients = computed(() => ociComboResult.value?.invalid_auth_combo_patients || []);
const filteredOciInvalidAuthPatients = computed(() => ociInvalidAuthPatients.value.filter(matchesOciPatientSearch));

const ociPatientSearchPlaceholder = computed(() => {
  if (ociResultDetailTab.value === 'missing_procedure') {
    return 'Pesquisar pacientes pendentes por nome, CPF, CNS, combo, procedimento, CID, CBO ou arquivo';
  }
  if (ociResultDetailTab.value === 'invalid_cid') {
    return 'Pesquisar pacientes com CID incompatível por nome, CPF, CNS, combo, CID, procedimento, CBO ou arquivo';
  }
  if (ociResultDetailTab.value === 'invalid_auth') {
    return 'Pesquisar pacientes com autorização inválida por nome, CPF, CNS, combo, autorização, procedimento, CBO ou arquivo';
  }
  return 'Pesquisar pacientes com combo por nome, CPF, CNS, combo, procedimento, CID, CBO ou arquivo';
});

const ociActivePatientSearchCount = computed(() => {
  if (ociResultDetailTab.value === 'missing_procedure') return filteredOciAlmostComboPatients.value.length;
  if (ociResultDetailTab.value === 'invalid_cid') return filteredOciInvalidCidPatients.value.length;
  if (ociResultDetailTab.value === 'invalid_auth') return filteredOciInvalidAuthPatients.value.length;
  return filteredOciComboPatients.value.length;
});

const ociActivePatientTotalCount = computed(() => {
  if (ociResultDetailTab.value === 'missing_procedure') return ociAlmostComboPatients.value.length;
  if (ociResultDetailTab.value === 'invalid_cid') return ociInvalidCidPatients.value.length;
  if (ociResultDetailTab.value === 'invalid_auth') return ociInvalidAuthPatients.value.length;
  return ociComboResult.value?.patient_details?.length || 0;
});

const ociAlmostComboTotalPages = computed(() => {
  const total = filteredOciAlmostComboPatients.value.length || 0;
  return Math.max(1, Math.ceil(total / ociAlmostComboPageSize));
});

const paginatedOciAlmostComboPatients = computed(() => {
  const start = (ociAlmostComboPage.value - 1) * ociAlmostComboPageSize;
  return filteredOciAlmostComboPatients.value.slice(start, start + ociAlmostComboPageSize);
});

const ociAlmostComboRangeLabel = computed(() => {
  const total = filteredOciAlmostComboPatients.value.length || 0;
  if (!total) return '0 a 0';
  const start = (ociAlmostComboPage.value - 1) * ociAlmostComboPageSize + 1;
  const end = Math.min(start + ociAlmostComboPageSize - 1, total);
  return `${start} a ${end}`;
});

const ociInvalidCidTotalPages = computed(() => {
  const total = filteredOciInvalidCidPatients.value.length || 0;
  return Math.max(1, Math.ceil(total / ociInvalidCidPageSize));
});

const paginatedOciInvalidCidPatients = computed(() => {
  const start = (ociInvalidCidPage.value - 1) * ociInvalidCidPageSize;
  return filteredOciInvalidCidPatients.value.slice(start, start + ociInvalidCidPageSize);
});

const ociInvalidCidRangeLabel = computed(() => {
  const total = filteredOciInvalidCidPatients.value.length || 0;
  if (!total) return '0 a 0';
  const start = (ociInvalidCidPage.value - 1) * ociInvalidCidPageSize + 1;
  const end = Math.min(start + ociInvalidCidPageSize - 1, total);
  return `${start} a ${end}`;
});

const ociInvalidAuthTotalPages = computed(() => {
  const total = filteredOciInvalidAuthPatients.value.length || 0;
  return Math.max(1, Math.ceil(total / ociInvalidAuthPageSize));
});

const paginatedOciInvalidAuthPatients = computed(() => {
  const start = (ociInvalidAuthPage.value - 1) * ociInvalidAuthPageSize;
  return filteredOciInvalidAuthPatients.value.slice(start, start + ociInvalidAuthPageSize);
});

const ociInvalidAuthRangeLabel = computed(() => {
  const total = filteredOciInvalidAuthPatients.value.length || 0;
  if (!total) return '0 a 0';
  const start = (ociInvalidAuthPage.value - 1) * ociInvalidAuthPageSize + 1;
  const end = Math.min(start + ociInvalidAuthPageSize - 1, total);
  return `${start} a ${end}`;
});

const ociComboHistoryCards = computed(() => [
  {
    label: 'Análises registradas',
    value: ociComboHistorySummary.value.total_analyses || 0,
    helper: 'Execuções registradas no período selecionado.',
  },
  {
    label: 'Validações concluídas',
    value: ociComboHistorySummary.value.total_combo_occurrences || 0,
    helper: 'Quantidade total de ocorrências validadas no período.',
  },
  {
    label: 'Pacientes validados',
    value: ociComboHistorySummary.value.total_patients_with_combos || 0,
    helper: 'Pacientes que efetivamente concluíram uma validação de combo.',
  },
  {
    label: 'Unidade destaque',
    value: ociComboHistorySummary.value.top_unit?.unit_cnes || '-',
    helper: ociComboHistorySummary.value.top_unit?.unit_name || 'Sem unidade identificada no período.',
  },
]);

const ociComboHistoryUnitChartData = computed(() => {
  const topUnits = (ociComboHistorySummary.value.unit_breakdown || []).slice(0, 8);
  if (!topUnits.length) return null;
  return {
    labels: topUnits.map((item) => `${item.unit_cnes || '---'} - ${truncate(item.unit_name, 24)}`),
    datasets: [
      {
        label: 'Validações de combos',
        data: topUnits.map((item) => item.combo_occurrences),
        backgroundColor: '#13335a',
        borderRadius: 10,
      },
      {
        label: 'Pacientes com combo',
        data: topUnits.map((item) => item.patients_with_combos),
        backgroundColor: '#42b9eb',
        borderRadius: 10,
      },
    ],
  };
});

const ociComboPatientTotalPages = computed(() => {
  const total = filteredOciComboPatients.value.length || 0;
  return Math.max(1, Math.ceil(total / ociComboPageSize));
});

const paginatedOciComboPatients = computed(() => {
  const start = (ociComboPatientPage.value - 1) * ociComboPageSize;
  return filteredOciComboPatients.value.slice(start, start + ociComboPageSize);
});

const ociComboPatientRangeLabel = computed(() => {
  const total = filteredOciComboPatients.value.length || 0;
  if (!total) return '0 a 0';
  const start = (ociComboPatientPage.value - 1) * ociComboPageSize + 1;
  const end = Math.min(start + ociComboPageSize - 1, total);
  return `${start} a ${end}`;
});

const resultCards = computed(() => [
  {
    label: 'Unidade processada',
    value: currentMetadata.value?.resolved_unit?.cnes || resolvedSelectedUnit.value?.cnes || '-',
    helper: currentMetadata.value?.resolved_unit?.nome_unidade || resolvedSelectedUnit.value?.nome_unidade || 'Unidade não identificada',
  },
  {
    label: 'Linhas OCI removidas',
    value: lastProcessStats.value?.oci_patients_removed ?? resultStatusCounts.value.removed ?? 0,
    helper: 'Registros eliminados do BPA tratado.',
  },
  {
    label: 'Linhas alteradas',
    value: resultStatusCounts.value.altered || 0,
    helper: 'Registros com redução de quantidade.',
  },
  {
    label: 'Pendências',
    value: totalNotFoundProcedures.value + totalProcsNotFound.value,
    helper: 'Procedimentos ou pacientes ainda não refletidos no BPA.',
  },
  
]);

const latestStatusChartData = computed(() => {
  if (!affectedRows.value.length) return null;
  return {
    labels: ['Excluído', 'Qtd. alterada', 'Mantido'],
    datasets: [
      {
        data: [resultStatusCounts.value.removed, resultStatusCounts.value.altered, resultStatusCounts.value.kept],
        backgroundColor: OCI_COLORS.chart,
        borderWidth: 0,
      },
    ],
  };
});

const latestPendingChartData = computed(() => {
  const values = [notFoundPatients.value.length, procsNotFoundPatients.value.length, totalNotFoundProcedures.value + totalProcsNotFound.value];
  if (!values.some((value) => value > 0)) return null;
  return {
    labels: ['Pacientes não encontrados', 'Pacientes com pendência', 'Procedimentos pendentes'],
    datasets: [
      {
        label: 'Ocorrências',
        data: values,
        backgroundColor: [OCI_COLORS.chart[0], OCI_COLORS.chart[1], OCI_COLORS.chart[3]],
        borderRadius: 10,
      },
    ],
  };
});

const commonPlugins = {
  legend: {
    labels: {
      color: '#6b7280',
      font: { size: 12 },
    },
  },
};

const dashboardUnitFilter = ref('');
const dashboardPeriodFilter = ref('30d');
const dashboardStartDate = ref('');
const dashboardEndDate = ref('');

watch(dashboardPeriodFilter, () => {
  if (dashboardPeriodFilter.value !== 'custom') {
    fetchOciComboHistory();
    fetchHistory();
  }
});

function applyCustomDateFilter() {
  if (dashboardStartDate.value && dashboardEndDate.value) {
    fetchOciComboHistory();
    fetchHistory();
  }
}

const dashboardAvailableUnits = computed(() => {
  const unitsMap = new Map();
  if (dashboardActiveTab.value === 'bpa') {
    (summary.value.unit_breakdown || []).forEach((item) => {
      if (item.unit_cnes) {
        unitsMap.set(item.unit_cnes, item.unit_name);
      }
    });
  } else {
    (ociComboHistorySummary.value.unit_breakdown || []).forEach((item) => {
      if (item.unit_cnes) {
        unitsMap.set(item.unit_cnes, item.unit_name);
      }
    });
  }
  return Array.from(unitsMap.entries()).map(([cnes, name]) => ({ cnes, name })).sort((a, b) => a.name.localeCompare(b.name));
});

const dashboardBpaChartData = computed(() => {
  let topUnits = (summary.value.unit_breakdown || []);
  if (dashboardUnitFilter.value) {
    topUnits = topUnits.filter(u => u.unit_cnes === dashboardUnitFilter.value);
  }
  topUnits = topUnits.slice(0, 10);
  if (!topUnits.length) return null;
  return {
    labels: topUnits.map((item) => `${dashboardUnitFilter.value ? truncate(item.unit_name, 30) : (item.unit_cnes || '---')} `),
    datasets: [
      {
        label: 'Pacientes OCI Removidos',
        data: topUnits.map((item) => item.oci_patients_removed),
        backgroundColor: OCI_COLORS.chart[1],
        borderRadius: 4,
      },
      {
        label: 'Registros OCI no APAC',
        data: topUnits.map((item) => item.apac_oci_count),
        backgroundColor: OCI_COLORS.chart[3],
        borderRadius: 4,
      },
    ],
  };
});

const dashboardBpaChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } },
    tooltip: {
      callbacks: {
        title: (context) => {
          return context[0].label;
        }
      }
    }
  },
  scales: {
    y: { beginAtZero: true, grid: { borderDash: [2, 2] } },
    x: { grid: { display: false } }
  }
};

const dashboardComboChartData = computed(() => {
  let topUnits = (ociComboHistorySummary.value.unit_breakdown || []);
  if (dashboardUnitFilter.value) {
    topUnits = topUnits.filter(u => u.unit_cnes === dashboardUnitFilter.value);
  }
  topUnits = topUnits.slice(0, 10);
  if (!topUnits.length) return null;
  return {
    labels: topUnits.map((item) => `${dashboardUnitFilter.value ? truncate(item.unit_name, 30) : (item.unit_cnes || '---')} `),
    datasets: [
      {
        label: 'Combos Formados',
        data: topUnits.map((item) => item.combo_occurrences),
        backgroundColor: OCI_COLORS.chart[0],
        borderRadius: 4,
      },
      {
        label: 'Não Formados (CID)',
        data: topUnits.map((item) => item.invalid_cid_combo_occurrences || 0),
        backgroundColor: OCI_COLORS.chart[1],
        borderRadius: 4,
      },
      {
        label: 'Não Formados (Auth)',
        data: topUnits.map((item) => item.invalid_auth_combo_occurrences || 0),
        backgroundColor: OCI_COLORS.chart[3],
        borderRadius: 4,
      },
    ],
  };
});

const dashboardComboChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } },
    tooltip: {
      callbacks: {
        title: (context) => {
          return context[0].label;
        }
      }
    }
  },
  scales: {
    y: { beginAtZero: true, grid: { borderDash: [2, 2] } },
    x: { grid: { display: false }, stacked: false }
  }
};

const dashboardComboRankData = computed(() => {
  let units = ociComboHistorySummary.value.unit_breakdown || [];
  if (dashboardUnitFilter.value) {
    units = units.filter(u => u.unit_cnes === dashboardUnitFilter.value);
  }
  return units.map((item) => {
    const totalInvalid = (item.invalid_cid_combo_occurrences || 0) + (item.invalid_auth_combo_occurrences || 0);
    const avg = item.analyses > 0 ? (totalInvalid / item.analyses).toFixed(2) : 0;
    return { ...item, avg_invalid: avg };
  }).sort((a, b) => b.avg_invalid - a.avg_invalid).slice(0, 10);
});

const dashboardFilteredComboSummary = computed(() => {
  if (!dashboardUnitFilter.value) return ociComboHistorySummary.value;
  
  const unitData = (ociComboHistorySummary.value.unit_breakdown || []).find(u => u.unit_cnes === dashboardUnitFilter.value);
  if (!unitData) {
    return {
      total_patients_with_combos: 0,
      total_combo_occurrences: 0,
      total_invalid_cid_combo_occurrences: 0,
      total_invalid_auth_combo_occurrences: 0
    };
  }
  
  return {
    total_patients_with_combos: unitData.patients_with_combos || 0,
    total_combo_occurrences: unitData.combo_occurrences || 0,
    total_invalid_cid_combo_occurrences: unitData.invalid_cid_combo_occurrences || 0,
    total_invalid_auth_combo_occurrences: unitData.invalid_auth_combo_occurrences || 0
  };
});

const dashboardFilteredBpaSummary = computed(() => {
  if (!dashboardUnitFilter.value) return summary.value;
  
  const unitData = (summary.value.unit_breakdown || []).find(u => u.unit_cnes === dashboardUnitFilter.value);
  if (!unitData) {
    return {
      total_patients_with_combos: 0
    };
  }
  
  return {
    total_patients_with_combos: unitData.patients_with_combos || 0
  };
});

const ociComboHistoryUnitChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    ...commonPlugins,
    title: {
      display: true,
      text: 'Validações de combos por unidade no período',
    },
  },
};

const latestStatusChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    ...commonPlugins,
    title: {
      display: true,
      text: 'Distribuição das linhas processadas',
    },
  },
};

const latestPendingChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    ...commonPlugins,
    title: {
      display: true,
      text: 'Pendências encontradas na comparação',
    },
  },
};

async function fetchAuditLogs(page = auditPage.value) {
  if (!userStore.hasModuleItemAccess('integra_oci', 'auditoria')) {
    return;
  }

  isFetchingAuditLogs.value = true;
  auditError.value = '';
  try {
    const params = new URLSearchParams();
    params.set('page', String(page));
    params.set('page_size', String(auditPageSize.value));
    if (auditFilters.value.event_type) params.set('event_type', auditFilters.value.event_type);
    if (auditFilters.value.unit_cnes) params.set('unit_cnes', auditFilters.value.unit_cnes);
    if (auditFilters.value.performed_by) params.set('performed_by', auditFilters.value.performed_by);
    if (auditFilters.value.username) params.set('username', auditFilters.value.username);
    if (auditFilters.value.start_date) params.set('start_date', auditFilters.value.start_date);
    if (auditFilters.value.end_date) params.set('end_date', auditFilters.value.end_date);

    const response = await api.get(`/api/v1/bpa-apac/integra-oci/audit/?${params.toString()}`);
    auditLogs.value = response.data.items || [];
    auditTotal.value = response.data.total || 0;
    auditPage.value = response.data.page || page;
    auditTotalPages.value = response.data.total_pages || 1;
  } catch (error) {
    console.error('Erro ao buscar auditoria:', error);
    auditError.value = error?.response?.data?.detail || 'Não foi possível carregar os registros de auditoria.';
    auditLogs.value = [];
  } finally {
    isFetchingAuditLogs.value = false;
  }
}

async function fetchAuditEventTypes() {
  if (!userStore.hasModuleItemAccess('integra_oci', 'auditoria')) {
    return;
  }
  try {
    const response = await api.get('/api/v1/bpa-apac/integra-oci/audit/event-types/');
    auditEventTypes.value = Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('Erro ao buscar tipos de evento da auditoria:', error);
  }
}

function applyAuditFilters() {
  auditPage.value = 1;
  fetchAuditLogs(1);
}

function clearAuditFilters() {
  auditFilters.value = {
    event_type: '',
    unit_cnes: '',
    performed_by: '',
    username: '',
    start_date: '',
    end_date: '',
  };
  applyAuditFilters();
}

function changeAuditPage(page) {
  if (page < 1 || page > auditTotalPages.value) return;
  fetchAuditLogs(page);
}

function toggleAuditRow(id) {
  const index = expandedAuditRows.value.indexOf(id);
  if (index >= 0) {
    expandedAuditRows.value.splice(index, 1);
  } else {
    expandedAuditRows.value.push(id);
  }
}

function auditEventTypeLabel(eventType) {
  const labels = {
    login: 'Login',
    bpa_limpo_process: 'Processamento BPA',
    bpa_limpo_download: 'Download BPA',
    combo_validate: 'Validação de Combos',
    combo_download: 'Download Combo',
    file_analyze: 'Análise de Arquivo',
  };
  return labels[eventType] || eventType || '-';
}

function auditModuleItemLabel(moduleItem) {
  const labels = {
    sistema: 'Sistema',
    bpa_limpo: 'BPA Inteligente',
    formar_combos: 'Validação de Combos',
    dashboard: 'Dashboard',
    historico: 'Histórico',
    auditoria: 'Auditoria',
  };
  return labels[moduleItem] || moduleItem || '-';
}

function formatAuditSummary(summary) {
  try {
    return JSON.stringify(summary, null, 2);
  } catch (error) {
    return String(summary || '');
  }
}

async function fetchHistory(period = null) {
  isFetchingHistory.value = true;
  try {
    const p = period || dashboardPeriodFilter.value;
    let url = `/api/v1/bpa-apac/history/`;
    if (p === 'custom' && dashboardStartDate.value && dashboardEndDate.value) {
      url += `?start_date=${dashboardStartDate.value}&end_date=${dashboardEndDate.value}`;
    } else {
      url += `?period=${encodeURIComponent(p)}`;
    }
    const response = await api.get(url);
    historyData.value = response.data.history || [];
    summary.value = response.data.summary || summary.value;
  } catch (error) {
    console.error('Erro ao buscar histórico:', error);
  } finally {
    isFetchingHistory.value = false;
  }
}

async function fetchOciComboHistory(period = null) {
  isFetchingOciComboHistory.value = true;
  try {
    const p = period || dashboardPeriodFilter.value;
    let url = `/api/v1/bpa-apac/oci-combos/history/`;
    if (p === 'custom' && dashboardStartDate.value && dashboardEndDate.value) {
      url += `?start_date=${dashboardStartDate.value}&end_date=${dashboardEndDate.value}`;
    } else {
      url += `?period=${encodeURIComponent(p)}`;
    }
    const response = await api.get(url);
    ociComboHistoryData.value = response.data.history || [];
    ociComboHistorySummary.value = response.data.summary || ociComboHistorySummary.value;
  } catch (error) {
    console.error('Erro ao buscar histórico OCI:', error);
  } finally {
    isFetchingOciComboHistory.value = false;
  }
}

function toggleRow(id) {
  const index = expandedRows.value.indexOf(id);
  if (index >= 0) {
    expandedRows.value.splice(index, 1);
  } else {
    expandedRows.value.push(id);
  }
}

function procedureEntries(mapValue) {
  return Object.entries(mapValue || {})
    .map(([proc, qty]) => ({ proc, qty: Number(qty || 0) }))
    .sort((a, b) => a.proc.localeCompare(b.proc));
}

function procedureDisplayEntries(detailList, mapValue) {
  if (Array.isArray(detailList) && detailList.length) {
    return detailList
      .map((item) => ({
        code: String(item?.code || '').trim(),
        qty: Number(item?.qty || 0),
        name: String(item?.name || '').trim(),
      }))
      .sort((a, b) => a.code.localeCompare(b.code));
  }

  return procedureEntries(mapValue).map((item) => ({
    code: item.proc,
    qty: item.qty,
    name: '',
  }));
}

async function analyzeSelectedFile(kind, file) {
  await ensureCsrfReady();
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post(`/api/v1/bpa-apac/analyze-file/?kind=${encodeURIComponent(kind)}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: ANALYZE_FILE_TIMEOUT_MS,
  });
  return response.data;
}

function buildUploadedFileKey(file) {
  return [file?.name || '', file?.size || 0, file?.lastModified || 0].join('__');
}

function mergeUniqueUploadedFiles(existingFiles, selectedFiles) {
  const merged = [...existingFiles];
  const seen = new Set(existingFiles.map((file) => buildUploadedFileKey(file)));

  selectedFiles.forEach((file) => {
    const key = buildUploadedFileKey(file);
    if (!seen.has(key)) {
      seen.add(key);
      merged.push(file);
    }
  });

  return merged;
}

function resetMainProcessingResults() {
  errorMsg.value = '';
  successMsg.value = '';
  currentMetadata.value = null;
  lastProcessStats.value = null;
  notFoundPatients.value = [];
  procsNotFoundPatients.value = [];
  ociComboDetails.value = [];
  affectedRows.value = [];
  lastGeneratedFileId.value = null;
  lastGeneratedFileName.value = '';
  lastRemovedOnlyFileId.value = null;
  lastRemovedOnlyFileName.value = '';
  searchQuery.value = '';
}

function resetOciComboResults() {
  ociComboErrorMsg.value = '';
  ociComboSuccessMsg.value = '';
  ociComboResult.value = null;
  ociGeneratedTreatedBpas.value = [];
  ociPatientSearchQuery.value = '';
  ociComboDetailsPage.value = 1;
  ociComboPatientPage.value = 1;
  ociAlmostComboPage.value = 1;
  ociInvalidCidPage.value = 1;
}

function clearSelectedFile(kind) {
  resetMainProcessingResults();
  if (kind === 'apac') {
    apacFile.value = null;
    apacAnalysis.value = null;
    apacFieldWarning.value = '';
    if (apacInputRef.value) apacInputRef.value.value = '';
    return;
  }
  bpaFile.value = null;
  bpaAnalysis.value = null;
  bpaFieldWarning.value = '';
  if (bpaInputRef.value) bpaInputRef.value.value = '';
}

function clearOciComboBpaFiles() {
  resetOciComboResults();
  ociComboBpaFiles.value = [];
  ociComboBpaAnalyses.value = [];
  ociComboBpaAnalysis.value = null;
  ociComboBpaFieldWarning.value = '';
  if (ociComboBpaInputRef.value) ociComboBpaInputRef.value.value = '';
}

function removeOciComboBpaFile(targetFile) {
  const targetKey = buildUploadedFileKey(targetFile);
  ociComboBpaFiles.value = ociComboBpaFiles.value.filter((file) => buildUploadedFileKey(file) !== targetKey);
  ociComboBpaAnalyses.value = ociComboBpaAnalyses.value.filter((analysis) => analysis?.file_name !== targetFile?.name);
  ociComboBpaAnalysis.value = buildOciComboBpaAnalysisSummary(ociComboBpaAnalyses.value);
  ociComboBpaFieldWarning.value = '';
  resetOciComboResults();
  if (!ociComboBpaFiles.value.length && ociComboBpaInputRef.value) {
    ociComboBpaInputRef.value.value = '';
  }
}

function clearOciComboProcedureFiles() {
  resetOciComboResults();
  ociComboProceduresFiles.value = [];
  if (ociComboProceduresInputRef.value) ociComboProceduresInputRef.value.value = '';
}

function removeOciComboProcedureFile(targetFile) {
  const targetKey = buildUploadedFileKey(targetFile);
  ociComboProceduresFiles.value = ociComboProceduresFiles.value.filter((file) => buildUploadedFileKey(file) !== targetKey);
  resetOciComboResults();
  if (!ociComboProceduresFiles.value.length && ociComboProceduresInputRef.value) {
    ociComboProceduresInputRef.value.value = '';
  }
}

async function handleFileChange(kind, event) {
  const file = event.target.files?.[0] || null;
  resetMainProcessingResults();
  if (kind === 'apac') apacFieldWarning.value = '';
  if (kind === 'bpa') bpaFieldWarning.value = '';

  if (kind === 'apac') {
    apacFile.value = file;
    apacAnalysis.value = null;
  } else {
    bpaFile.value = file;
    bpaAnalysis.value = null;
  }

  if (!file) return;
  if (!validateSelectedFileSize(file, 'main')) {
    if (kind === 'apac') {
      apacFile.value = null;
      if (apacInputRef.value) apacInputRef.value.value = '';
    } else {
      bpaFile.value = null;
      if (bpaInputRef.value) bpaInputRef.value.value = '';
    }
    return;
  }

  try {
    if (kind === 'apac') isAnalyzingApac.value = true;
    if (kind === 'bpa') isAnalyzingBpa.value = true;
    const analysis = await analyzeSelectedFile(kind, file);
    if (analysis?.mismatch_detected) {
      const warningMessage =
        analysis.detail ||
        `O arquivo selecionado nao corresponde ao campo ${kind.toUpperCase()}. Revise se voce nao trocou o BPA pelo APAC.`;
      if (kind === 'apac') {
        apacFieldWarning.value = warningMessage;
        apacAnalysis.value = null;
      }
      if (kind === 'bpa') {
        bpaFieldWarning.value = warningMessage;
        bpaAnalysis.value = null;
      }
      return;
    }
    if (kind === 'apac') apacAnalysis.value = analysis;
    if (kind === 'bpa') bpaAnalysis.value = analysis;
  } catch (error) {
    console.error(`Erro ao analisar ${kind}:`, error);
    errorMsg.value = resolveAnalyzeErrorMessage(
      error,
      `Não foi possível analisar o arquivo ${kind.toUpperCase()}.`,
      file?.name || `o arquivo ${kind.toUpperCase()}`,
    );
  } finally {
    if (kind === 'apac') isAnalyzingApac.value = false;
    if (kind === 'bpa') isAnalyzingBpa.value = false;
  }
}

async function handleOciComboBpaFileChange(event) {
  const selectedFiles = filterFilesBySize(Array.from(event.target.files || []), 'oci');
  resetOciComboResults();
  ociComboBpaFieldWarning.value = '';
  if (!selectedFiles.length) return;

  const existingFiles = [...ociComboBpaFiles.value];
  const existingAnalyses = [...ociComboBpaAnalyses.value];
  const mergedFiles = mergeUniqueUploadedFiles(existingFiles, selectedFiles);
  const existingKeys = new Set(existingFiles.map((file) => buildUploadedFileKey(file)));
  const newFiles = mergedFiles.filter((file) => !existingKeys.has(buildUploadedFileKey(file)));

  ociComboBpaFiles.value = mergedFiles;
  ociComboBpaAnalysis.value = null;

  try {
    isAnalyzingOciComboBpa.value = true;
    const analyses = [...existingAnalyses];
    const validFiles = [...existingFiles];
    let hasError = false;

    for (const file of newFiles) {
      try {
        const analysis = await analyzeSelectedFile('bpa', file);
        if (analysis?.mismatch_detected) {
          const warningMessage =
            analysis.detail ||
            `O arquivo ${file.name} nao corresponde ao campo BPA. Revise o arquivo informado.`;
          ociComboBpaFieldWarning.value = warningMessage;
          hasError = true;
          break; // Stop processing further files if one is invalid format
        }
        analyses.push(analysis);
        validFiles.push(file);
      } catch (error) {
        console.error(`Erro ao analisar arquivo individual ${file.name}:`, error);
        ociComboErrorMsg.value = resolveAnalyzeErrorMessage(
          error,
          `Nao foi possivel analisar o arquivo ${file.name}.`,
          file?.name || 'o arquivo BPA',
        );
        hasError = true;
        break; // Stop on first error (e.g. invalid CNES)
      }
    }
    
    if (!hasError) {
      ociComboBpaFiles.value = validFiles;
      ociComboBpaAnalyses.value = analyses;
      ociComboBpaAnalysis.value = buildOciComboBpaAnalysisSummary(analyses);
    } else {
      // Se deu erro, reverte para os arquivos que já estavam válidos antes da seleção
      ociComboBpaFiles.value = existingFiles;
      ociComboBpaAnalyses.value = existingAnalyses;
      ociComboBpaAnalysis.value = existingAnalyses.length ? buildOciComboBpaAnalysisSummary(existingAnalyses) : null;
    }
  } catch (error) {
    console.error('Erro ao analisar BPA para validacao de combos:', error);
    ociComboBpaFiles.value = existingFiles;
    ociComboBpaAnalyses.value = existingAnalyses;
    ociComboBpaAnalysis.value = existingAnalyses.length ? buildOciComboBpaAnalysisSummary(existingAnalyses) : null;
    ociComboErrorMsg.value = error.response?.data?.detail || 'Nao foi possivel analisar o arquivo BPA para a validacao de combos.';
  } finally {
    isAnalyzingOciComboBpa.value = false;
    if (ociComboBpaInputRef.value) ociComboBpaInputRef.value.value = '';
  }
}

function handleOciComboProceduresFileChange(event) {
  const selectedFiles = filterFilesBySize(Array.from(event.target.files || []), 'oci');
  resetOciComboResults();
  if (!selectedFiles.length) return;

  ociComboProceduresFiles.value = mergeUniqueUploadedFiles(
    ociComboProceduresFiles.value,
    selectedFiles,
  );
  if (ociComboProceduresInputRef.value) ociComboProceduresInputRef.value.value = '';
}

async function loadHistoryDetails(item) {
  try {
    const response = await api.get(`/api/v1/bpa-apac/history/${item.id}/details/`);
    if (response.data.error) {
      errorMsg.value = 'Detalhes não encontrados ou expirados.';
      return;
    }

    affectedRows.value = response.data.affected_rows || [];
    notFoundPatients.value = response.data.not_found_patients || [];
    procsNotFoundPatients.value = response.data.procs_not_found_patients || [];
    ociComboDetails.value = response.data.oci_combo_details || [];
    ociComboDetailsPage.value = 1;
    currentMetadata.value = response.data.metadata || null;
    lastProcessStats.value = response.data.stats || {
      apac_oci_count: item.apac_oci_count || 0,
      bpa_lines_before: item.bpa_lines_before || 0,
      bpa_lines_after: item.bpa_lines_after || 0,
      oci_patients_removed: item.oci_patients_removed || 0,
    };
    lastGeneratedFileId.value = item.id;
    lastGeneratedFileName.value = response.data.metadata?.treated_filename || `${(item.bpa_filename || 'bpa_tratado').replace(/\.[^.]+$/, '')}_tratado.txt`;
    lastRemovedOnlyFileId.value = response.data.metadata?.removed_only_filename ? item.id : null;
    lastRemovedOnlyFileName.value = response.data.metadata?.removed_only_filename || '';
    searchQuery.value = '';

    setTimeout(() => {
      window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth',
      });
    }, 100);
  } catch (error) {
    console.error('Erro ao carregar detalhes:', error);
    errorMsg.value = 'Falha ao buscar os detalhes desta importação.';
  }
}

async function submitFiles() {
  if (!apacFile.value || !bpaFile.value) {
    errorMsg.value = 'Por favor, selecione os dois arquivos.';
    return;
  }
  if (!validateSelectedFileSize(apacFile.value, 'main') || !validateSelectedFileSize(bpaFile.value, 'main')) {
    return;
  }

  isLoading.value = true;
  resetProgress('processing');
  startProgressTimer('processing');
  errorMsg.value = '';
  successMsg.value = '';
  notFoundPatients.value = [];
  procsNotFoundPatients.value = [];
  ociComboDetails.value = [];
  affectedRows.value = [];
  lastGeneratedFileId.value = null;
  lastGeneratedFileName.value = '';
  lastRemovedOnlyFileId.value = null;
  lastRemovedOnlyFileName.value = '';
  currentMetadata.value = null;
  lastProcessStats.value = null;
  searchQuery.value = '';

  const formData = new FormData();
  formData.append('apac_file', apacFile.value);
  formData.append('bpa_file', bpaFile.value);

  try {
    await ensureCsrfReady();
    const response = await api.post('/api/v1/bpa-apac/process/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => handleUploadProgress('processing', event),
    });

    completeProgress('processing', true);

    const data = response.data || {};
    notFoundPatients.value = data.not_found || [];
    procsNotFoundPatients.value = data.procs_not_found_patients || [];
    ociComboDetails.value = data.oci_combo_details || [];
    ociComboDetailsPage.value = 1;
    affectedRows.value = data.affected_rows || [];
    currentMetadata.value = {
      apac_analysis: data.apac_analysis || apacAnalysis.value,
      bpa_analysis: data.bpa_analysis || bpaAnalysis.value,
      resolved_unit: data.resolved_unit || resolvedSelectedUnit.value,
    };
    lastProcessStats.value = data.stats || null;

    if (data.file_id) {
      lastGeneratedFileId.value = data.file_id;
      lastGeneratedFileName.value = data.filename || 'BPA_tratado.txt';
    }
    lastRemovedOnlyFileId.value = data.removed_only_file_id || null;
    lastRemovedOnlyFileName.value = data.removed_only_filename || '';

    if (data.stats) {
      successMsg.value = data.stats.oci_patients_removed
        ? `Processamento concluido com sucesso. ${data.stats.oci_patients_removed} linha(s) OCI removida(s).${data.removed_only_file_id ? ' Dois arquivos disponiveis: BPA limpo e BPA com procedimentos removidos.' : ''}`
        : 'Processamento concluido com sucesso, sem remocoes OCI nesta execucao.';
    } else {
      successMsg.value = 'Processamento concluido com sucesso.';
    }

    fetchHistory().catch((historyError) => {
      console.error('Erro ao atualizar historico apos processamento:', historyError);
    });
  } catch (error) {
    completeProgress('processing', false);
    console.error('Erro no processamento:', error);
    errorMsg.value = error.response?.data?.detail || 'Erro de conexão ou no processamento dos arquivos.';
  } finally {
    isLoading.value = false;
    resetProgress('processing');
    if (apacInputRef.value) apacInputRef.value.value = '';
    if (bpaInputRef.value) bpaInputRef.value.value = '';
    apacFile.value = null;
    bpaFile.value = null;
  }
}

async function submitOciComboFiles() {
  if (!ociComboBpaFiles.value.length && !ociComboProceduresFiles.value.length) {
    ociComboErrorMsg.value = 'Por favor, selecione ao menos um arquivo BPA ou uma planilha complementar para validar os combos.';
    return;
  }
  if (
    !ociComboBpaFiles.value.every((file) => validateSelectedFileSize(file, 'oci'))
    || !ociComboProceduresFiles.value.every((file) => validateSelectedFileSize(file, 'oci'))
  ) {
    return;
  }

  isOciComboLoading.value = true;
  resetProgress('oci');
  startProgressTimer('oci');
  ociComboErrorMsg.value = '';
  ociComboSuccessMsg.value = '';
  ociComboResult.value = null;
  ociGeneratedTreatedBpas.value = [];
  ociPatientSearchQuery.value = '';
  ociComboPatientPage.value = 1;
  ociAlmostComboPage.value = 1;

  const formData = new FormData();
  ociComboBpaFiles.value.forEach((file) => {
    formData.append('bpa_files', file);
  });
  ociComboProceduresFiles.value.forEach((file) => {
    formData.append('procedures_files', file);
  });

  try {
    await ensureCsrfReady();
    const response = await api.post('/api/v1/bpa-apac/oci-combos/analyze/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => handleUploadProgress('oci', event),
    });

    completeProgress('oci', true);

    ociComboResult.value = response.data || null;
    ociGeneratedTreatedBpas.value = Array.isArray(response.data?.generated_treated_bpas)
      ? response.data.generated_treated_bpas
      : response.data?.generated_treated_bpa
        ? [response.data.generated_treated_bpa]
        : [];
    if ((response.data?.patient_details || []).length) {
      ociResultDetailTab.value = 'formed';
    } else if ((response.data?.almost_combo_patients || []).length) {
      ociResultDetailTab.value = 'missing_procedure';
    } else {
      ociResultDetailTab.value = 'invalid_cid';
    }
    ociComboBpaAnalysis.value = response.data?.bpa_analysis || null;
    ociComboBpaAnalyses.value = response.data?.bpa_analyses || [];
    ociComboPatientPage.value = 1;
    ociAlmostComboPage.value = 1;
    ociInvalidCidPage.value = 1;
    await fetchOciComboHistory();
    const totalCombos = response.data?.summary?.combo_occurrences || 0;
    const totalPatients = response.data?.summary?.patients_with_combos || 0;
    const missingProcedureCombos = response.data?.summary?.almost_combo_occurrences || 0;
    const missingProcedurePatients = response.data?.summary?.patients_almost_with_combos || 0;
    const invalidCidCombos = response.data?.summary?.invalid_cid_combo_occurrences || 0;
    const invalidCidPatients = response.data?.summary?.patients_with_invalid_cid_combos || 0;
    const supplementalCount = Number(response.data?.summary?.supplemental_sheet_file_count || 0);
    const supplementalNames = Array.isArray(response.data?.summary?.supplemental_sheet_file_names)
      ? response.data.summary.supplemental_sheet_file_names.filter(Boolean)
      : [];
    const treatedBpas = Array.isArray(response.data?.generated_treated_bpas)
      ? response.data.generated_treated_bpas
      : response.data?.generated_treated_bpa
        ? [response.data.generated_treated_bpa]
        : [];
    const supplementalLabel = response.data?.summary?.supplemental_sheet_used
      ? ` ${supplementalCount > 1 ? `${supplementalCount} planilhas complementares` : 'A planilha complementar'} ${supplementalNames.length ? `(${supplementalNames.join(', ')}) ` : ''}também ${supplementalCount > 1 ? 'foram' : 'foi'} considerada${supplementalCount > 1 ? 's' : ''} nesta análise.`
      : '';
    const treatedBpaSummaries = treatedBpas.map((item) => {
      const targetLabel = item?.target_code || item?.target_display_name || item?.target_cnes || 'CNES';
      if (item?.generated) {
        const removedLabel = item?.removed_only_file_id ? ' Um BPA com os procedimentos removidos também está disponível para download.' : '';
        return `O BPA tratado do ${targetLabel} (CNES ${item.target_cnes || '-'}) foi gerado${item?.stats?.oci_patients_removed ? ` com ${item.stats.oci_patients_removed} remoção(ões)/ajuste(s)` : ' sem remoções necessárias'} e já está disponível para download.${removedLabel}`;
      }
      return item?.notice || `O BPA tratado do ${targetLabel} não foi gerado nesta análise.`;
    }).filter(Boolean);
    const treatedBpaLabel = treatedBpaSummaries.length ? ` ${treatedBpaSummaries.join(' ')}` : '';
    if (totalCombos) {
      ociComboSuccessMsg.value = `Validacao concluida com sucesso. ${totalPatients} paciente(s) formaram ${totalCombos} ocorrencia(s) de combo.${missingProcedureCombos ? ` ${missingProcedurePatients} paciente(s) ficaram com ${missingProcedureCombos} ocorrencia(s) pendente(s) por falta de procedimento.` : ''}${invalidCidCombos ? ` ${invalidCidPatients} paciente(s) tambem fecharam ${invalidCidCombos} ocorrencia(s) com CID incompatível.` : ''}${supplementalLabel}${treatedBpaLabel}`;
    } else if (missingProcedureCombos || invalidCidCombos) {
      ociComboSuccessMsg.value = `Validacao concluida com sucesso. Nenhum combo foi validado por completo.${missingProcedureCombos ? ` ${missingProcedurePatients} paciente(s) ficaram com ${missingProcedureCombos} ocorrencia(s) pendente(s) por falta de procedimento.` : ''}${invalidCidCombos ? ` ${invalidCidPatients} paciente(s) fecharam ${invalidCidCombos} ocorrencia(s) de combo com CID incompatível.` : ''}${supplementalLabel}${treatedBpaLabel}`;
    } else {
      ociComboSuccessMsg.value = `Validacao concluida com sucesso, mas nenhum combo foi formado com os arquivos informados.${supplementalLabel}${treatedBpaLabel}`;
    }
  } catch (error) {
    completeProgress('oci', false);
    console.error('Erro ao validar combos:', error);
    ociComboErrorMsg.value = error.response?.data?.detail || 'Erro de conexao ou no processamento dos arquivos para validar os combos.';
  } finally {
    isOciComboLoading.value = false;
    resetProgress('oci');
    if (ociComboBpaInputRef.value) ociComboBpaInputRef.value.value = '';
    if (ociComboProceduresInputRef.value) ociComboProceduresInputRef.value.value = '';
    ociComboBpaFiles.value = [];
    ociComboProceduresFiles.value = [];
  }
}

function resetOciResultPagination() {
  ociComboPatientPage.value = 1;
  ociAlmostComboPage.value = 1;
  ociInvalidCidPage.value = 1;
}

async function loadImageAsDataUrl(url) {
  const response = await fetch(url);
  const blob = await response.blob();
  return await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

async function getImageDimensions(src) {
  return await new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      resolve({
        width: image.naturalWidth || image.width,
        height: image.naturalHeight || image.height,
      });
    };
    image.onerror = reject;
    image.src = src;
  });
}

function buildOciComboPdfPayload(source) {
  const summaryData = source?.summary || {};
  const comboSummary = source?.combo_summary || [];
  const patientDetails = source?.patient_details || [];
  const almostComboPatients = source?.almost_combo_patients || [];
  const invalidCidComboPatients = source?.invalid_cid_combo_patients || [];
  const invalidAuthComboPatients = source?.invalid_auth_combo_patients || [];
  const patientsWithMultipleCombos = patientDetails.filter((patient) => Number(patient.formed_combo_count || 0) > 1);
  const resolvedUnit = source?.resolved_unit || {};
  const bpaInfo = source?.bpa_analysis || {};
  const bpaFiles = source?.bpa_analyses || bpaInfo?.input_files || [];
  return {
    summaryData,
    comboSummary,
    patientDetails,
    almostComboPatients,
    invalidCidComboPatients,
    invalidAuthComboPatients,
    patientsWithMultipleCombos,
    resolvedUnit,
    bpaInfo,
    bpaFiles,
  };
}

function formatListForExport(items, fallback = '') {
  return Array.isArray(items) && items.length ? items.join(', ') : fallback;
}

function formatProceduresForExport(detailList, mapValue) {
  const entries = procedureDisplayEntries(detailList, mapValue);
  if (!entries.length) return '';
  return entries.map((item) => formatProcedureDisplay(item)).join(', ');
}

function sanitizeFileNamePart(value, fallback = 'geral') {
  const normalized = String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9_-]+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '');
  return normalized || fallback;
}

function formatRuleMatchesForExport(items, fallback = '') {
  if (!Array.isArray(items) || !items.length) return fallback;
  return items
    .map((item) => {
      const label = String(item?.label || '').trim() || 'Regra';
      const matchedCodes = Array.isArray(item?.matched_codes) ? item.matched_codes.filter(Boolean) : [];
      return `${label}: ${matchedCodes.length ? matchedCodes.join(', ') : '-'}`;
    })
    .join(' | ');
}

function buildOciComboCsvRows(source, options = {}) {
  const payload = buildOciComboPdfPayload(source);
  const exportMode = options.exportMode || 'all';
  const fileNames = (payload.bpaFiles || []).length
    ? payload.bpaFiles.map((item) => item.file_name).filter(Boolean).join(' | ')
    : String(payload.bpaInfo?.file_name || options.fileName || '').trim();
  const competencias = formatCompetencias(payload.bpaInfo?.competencias || options.competencias || []);
  const unitName = payload.resolvedUnit?.nome_unidade || options.unitName || '';
  const unitCnes = payload.resolvedUnit?.cnes || options.unitCnes || '';
  const analysisLabel = options.analysisLabel || 'Análise atual';

  const formedRows = (payload.patientDetails || []).flatMap((patient) =>
    (patient.formed_combos || []).map((combo) => ({
      analise: analysisLabel,
      status: 'FORMADO',
      arquivo_bpa: fileNames,
      unidade: unitName,
      cnes: unitCnes,
      competencias,
      paciente_nome: patient.name || '',
      paciente_data_nascimento: patient.dob || '',
      paciente_cpf: patient.cpf || '',
      paciente_cns: patient.cns || '',
      paciente_cids: formatListForExport(patient.cids),
      combo_codigo: combo.combo_code || '',
      combo_nome: combo.combo_name || '',
      cid_esperado_regra: '',
      cid_recebido_bpa: formatListForExport(patient.cids),
      cid_compativel_encontrado: formatListForExport(combo.matched_cids),
      procedimentos_localizados: formatProceduresForExport(combo.matched_procedure_details, combo.matched_procedures),
      cbos_validados: formatListForExport(combo.matched_cbos),
      observacoes: combo.notes || '',
    }))
  );

  const invalidRows = (payload.invalidCidComboPatients || []).flatMap((patient) =>
    (patient.invalid_cid_combos || []).map((combo) => ({
      analise: analysisLabel,
      status: 'NAO_FORMADO_CID_INCOMPATIVEL',
      arquivo_bpa: fileNames,
      unidade: unitName,
      cnes: unitCnes,
      competencias,
      paciente_nome: patient.name || '',
      paciente_data_nascimento: patient.dob || '',
      paciente_cpf: patient.cpf || '',
      paciente_cns: patient.cns || '',
      paciente_cids: formatListForExport(patient.cids),
      combo_codigo: combo.combo_code || '',
      combo_nome: combo.combo_name || '',
      cid_esperado_regra: formatListForExport(combo.required_cid_prefixes),
      cid_recebido_bpa: formatListForExport(combo.patient_cids),
      cid_compativel_encontrado: formatListForExport(combo.matched_cids),
      procedimentos_localizados: formatProceduresForExport(combo.matched_procedure_details, combo.matched_procedures),
      cbos_validados: formatListForExport(combo.matched_cbos),
      observacoes: combo.notes || '',
    }))
  );

  const missingProcedureRows = (payload.almostComboPatients || []).flatMap((patient) =>
    (patient.almost_combos || []).map((combo) => ({
      analise: analysisLabel,
      status: 'NAO_FORMADO_FALTA_PROCEDIMENTO',
      arquivo_bpa: fileNames,
      unidade: unitName,
      cnes: unitCnes,
      competencias,
      paciente_nome: patient.name || '',
      paciente_data_nascimento: patient.dob || '',
      paciente_cpf: patient.cpf || '',
      paciente_cns: patient.cns || '',
      paciente_cids: '',
      combo_codigo: combo.combo_code || '',
      combo_nome: combo.combo_name || '',
      cid_esperado_regra: '',
      cid_recebido_bpa: '',
      cid_compativel_encontrado: '',
      procedimentos_localizados: formatRuleMatchesForExport(combo.matched_required, formatProceduresForExport([], patient.procedures)),
      cbos_validados: '',
      observacoes: combo.missing_required?.length
        ? `Faltando: ${combo.missing_required.join(', ')}${combo.notes ? ` | ${combo.notes}` : ''}`
        : (combo.notes || ''),
    }))
  );

  const invalidAuthRows = (payload.invalidAuthComboPatients || []).flatMap((patient) =>
    (patient.invalid_auth_combos || []).map((combo) => ({
      analise: analysisLabel,
      status: 'NAO_FORMADO_AUTORIZACAO_INVALIDA',
      arquivo_bpa: fileNames,
      unidade: unitName,
      cnes: unitCnes,
      competencias,
      paciente_nome: patient.name || '',
      paciente_data_nascimento: patient.dob || '',
      paciente_cpf: patient.cpf || '',
      paciente_cns: patient.cns || '',
      paciente_cids: formatListForExport(patient.cids),
      combo_codigo: combo.combo_code || '',
      combo_nome: combo.combo_name || '',
      cid_esperado_regra: '',
      cid_recebido_bpa: formatListForExport(combo.patient_cids),
      cid_compativel_encontrado: formatListForExport(combo.matched_cids),
      procedimentos_localizados: formatProceduresForExport(combo.matched_procedure_details, combo.matched_procedures),
      cbos_validados: formatListForExport(combo.matched_cbos),
      observacoes: `Autorização inválida: ${getValidAuths(patient.autorizacoes).length ? formatListForExport(getValidAuths(patient.autorizacoes)) : 'Nenhuma válida encontrada'}${combo.notes ? ` | ${combo.notes}` : ''}`,
    }))
  );

  if (exportMode === 'validated') return formedRows;
  if (exportMode === 'invalid_cid') return invalidRows;
  if (exportMode === 'invalid_auth') return invalidAuthRows;
  if (exportMode === 'missing_procedure') return missingProcedureRows;
  return [...formedRows, ...missingProcedureRows, ...invalidRows, ...invalidAuthRows];
}

function buildCsvContent(rows) {
  const headers = [
    'analise',
    'status',
    'arquivo_bpa',
    'unidade',
    'cnes',
    'competencias',
    'paciente_nome',
    'paciente_data_nascimento',
    'paciente_cpf',
    'paciente_cns',
    'paciente_cids',
    'combo_codigo',
    'combo_nome',
    'cid_esperado_regra',
    'cid_recebido_bpa',
    'cid_compativel_encontrado',
    'procedimentos_localizados',
    'cbos_validados',
    'observacoes',
  ];

  const formatCsvCellValue = (header, value) => {
    const normalized = String(value ?? '').trim();
    return normalized;
  };

  const escapeCell = (value) => {
    const normalized = String(value ?? '').replace(/"/g, '""');
    return `"${normalized}"`;
  };

  const lines = [
    headers.join(';'),
    ...rows.map((row) => headers.map((header) => escapeCell(formatCsvCellValue(header, row[header]))).join(';')),
  ];
  return `\ufeff${lines.join('\r\n')}`;
}

function downloadCsvContent(fileName, rows) {
  const csvContent = buildCsvContent(rows);
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const blobUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = blobUrl;
  link.setAttribute('download', fileName);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(blobUrl);
}

async function generateOciComboPdf(source, options = {}) {
  const payload = buildOciComboPdfPayload(source);
  const summaryOnly = Boolean(options.summaryOnly);
  const doc = new jsPDF('portrait', 'mm', 'a4');
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 14;
  const contentWidth = pageWidth - (margin * 2);

  let logoBase64 = null;
  let logoDimensions = null;
  try {
    logoBase64 = await loadImageAsDataUrl(logoCcdti);
    logoDimensions = await getImageDimensions(logoBase64);
  } catch (logoError) {
    console.warn('Nao foi possivel carregar a logo para o PDF do Integra OCI:', logoError);
  }

  const ensureSpace = (currentY, requiredHeight) => {
    if (currentY + requiredHeight <= pageHeight - 18) {
      return currentY;
    }
    doc.addPage();
    return drawHeader(14);
  };

  const drawHeader = (startY) => {
    let currentY = startY;

    if (logoBase64) {
      const logoWidth = 42;
      const naturalWidth = logoDimensions?.width || 1;
      const naturalHeight = logoDimensions?.height || 1;
      const logoHeight = logoWidth * (naturalHeight / naturalWidth);
      const logoX = (pageWidth - logoWidth) / 2;
      doc.addImage(logoBase64, 'PNG', logoX, currentY, logoWidth, logoHeight);
      currentY += logoHeight + 6;
    }

    doc.setFontSize(16);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(19, 51, 90);
    doc.text(summaryOnly ? 'Integra OCI | Relatorio Resumido de Validacao' : 'Integra OCI | Relatorio Detalhado de Validacao', margin, currentY + 6);

    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(90, 90, 90);
    doc.text(`Emitido em ${new Date().toLocaleString('pt-BR')}`, margin, currentY + 11);

    currentY += 16;
    doc.setDrawColor(42, 104, 143);
    doc.setLineWidth(0.5);
    doc.line(margin, currentY, pageWidth - margin, currentY);
    return currentY + 8;
  };

  const drawSectionTitle = (title, currentY) => {
    doc.setFontSize(13);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(19, 51, 90);
    doc.text(title, margin, currentY);
    return currentY + 6;
  };

  const drawWrappedText = (text, x, y, width, options = {}) => {
    const lineHeight = options.lineHeight || 4.2;
    const color = options.color || [55, 65, 81];
    const fontSize = options.fontSize || 9;
    const fontStyle = options.fontStyle || 'normal';
    const lines = doc.splitTextToSize(String(text || ''), width);
    doc.setFontSize(fontSize);
    doc.setFont(undefined, fontStyle);
    doc.setTextColor(...color);
    doc.text(lines, x, y);
    return y + (lines.length * lineHeight);
  };

  const drawLabeledBlock = (label, value, currentY, options = {}) => {
    const baseX = options.x || (margin + 4);
    const maxWidth = options.width || (contentWidth - 8);
    const labelText = `${label}: `;
    doc.setFontSize(9);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(19, 51, 90);
    doc.text(labelText, baseX, currentY);
    const labelWidth = doc.getTextWidth(labelText);
    return drawWrappedText(value, baseX + labelWidth, currentY, Math.max(maxWidth - labelWidth, 20), {
      lineHeight: options.lineHeight || 4.2,
      color: options.color || [55, 65, 81],
      fontSize: options.fontSize || 9,
      fontStyle: options.fontStyle || 'normal',
    });
  };

  const formatListForPdf = (items, fallback = 'Nao informado') => {
    return Array.isArray(items) && items.length ? items.join(', ') : fallback;
  };

  const formatRuleMatchesForPdf = (items, fallback = 'Nao informado') => {
    if (!Array.isArray(items) || !items.length) return fallback;
    return items
      .map((item) => {
        const label = String(item?.label || '').trim() || 'Regra';
        const matchedCodes = Array.isArray(item?.matched_codes) ? item.matched_codes.filter(Boolean) : [];
        return `${label}: ${matchedCodes.length ? matchedCodes.join(', ') : '-'}`;
      })
      .join(' | ');
  };

  const formatComboProceduresForPdf = (mapValue) => {
    const entries = procedureEntries(mapValue);
    if (!entries.length) return 'Nenhum procedimento consolidado.';
    return entries.map((item) => `${item.proc} (${item.qty}x)`).join(', ');
  };

  const drawPatientCard = (title, patientLines, currentY, options = {}) => {
    const titleBgColor = options.titleBgColor || [19, 51, 90];
    const bodyBgColor = options.bodyBgColor || [248, 250, 252];
    const borderColor = options.borderColor || [226, 232, 240];
    const x = margin;
    const width = contentWidth;
    const titleHeight = 8;
    const padding = 4;
    const lineHeight = 4.4;

    let contentHeight = padding;
    patientLines.forEach((line) => {
      const labelText = `${line.label}: `;
      doc.setFontSize(line.fontSize || 9);
      const labelWidth = doc.getTextWidth(labelText);
      const lines = doc.splitTextToSize(String(line.value || ''), width - (padding * 2) - labelWidth);
      contentHeight += Math.max(lines.length, 1) * lineHeight + 1;
    });
    contentHeight += 2;

    const totalHeight = titleHeight + contentHeight;
    currentY = ensureSpace(currentY, totalHeight + 4);

    doc.setDrawColor(...borderColor);
    doc.setFillColor(...bodyBgColor);
    doc.roundedRect(x, currentY, width, totalHeight, 3, 3, 'FD');

    doc.setFillColor(...titleBgColor);
    doc.roundedRect(x, currentY, width, titleHeight, 3, 3, 'F');
    doc.rect(x, currentY + titleHeight - 3, width, 3, 'F');

    doc.setFontSize(10);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(255, 255, 255);
    doc.text(title, x + padding, currentY + 5.3);

    let innerY = currentY + titleHeight + padding + 1;
    patientLines.forEach((line) => {
      innerY = drawLabeledBlock(line.label, line.value, innerY, {
        x: x + padding,
        width: width - (padding * 2),
        lineHeight,
        color: line.color || [55, 65, 81],
        fontSize: line.fontSize || 9,
      });
      innerY += 1;
    });

    return currentY + totalHeight + 4;
  };

  let currentY = drawHeader(14);

  currentY = ensureSpace(currentY, 32);
  doc.setFillColor(236, 237, 237);
  doc.roundedRect(margin, currentY, contentWidth, 24, 3, 3, 'F');
  doc.setFontSize(10);
  doc.setFont(undefined, 'bold');
  doc.setTextColor(19, 51, 90);
  doc.text('Resumo da Análise', margin + 4, currentY + 6);

  doc.setFontSize(9);
  doc.setFont(undefined, 'normal');
  doc.setTextColor(40, 40, 40);
  doc.text(`Unidade: ${payload.resolvedUnit.nome_unidade || 'Não identificada'}${payload.resolvedUnit.cnes ? ` (${payload.resolvedUnit.cnes})` : ''}`, margin + 4, currentY + 12);
  doc.text(`Competência(s): ${formatCompetencias(payload.bpaInfo.competencias)}`, margin + 4, currentY + 17);
  doc.text(`Arquivo(s) BPA: ${payload.bpaInfo.file_name || options.fileName || 'Não informado'}`, margin + 4, currentY + 22);
  if ((payload.bpaFiles || []).length > 1) {
    doc.text(`Detalhe dos arquivos: ${(payload.bpaFiles || []).map((item) => item.file_name).join(' | ')}`, margin + 4, currentY + 27);
    currentY += 5;
  }
  currentY += 30;

  currentY = drawSectionTitle('Indicadores Consolidados', currentY);
  const metrics = [
    `Quantidade de combos formados: ${payload.summaryData.combo_occurrences || 0}`,
    `Quais combos foram identificados: ${payload.comboSummary.length || 0} tipo(s)`,
    `Pacientes que formam combos: ${payload.summaryData.patients_with_combos || 0}`,
    `Ocorrencias pendentes por falta de procedimento: ${payload.summaryData.almost_combo_occurrences || 0}`,
    `Ocorrencias com CID incompatível: ${payload.summaryData.invalid_cid_combo_occurrences || 0}`,
    `Pacientes que formaram mais de um combo: ${payload.patientsWithMultipleCombos.length || 0}`,
    `Pacientes avaliados: ${payload.summaryData.total_patients_analyzed || 0}`,
  ];

  doc.setFontSize(10);
  doc.setTextColor(40, 40, 40);
  metrics.forEach((item) => {
    currentY = ensureSpace(currentY, 7);
    doc.text(`- ${item}`, margin + 2, currentY);
    currentY += 6;
  });

  currentY += 3;
  currentY = drawSectionTitle('Resumo dos Combos Identificados', currentY);

  if (!payload.comboSummary.length) {
    doc.setFontSize(10);
    doc.setTextColor(90, 90, 90);
    doc.text('Nenhum combo foi identificado nesta validacao.', margin + 2, currentY);
    currentY += 6;
  } else {
    payload.comboSummary.forEach((combo) => {
      currentY = drawPatientCard(
        `${combo.combo_code || '-'} | ${combo.combo_name || 'Combo sem descrição'}`,
        [
          {
            label: 'Pacientes com este combo',
            value: String(combo.patients_count || 0),
          },
        ],
        currentY,
        {
          titleBgColor: [19, 51, 90],
          bodyBgColor: [248, 250, 252],
          borderColor: [226, 232, 240],
        }
      );
    });
  }

  if (!summaryOnly) {
    currentY += 2;
    currentY = drawSectionTitle('Pacientes que Formaram Combos', currentY);

    if (!payload.patientDetails.length) {
      doc.setFontSize(10);
      doc.setTextColor(90, 90, 90);
      doc.text('Nenhum paciente formou combo nesta validacao.', margin + 2, currentY);
      currentY += 6;
    } else {
      payload.patientDetails.forEach((patient) => {
        currentY = drawPatientCard(
          `${patient.name || 'Paciente'} | Nasc. ${formatPatientDob(patient.dob)}`,
          [
            ...((patient.cpf || patient.cns)
              ? [{
                  label: 'Identificadores do paciente',
                  value: [patient.cpf ? `CPF ${patient.cpf}` : null, patient.cns ? `CNS ${patient.cns}` : null].filter(Boolean).join(' | '),
                }]
              : []),
            {
              label: 'Total de combos formados',
              value: String(patient.formed_combo_count || 0),
            },
            {
        label: getOciCidSourceLabel(patient.cid_sources),
        value: formatListForPdf(patient.cids, getOciCidMissingLabel(patient.cid_sources)),
            },
            {
              label: 'CBOs identificados',
              value: formatListForPdf(patient.cbos, 'Nenhum CBO identificado'),
            },
            {
              label: 'Competencias',
              value: formatListForPdf(patient.competencias, 'Nao identificada'),
            },
            {
              label: 'Datas de atendimento',
              value: formatListForPdf(patient.service_dates, 'Nao informadas'),
            },
            {
              label: 'Procedimentos do paciente',
              value: formatComboProceduresForPdf(patient.procedures),
            },
            {
              label: 'Combos formados',
              value: (patient.formed_combos || [])
                .map((combo) => `${combo.combo_code} - ${combo.combo_name}`)
                .join(' | '),
            },
          ],
          currentY,
          {
            titleBgColor: [42, 104, 143],
            bodyBgColor: [236, 237, 237],
            borderColor: [203, 213, 225],
          }
        );

        (patient.formed_combos || []).forEach((combo) => {
          currentY = drawPatientCard(
            `Detalhe do combo ${combo.combo_code || '-'} | ${combo.combo_name || 'Sem descrição'}`,
            [
              {
                label: 'Procedimentos que sustentaram o combo',
                value: formatComboProceduresForPdf(combo.matched_procedures),
              },
              {
                label: 'CIDs validados no combo',
                value: formatListForPdf(combo.matched_cids, 'Nao se aplica ou nao informado'),
              },
              {
                label: 'CBOs validados no combo',
                value: formatListForPdf(combo.matched_cbos, 'Nao se aplica ou nao informado'),
              },
              {
                label: 'Regra de CID/CBO de origem',
                value: combo.context_source_combo_code || combo.context_source_combo_name
                  ? `${combo.context_source_combo_code || combo.combo_code}${combo.context_source_combo_name ? ` - ${combo.context_source_combo_name}` : ''}`
                  : 'Nao aplicavel',
              },
              {
                label: 'Observacoes',
                value: combo.notes || 'Sem observacoes adicionais.',
              },
            ],
            currentY,
            {
              titleBgColor: [19, 51, 90],
              bodyBgColor: [255, 255, 255],
              borderColor: [226, 232, 240],
            }
          );
        });
      });
    }
  }

  currentY += 2;
  currentY = drawSectionTitle(summaryOnly ? 'Resumo das Pendencias por Falta de Procedimento' : 'Pendencias por Falta de Procedimento', currentY);

  if (!payload.almostComboPatients.length) {
    doc.setFontSize(10);
    doc.setTextColor(90, 90, 90);
    doc.text('Nenhum paciente ficou pendente apenas por falta de procedimento nesta análise.', margin + 2, currentY);
    currentY += 6;
  } else if (summaryOnly) {
    const missingProcedureMetrics = [
      `Combos pendentes por falta de procedimento: ${payload.summaryData.almost_combo_occurrences || 0}`,
      `Pacientes com pendencia por procedimento: ${payload.summaryData.patients_almost_with_combos || 0}`,
    ];

    doc.setFontSize(10);
    doc.setTextColor(40, 40, 40);
    missingProcedureMetrics.forEach((item) => {
      currentY = ensureSpace(currentY, 7);
      doc.text(`- ${item}`, margin + 2, currentY);
      currentY += 6;
    });
  } else {
    payload.almostComboPatients.forEach((patient) => {
      currentY = drawPatientCard(
        `${patient.name || 'Paciente'} | Nasc. ${formatPatientDob(patient.dob)} | ${patient.almost_combo_count || 0} pendencia(s)`,
        [
          ...(formatMaskedPatientIdentifiers(patient)
            ? [{
                label: 'Identificadores mascarados',
                value: formatMaskedPatientIdentifiers(patient),
              }]
            : []),
          {
            label: 'Total de pendencias por procedimento',
            value: String(patient.almost_combo_count || 0),
          },
          {
            label: 'Procedimentos consolidados do paciente',
            value: formatComboProceduresForPdf(patient.procedures),
          },
        ],
        currentY,
        {
          titleBgColor: [2, 132, 199],
          bodyBgColor: [240, 249, 255],
          borderColor: [186, 230, 253],
        }
      );

      (patient.almost_combos || []).forEach((combo) => {
        currentY = drawPatientCard(
          `Pendencia no combo ${combo.combo_code || '-'} | ${combo.combo_name || 'Sem descrição'}`,
          [
            {
              label: 'Obrigatorios localizados',
              value: formatRuleMatchesForPdf(combo.matched_required, 'Nenhum procedimento obrigatório localizado'),
            },
            {
              label: 'Obrigatorios faltantes',
              value: formatListForPdf(combo.missing_required, 'Nenhuma pendencia identificada'),
            },
            {
              label: 'Progresso da regra',
              value: `${combo.matched_required_count || 0} de ${combo.required_count || 0} obrigatorios encontrados`,
            },
            {
              label: 'Observacoes',
              value: combo.notes || 'Sem observacoes adicionais.',
            },
          ],
          currentY,
          {
            titleBgColor: [3, 105, 161],
            bodyBgColor: [255, 255, 255],
            borderColor: [186, 230, 253],
          }
        );
      });
    });
  }

  currentY += 2;
  currentY = drawSectionTitle(summaryOnly ? 'Resumo dos Combos Não Formados por CID' : 'Combos com CID Incompatível', currentY);

  if (!payload.invalidCidComboPatients.length) {
    doc.setFontSize(10);
    doc.setTextColor(90, 90, 90);
    doc.text('Nenhum paciente fechou procedimentos de combo com CID incompatível nesta análise.', margin + 2, currentY);
    currentY += 6;
  } else if (summaryOnly) {
    const invalidCidMetrics = [
      `Combos não validados por CID incorreto: ${payload.summaryData.invalid_cid_combo_occurrences || 0}`,
      `Pacientes barrados por CID incorreto: ${payload.summaryData.patients_with_invalid_cid_combos || 0}`,
    ];

    doc.setFontSize(10);
    doc.setTextColor(40, 40, 40);
    invalidCidMetrics.forEach((item) => {
      currentY = ensureSpace(currentY, 7);
      doc.text(`- ${item}`, margin + 2, currentY);
      currentY += 6;
    });
  } else {
    payload.invalidCidComboPatients.forEach((patient) => {
      currentY = drawPatientCard(
        `${patient.name || 'Paciente'} | Nasc. ${formatPatientDob(patient.dob)} | ${patient.invalid_cid_combo_count || 0} inconsistencia(s)`,
        [
          ...(formatMaskedPatientIdentifiers(patient)
            ? [{
                label: 'Identificadores do paciente',
                value: [patient.cpf ? `CPF ${patient.cpf}` : null, patient.cns ? `CNS ${patient.cns}` : null].filter(Boolean).join(' | '),
              }]
            : []),
          {
      label: getOciCidSourceLabel(patient.cid_sources),
      value: formatListForPdf(patient.cids, getOciCidMissingLabel(patient.cid_sources)),
            color: [153, 27, 27],
          },
          {
            label: 'CBOs identificados',
            value: formatListForPdf(patient.cbos, 'Nenhum CBO identificado'),
          },
          {
            label: 'Competencias',
            value: formatListForPdf(patient.competencias, 'Nao identificada'),
          },
          {
            label: 'Datas de atendimento',
            value: formatListForPdf(patient.service_dates, 'Nao informadas'),
          },
          {
            label: 'Procedimentos do paciente',
            value: formatComboProceduresForPdf(patient.procedures),
          },
        ],
        currentY,
        {
          titleBgColor: [153, 27, 27],
          bodyBgColor: [254, 242, 242],
          borderColor: [254, 202, 202],
        }
      );

      (patient.invalid_cid_combos || []).forEach((combo) => {
        currentY = drawPatientCard(
          `CID incorreto no combo ${combo.combo_code || '-'} | ${combo.combo_name || 'Sem descrição'}`,
          [
            {
              label: 'Procedimentos que fecharam o combo',
              value: formatComboProceduresForPdf(combo.matched_procedures),
            },
            {
        label: getOciCidSourceLabel(combo.patient_cid_sources),
        value: formatListForPdf(combo.patient_cids, getOciCidMissingLabel(combo.patient_cid_sources)),
              color: [153, 27, 27],
            },
            {
              label: 'CID esperado pela regra',
              value: formatListForPdf(combo.required_cid_prefixes, 'Regra sem CID esperado definido'),
              color: [19, 51, 90],
            },
            {
              label: 'CIDs que coincidiram',
              value: formatListForPdf(combo.matched_cids, 'Nenhum CID compativel encontrado'),
            },
            {
              label: 'CBOs validados',
              value: formatListForPdf(combo.matched_cbos, 'Nenhum CBO compativel encontrado'),
            },
            {
              label: 'Regra de origem',
              value: combo.context_source_combo_code || combo.context_source_combo_name
                ? `${combo.context_source_combo_code || combo.combo_code}${combo.context_source_combo_name ? ` - ${combo.context_source_combo_name}` : ''}`
                : 'Nao informada',
            },
            {
              label: 'Observacoes',
              value: combo.notes || 'Sem observacoes adicionais.',
            },
          ],
          currentY,
          {
            titleBgColor: [127, 29, 29],
            bodyBgColor: [255, 255, 255],
            borderColor: [254, 202, 202],
          }
        );
      });
    });
  }

  if (!summaryOnly) {
    currentY += 2;
    currentY = drawSectionTitle('Pacientes com Mais de Um Combo', currentY);
    if (!payload.patientsWithMultipleCombos.length) {
      doc.setFontSize(10);
      doc.setTextColor(90, 90, 90);
      doc.text('Nenhum paciente formou mais de um combo nesta análise.', margin + 2, currentY);
      currentY += 6;
    } else {
      payload.patientsWithMultipleCombos.forEach((patient) => {
        currentY = drawPatientCard(
          `${patient.name || 'Paciente'} | Nasc. ${formatPatientDob(patient.dob)}`,
          [
            ...((patient.cpf || patient.cns)
              ? [{
                  label: 'Identificadores do paciente',
                  value: [patient.cpf ? `CPF ${patient.cpf}` : null, patient.cns ? `CNS ${patient.cns}` : null].filter(Boolean).join(' | '),
                }]
              : []),
            {
              label: 'Quantidade de combos',
              value: String(patient.formed_combo_count || 0),
            },
            {
              label: 'Combos do paciente',
              value: (patient.formed_combos || [])
                .map((combo) => `${combo.combo_code} - ${combo.combo_name}`)
                .join(' | '),
            },
          ],
          currentY,
          {
            titleBgColor: [42, 104, 143],
            bodyBgColor: [248, 250, 252],
            borderColor: [203, 213, 225],
          }
        );
      });
    }
  }

  const totalPages = doc.internal.getNumberOfPages();
  for (let page = 1; page <= totalPages; page += 1) {
    doc.setPage(page);
    doc.setDrawColor(180, 180, 180);
    doc.line(margin, pageHeight - 12, pageWidth - margin, pageHeight - 12);
    doc.setFontSize(8);
    doc.setTextColor(90, 90, 90);
    doc.text(`Página ${page} de ${totalPages}`, pageWidth - margin, pageHeight - 7, { align: 'right' });
  }

  const fileSuffix = (options.fileSuffix || payload.resolvedUnit.cnes || 'geral').replace(/\s+/g, '_');
  doc.save(`${summaryOnly ? 'integra_oci_validacao_resumida' : 'integra_oci_validacao_detalhada'}_${fileSuffix}.pdf`);
}

async function exportOciComboPdf() {
  if (!ociComboResult.value) return;

  isExportingOciComboPdf.value = true;
  try {
    await generateOciComboPdf(
      {
        bpa_analysis: ociComboBpaAnalysis.value,
        bpa_analyses: ociComboBpaAnalyses.value,
        resolved_unit: ociComboResolvedUnit.value,
        summary: ociComboResult.value.summary,
        combo_summary: ociComboResult.value.combo_summary,
        patient_details: ociComboResult.value.patient_details,
        almost_combo_patients: ociComboResult.value.almost_combo_patients,
        invalid_cid_combo_patients: ociComboResult.value.invalid_cid_combo_patients,
        invalid_auth_combo_patients: ociComboResult.value.invalid_auth_combo_patients,
      },
      {
        fileName: ociComboBpaAnalysis.value?.file_name,
        fileSuffix: ociComboResolvedUnit.value?.cnes || 'geral',
      }
    );
  } catch (error) {
    console.error('Erro ao exportar PDF da validacao Integra OCI:', error);
    ociComboErrorMsg.value = 'Nao foi possivel exportar o PDF detalhado da validacao.';
  } finally {
    isExportingOciComboPdf.value = false;
  }
}

async function exportOciComboSummaryPdf() {
  if (!ociComboResult.value) return;

  isExportingOciComboSummaryPdf.value = true;
  try {
    await generateOciComboPdf(
      {
        bpa_analysis: ociComboBpaAnalysis.value,
        bpa_analyses: ociComboBpaAnalyses.value,
        resolved_unit: ociComboResolvedUnit.value,
        summary: ociComboResult.value.summary,
        combo_summary: ociComboResult.value.combo_summary,
        patient_details: ociComboResult.value.patient_details,
        almost_combo_patients: ociComboResult.value.almost_combo_patients,
        invalid_cid_combo_patients: ociComboResult.value.invalid_cid_combo_patients,
        invalid_auth_combo_patients: ociComboResult.value.invalid_auth_combo_patients,
      },
      {
        fileName: ociComboBpaAnalysis.value?.file_name,
        fileSuffix: ociComboResolvedUnit.value?.cnes || 'geral',
        summaryOnly: true,
      }
    );
  } catch (error) {
    console.error('Erro ao exportar PDF resumido da validacao Integra OCI:', error);
    ociComboErrorMsg.value = 'Nao foi possivel exportar o PDF resumido da validacao.';
  } finally {
    isExportingOciComboSummaryPdf.value = false;
  }
}

async function exportOciComboCsv() {
  if (!ociComboResult.value) return;

  isExportingOciComboCsv.value = true;
  try {
    const rows = buildOciComboCsvRows(
      {
        bpa_analysis: ociComboBpaAnalysis.value,
        bpa_analyses: ociComboBpaAnalyses.value,
        resolved_unit: ociComboResolvedUnit.value,
        summary: ociComboResult.value.summary,
        combo_summary: ociComboResult.value.combo_summary,
        patient_details: ociComboResult.value.patient_details,
        almost_combo_patients: ociComboResult.value.almost_combo_patients,
        invalid_cid_combo_patients: ociComboResult.value.invalid_cid_combo_patients,
        invalid_auth_combo_patients: ociComboResult.value.invalid_auth_combo_patients,
      },
      {
        exportMode: ociExportMode.value,
        analysisLabel: 'Análise atual',
      }
    );

    if (!rows.length) {
      ociComboErrorMsg.value = ociExportMode.value === 'invalid_cid'
        ? 'Nao ha combos nao formados por CID incompatível para exportar nesta analise.'
        : ociExportMode.value === 'invalid_auth'
          ? 'Nao ha combos nao formados por autorização inválida para exportar nesta analise.'
          : ociExportMode.value === 'missing_procedure'
            ? 'Nao ha combos nao formados por falta de procedimento para exportar nesta analise.'
            : ociExportMode.value === 'validated'
              ? 'Nao ha combos validados para exportar nesta analise.'
              : 'Nao ha dados da validacao para exportar nesta analise.';
      return;
    }

    const unitSuffix = sanitizeFileNamePart(ociComboResolvedUnit.value?.nome_unidade || ociComboResolvedUnit.value?.cnes, 'geral');
    const fileName = ociExportMode.value === 'invalid_cid'
      ? `integra_oci_cid_incompativel_${unitSuffix}.csv`
      : ociExportMode.value === 'invalid_auth'
        ? `integra_oci_autorizacao_invalida_${unitSuffix}.csv`
        : ociExportMode.value === 'missing_procedure'
          ? `integra_oci_falta_procedimento_${unitSuffix}.csv`
          : ociExportMode.value === 'validated'
            ? `integra_oci_validados_${unitSuffix}.csv`
            : `integra_oci_validacao_${unitSuffix}.csv`;
    downloadCsvContent(fileName, rows);
  } catch (error) {
    console.error('Erro ao exportar CSV da validacao Integra OCI:', error);
    ociComboErrorMsg.value = 'Nao foi possivel exportar o CSV da validacao.';
  } finally {
    isExportingOciComboCsv.value = false;
  }
}

function isExportingDetailedHistoryPdf(historyId) {
  return exportingOciHistoryState.value.id === historyId && exportingOciHistoryState.value.mode === 'detailed';
}

function isExportingSummaryHistoryPdf(historyId) {
  return exportingOciHistoryState.value.id === historyId && exportingOciHistoryState.value.mode === 'summary';
}

function isExportingHistoryCsv(historyId) {
  return exportingOciHistoryState.value.id === historyId && exportingOciHistoryState.value.mode === 'csv';
}

async function downloadOciHistoryAnalysis(item) {
  exportingOciHistoryState.value = { id: item.id, mode: 'detailed' };
  try {
    const response = await api.get(`/api/v1/bpa-apac/oci-combos/history/${item.id}/details/?export_type=pdf_detailed`);
    if (response.data?.error) {
      throw new Error(response.data.error);
    }
    await generateOciComboPdf(response.data, {
      fileName: item.bpa_filename,
      fileSuffix: item.unit_cnes || `historico_${item.id}`,
    });
  } catch (error) {
    console.error('Erro ao baixar PDF do historico Integra OCI:', error);
    ociComboErrorMsg.value = 'Nao foi possivel baixar o PDF detalhado desta validacao do historico.';
  } finally {
    exportingOciHistoryState.value = { id: null, mode: null };
  }
}

async function downloadOciHistorySummaryAnalysis(item) {
  exportingOciHistoryState.value = { id: item.id, mode: 'summary' };
  try {
    const response = await api.get(`/api/v1/bpa-apac/oci-combos/history/${item.id}/details/?export_type=pdf_summary`);
    if (response.data?.error) {
      throw new Error(response.data.error);
    }
    await generateOciComboPdf(response.data, {
      fileName: item.bpa_filename,
      fileSuffix: item.unit_cnes || `historico_${item.id}`,
      summaryOnly: true,
    });
  } catch (error) {
    console.error('Erro ao baixar PDF resumido do historico Integra OCI:', error);
    ociComboErrorMsg.value = 'Nao foi possivel baixar o PDF resumido desta validacao do historico.';
  } finally {
    exportingOciHistoryState.value = { id: null, mode: null };
  }
}

async function downloadOciHistoryCsv(item) {
  exportingOciHistoryState.value = { id: item.id, mode: 'csv' };
  try {
    const response = await api.get(`/api/v1/bpa-apac/oci-combos/history/${item.id}/details/?export_type=csv`);
    if (response.data?.error) {
      throw new Error(response.data.error);
    }

    const rows = buildOciComboCsvRows(response.data, {
      exportMode: ociExportMode.value,
      analysisLabel: `Histórico ${item.id}`,
      fileName: item.bpa_filename,
      competencias: item.competencias,
      unitName: item.unit_name,
      unitCnes: item.unit_cnes,
    });

    if (!rows.length) {
      ociComboErrorMsg.value = ociExportMode.value === 'invalid_cid'
        ? 'Este histórico não possui combos não formados por CID incompatível para exportar.'
        : ociExportMode.value === 'invalid_auth'
          ? 'Este histórico não possui combos não formados por autorização inválida para exportar.'
          : ociExportMode.value === 'missing_procedure'
            ? 'Este histórico não possui combos não formados por falta de procedimento para exportar.'
            : ociExportMode.value === 'validated'
              ? 'Este histórico não possui combos validados para exportar.'
              : 'Este historico nao possui dados da validacao para exportar.';
      return;
    }

    const unitSuffix = sanitizeFileNamePart(item.unit_name || item.unit_cnes, `historico_${item.id}`);
    const fileName = ociExportMode.value === 'invalid_cid'
      ? `historico_integra_oci_cid_incompativel_${unitSuffix}.csv`
      : ociExportMode.value === 'invalid_auth'
        ? `historico_integra_oci_autorizacao_invalida_${unitSuffix}.csv`
        : ociExportMode.value === 'missing_procedure'
          ? `historico_integra_oci_falta_procedimento_${unitSuffix}.csv`
          : ociExportMode.value === 'validated'
            ? `historico_integra_oci_validados_${unitSuffix}.csv`
            : `historico_integra_oci_validacao_${unitSuffix}.csv`;
    downloadCsvContent(fileName, rows);
  } catch (error) {
    console.error('Erro ao baixar CSV do historico Integra OCI:', error);
    ociComboErrorMsg.value = 'Nao foi possivel baixar o CSV desta validacao do historico.';
  } finally {
    exportingOciHistoryState.value = { id: null, mode: null };
  }
}

async function handleHistoryDownload(type) {
  const item = selectedOciHistoryItem.value;
  if (!item) return;
  showOciHistoryDownloadModal.value = false;
  if (type === 'csv') await downloadOciHistoryCsv(item);
  else if (type === 'pdf_summary') await downloadOciHistorySummaryAnalysis(item);
  else if (type === 'pdf_detailed') await downloadOciHistoryAnalysis(item);
}

async function downloadGeneratedFileById(fileId, fileName = 'BPA_tratado.txt', kind = 'treated') {
  if (!fileId) return;

  const url = `/api/v1/bpa-apac/download/${fileId}/?filename=${encodeURIComponent(fileName || 'BPA_tratado.txt')}&kind=${encodeURIComponent(kind)}`;
  const response = await api.get(url, { responseType: 'blob' });
  const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = blobUrl;
  link.setAttribute('download', fileName || 'BPA_tratado.txt');
  document.body.appendChild(link);
  link.click();
  window.URL.revokeObjectURL(blobUrl);
  document.body.removeChild(link);
}

async function downloadGeneratedFile() {
  if (!lastGeneratedFileId.value) return;

  try {
    await downloadGeneratedFileById(lastGeneratedFileId.value, lastGeneratedFileName.value || 'BPA_tratado.txt');
  } catch (error) {
    console.error('Erro ao baixar arquivo:', error);
    errorMsg.value = 'Erro ao tentar baixar o arquivo. Tente novamente.';
  }
}

async function downloadRemovedOnlyFile() {
  if (!lastRemovedOnlyFileId.value) return;

  try {
    const kind = String(lastRemovedOnlyFileId.value).match(/^\d+$/) ? 'removed' : 'treated';
    await downloadGeneratedFileById(
      lastRemovedOnlyFileId.value,
      lastRemovedOnlyFileName.value || 'BPA_removidos.txt',
      kind,
    );
  } catch (error) {
    console.error('Erro ao baixar BPA removidos:', error);
    errorMsg.value = 'Erro ao tentar baixar o BPA de procedimentos removidos. Tente novamente.';
  }
}

function buildAnalysisSummary(analysis) {
  if (!analysis) return [];
  const fileCount = Number(analysis.file_count || 0);
  const unitsLabel = getAnalysisSummaryUnitsLabel(analysis);
  return [
    ...(fileCount > 1 ? [{ label: 'Arquivos BPA', value: fileCount }] : []),
    { label: unitsLabel, value: formatAnalysisUnitsSummary(analysis) },
    { label: 'Competência', value: formatCompetencias(analysis.competencias) },
    { label: 'Registros lidos', value: analysis.total_registros ?? 0 },
    {
      label: analysis.kind === 'apac' ? 'Volume analisado' : 'Produção analisada',
      value: analysis.kind === 'apac'
        ? `${analysis.total_apacs ?? 0} APAC(s) | ${analysis.apac_oci_count ?? 0} OCI`
        : `${analysis.total_procedimentos ?? 0} procedimento(s) | ${analysis.total_quantidade ?? 0} qtd.`,
    },
  ];
}

function getAnalysisUnitsList(analysis) {
  const units = Array.isArray(analysis?.cnes_summary?.units)
    ? analysis.cnes_summary.units
    : analysis?.cnes_summary?.primary_unit
      ? [analysis.cnes_summary.primary_unit]
      : [];
  return units.filter(Boolean);
}

function formatUnitWithCnes(unit) {
  const name = String(unit?.nome_unidade || 'Unidade não identificada').trim();
  const cnes = String(unit?.cnes || '').trim();
  return cnes ? `${name} (CNES ${cnes})` : name;
}

function formatAnalysisUnitsSummary(analysis, maxUnits = 2) {
  const units = getAnalysisUnitsList(analysis);
  if (!units.length) return 'Não identificada';
  const visibleUnits = units.slice(0, maxUnits).map(formatUnitWithCnes);
  const remaining = units.length - visibleUnits.length;
  return remaining > 0 ? `${visibleUnits.join(' | ')} | +${remaining} unidade(s)` : visibleUnits.join(' | ');
}

function getAnalysisSummaryUnitsLabel(analysis) {
  return getAnalysisUnitsList(analysis).length > 1 ? 'Unidades identificadas' : 'Unidade identificada';
}

function describeOciPatientSources(patient) {
  const sources = Array.isArray(patient?.sources) ? patient.sources : [];
  const hasSheet = sources.includes('PLANILHA_PROCEDIMENTOS') || sources.includes('PLANILHA_CCE');
  const hasBpa = sources.includes('BPA');
  if (hasSheet && hasBpa) return 'BPAs e planilha complementar';
  if (hasSheet) return 'Planilha complementar';
  return 'BPAs';
}

function normalizeOciCidSources(cidSources) {
  const sources = Array.isArray(cidSources) ? cidSources : [];
  return {
    hasBpa: sources.includes('BPA'),
    hasSheet: sources.includes('PLANILHA_PROCEDIMENTOS') || sources.includes('PLANILHA_CCE'),
  };
}

function getOciCidSourceLabel(cidSources) {
  const { hasBpa, hasSheet } = normalizeOciCidSources(cidSources);
  if (hasBpa && hasSheet) return 'CIDs identificados no BPA e na planilha complementar';
  if (hasSheet) return 'CIDs identificados na planilha complementar';
  if (hasBpa) return 'CIDs informados no BPA';
  return 'CIDs identificados nas fontes analisadas';
}

function getOciCidMissingLabel(cidSources) {
  const { hasBpa, hasSheet } = normalizeOciCidSources(cidSources);
  if (hasBpa && hasSheet) return 'Nenhum CID identificado no BPA ou na planilha complementar.';
  if (hasSheet) return 'Nenhum CID identificado na planilha complementar.';
  if (hasBpa) return 'Nenhum CID informado para este paciente no BPA.';
  return 'Nenhum CID identificado nas fontes analisadas.';
}

function getOciPatientBpaFiles(patient) {
  const sourceOrigins = patient?.source_origins || {};
  return Array.isArray(sourceOrigins.BPA) ? sourceOrigins.BPA : [];
}

function getOciPatientSupplementalFiles(patient) {
  const sourceOrigins = patient?.source_origins || {};
  if (Array.isArray(sourceOrigins.PLANILHA_PROCEDIMENTOS)) return sourceOrigins.PLANILHA_PROCEDIMENTOS;
  if (Array.isArray(sourceOrigins.PLANILHA_CCE)) return sourceOrigins.PLANILHA_CCE;
  return [];
}

function describeOciPatientOriginSummary(patient) {
  const bpaFiles = getOciPatientBpaFiles(patient);
  const supplementalFiles = getOciPatientSupplementalFiles(patient);
  const parts = [];
  if (bpaFiles.length) {
    parts.push(`${bpaFiles.length} BPA${bpaFiles.length > 1 ? 's' : ''}`);
  }
  if (supplementalFiles.length) {
    parts.push(`${supplementalFiles.length} planilha${supplementalFiles.length > 1 ? 's' : ''} complementar${supplementalFiles.length > 1 ? 'es' : ''}`);
  }
  return parts.length ? parts.join(' + ') : 'Origem detalhada não disponível';
}

function getSupplementalSheetFileNames(summary) {
  if (Array.isArray(summary?.supplemental_sheet_file_names) && summary.supplemental_sheet_file_names.length) {
    return summary.supplemental_sheet_file_names.filter(Boolean);
  }
  const singleName = String(summary?.supplemental_sheet_file_name || '').trim();
  return singleName ? [singleName] : [];
}

function formatSupplementalSheetSummary(summary) {
  const fileNames = getSupplementalSheetFileNames(summary);
  const fileCount = Number(summary?.supplemental_sheet_file_count || fileNames.length || 0);
  if (!fileCount) return '';
  if (fileCount === 1) {
    return `Planilha complementar aplicada: ${fileNames[0] || '1 arquivo'}`;
  }
  return `Planilhas complementares aplicadas: ${fileNames.join(', ') || `${fileCount} arquivos`}`;
}

function getOciSelectedBpaFileMeta(file) {
  return (ociComboBpaAnalyses.value || []).find((analysis) => analysis?.file_name === file?.name) || null;
}

function clearProgressTimer(kind) {
  if (kind === 'processing' && processingProgressTimer) {
    clearInterval(processingProgressTimer);
    processingProgressTimer = null;
  }
  if (kind === 'oci' && ociComboProgressTimer) {
    clearInterval(ociComboProgressTimer);
    ociComboProgressTimer = null;
  }
}

function startProgressTimer(kind) {
  clearProgressTimer(kind);
  const progressRef = kind === 'processing' ? processingProgress : ociComboProgress;
  const labelRef = kind === 'processing' ? processingProgressLabel : ociComboProgressLabel;
  const preparingLabel = 'Preparando processamento...';
  const uploadingLabel = 'Enviando arquivos...';
  const waitingLabel = 'Processando dados...';

  progressRef.value = Math.max(progressRef.value, 8);
  labelRef.value = progressRef.value < 18 ? preparingLabel : uploadingLabel;

  const timer = setInterval(() => {
    if (progressRef.value < 18) {
      progressRef.value += 2;
      labelRef.value = preparingLabel;
      return;
    }
    if (progressRef.value < 45) {
      progressRef.value += 3;
      labelRef.value = uploadingLabel;
      return;
    }
    if (progressRef.value < 92) {
      progressRef.value += progressRef.value < 70 ? 2 : 1;
      labelRef.value = waitingLabel;
    }
  }, 700);

  if (kind === 'processing') {
    processingProgressTimer = timer;
  } else {
    ociComboProgressTimer = timer;
  }
}

function handleUploadProgress(kind, event) {
  if (!event?.total) return;

  const progressRef = kind === 'processing' ? processingProgress : ociComboProgress;
  const labelRef = kind === 'processing' ? processingProgressLabel : ociComboProgressLabel;
  const uploadPercent = Math.min(55, Math.max(12, Math.round((event.loaded / event.total) * 45) + 10));

  progressRef.value = Math.max(progressRef.value, uploadPercent);
  labelRef.value = uploadPercent >= 50 ? 'Processando dados...' : 'Enviando arquivos...';
}

function isOciAuthInvalid(auth) {
  let s = String(auth ?? '').trim();
  s = s.replace(/^0+/, '');
  return s.length !== 9;
}

function getValidAuths(auths) {
  return (auths || []).filter(a => !isOciAuthInvalid(a));
}

function completeProgress(kind, success = true) {
  clearProgressTimer(kind);
  const progressRef = kind === 'processing' ? processingProgress : ociComboProgress;
  const labelRef = kind === 'processing' ? processingProgressLabel : ociComboProgressLabel;
  progressRef.value = success ? 100 : Math.max(progressRef.value, 100);
  labelRef.value = success ? 'Finalizando...' : 'Não foi possível concluir.';
}

function resetProgress(kind) {
  clearProgressTimer(kind);
  if (kind === 'processing') {
    processingProgress.value = 0;
    processingProgressLabel.value = 'Preparando processamento...';
    return;
  }
  ociComboProgress.value = 0;
  ociComboProgressLabel.value = 'Preparando processamento...';
}

function formatOciCurrentInputFileMeta(fileInfo) {
  const unitName =
    fileInfo?.unit_name ||
    fileInfo?.cnes_summary?.primary_unit?.nome_unidade ||
    'Unidade não identificada';
  const unitCnes =
    fileInfo?.unit_cnes ||
    fileInfo?.cnes_summary?.primary_unit?.cnes ||
    '';
  const competencias = formatCompetencias(fileInfo?.competencias || []);
  return `${unitName}${unitCnes ? ` | CNES ${unitCnes}` : ''} | Competência ${competencias}`;
}

function formatOciSelectedBpaFileMeta(fileInfo) {
  return formatOciCurrentInputFileMeta(fileInfo);
}

function buildOciComboBpaAnalysisSummary(analyses) {
  const normalizedAnalyses = Array.isArray(analyses) ? analyses.filter(Boolean) : [];
  if (!normalizedAnalyses.length) return null;
  if (normalizedAnalyses.length === 1) {
    return {
      ...normalizedAnalyses[0],
      file_count: 1,
    };
  }

  const competencias = [...new Set(normalizedAnalyses.flatMap((item) => item.competencias || []).filter(Boolean))];
  const unitsMap = new Map();
  normalizedAnalyses.forEach((item) => {
    const units = item.cnes_summary?.units || [];
    units.forEach((unit) => {
      const cnes = String(unit?.cnes || '').trim();
      if (!cnes) return;
      const current = unitsMap.get(cnes) || {
        cnes,
        nome_unidade: unit?.nome_unidade || 'Unidade não identificada',
        count: 0,
      };
      current.count += Number(unit?.count || 0);
      unitsMap.set(cnes, current);
    });
  });
  const units = [...unitsMap.values()].sort((a, b) => Number(b.count || 0) - Number(a.count || 0));

  return {
    kind: 'bpa',
    file_name: `${normalizedAnalyses.length} arquivos BPA`,
    detected_format: 'Multiplos arquivos',
    file_count: normalizedAnalyses.length,
    competencias,
    total_registros: normalizedAnalyses.reduce((sum, item) => sum + Number(item.total_registros || 0), 0),
    total_procedimentos: normalizedAnalyses.reduce((sum, item) => sum + Number(item.total_procedimentos || 0), 0),
    total_quantidade: normalizedAnalyses.reduce((sum, item) => sum + Number(item.total_quantidade || 0), 0),
    cnes_summary: {
      primary_unit: units.length === 1 ? units[0] : null,
      units,
    },
  };
}

function formatProcedureMap(mapValue) {
  const entries = procedureEntries(mapValue);
  if (!entries.length) return 'Sem procedimento correspondente.';
  return entries.map((item) => `${item.proc} (${item.qty}x)`).join(', ');
}

function formatComboRequiredCbos(items) {
  return Array.isArray(items) && items.length ? items.join(', ') : 'Nao se aplica';
}

function formatComboMatchedCbos(items, requiredItems = []) {
  if (Array.isArray(items) && items.length) return items.join(', ');
  return Array.isArray(requiredItems) && requiredItems.length ? 'Nenhum CBO compativel encontrado' : 'Nao se aplica';
}

function getOciExportModeLabel(mode) {
  if (mode === 'validated') return 'Somente combos validados';
  if (mode === 'invalid_cid') return 'Somente CID incompatível';
  if (mode === 'invalid_auth') return 'Somente autorização inválida';
  return 'Todos os resultados';
}

function triggerApacInput() {
  apacInputRef.value?.click();
}

function triggerBpaInput() {
  bpaInputRef.value?.click();
}

function triggerOciComboBpaInput() {
  ociComboBpaInputRef.value?.click();
}

function triggerOciComboProceduresInput() {
  ociComboProceduresInputRef.value?.click();
}

function openOciExportModal() {
  showOciExportModal.value = true;
}

function closeOciExportModal() {
  showOciExportModal.value = false;
}

async function handleOciExportAction(action) {
  if (action === 'csv') {
    await exportOciComboCsv();
    closeOciExportModal();
    return;
  }
  if (action === 'summary_pdf') {
    await exportOciComboSummaryPdf();
    closeOciExportModal();
    return;
  }
  if (action === 'detailed_pdf') {
    await exportOciComboPdf();
    closeOciExportModal();
  }
}

function formatProcedureDisplay(item) {
  const code = item?.code || '-';
  const qty = Number(item?.qty || 0);
  const name = String(item?.name || '').trim();
  return name ? `${code} - ${name} (${qty}x)` : `${code} (${qty}x)`;
}

function formatProcedureCodeWithName(code, name) {
  const normalizedCode = String(code || '').trim();
  const normalizedName = String(name || '').trim();
  if (!normalizedCode) return '-';
  return normalizedName ? `${normalizedCode} - ${normalizedName}` : normalizedCode;
}

function goToPreviousOciComboDetailsPage() {
  if (ociComboDetailsPage.value > 1) {
    ociComboDetailsPage.value -= 1;
    scrollOciPaginationToTop(ociComboDetailsSectionRef, ociComboDetailsListRef);
  }
}

function goToNextOciComboDetailsPage() {
  if (ociComboDetailsPage.value < ociComboDetailsTotalPages.value) {
    ociComboDetailsPage.value += 1;
    scrollOciPaginationToTop(ociComboDetailsSectionRef, ociComboDetailsListRef);
  }
}

function goToPreviousOciComboPatientPage() {
  if (ociComboPatientPage.value > 1) {
    ociComboPatientPage.value -= 1;
    scrollOciPaginationToTop(ociComboPatientsSectionRef, ociComboPatientsListRef);
  }
}

function goToNextOciComboPatientPage() {
  if (ociComboPatientPage.value < ociComboPatientTotalPages.value) {
    ociComboPatientPage.value += 1;
    scrollOciPaginationToTop(ociComboPatientsSectionRef, ociComboPatientsListRef);
  }
}

function goToPreviousOciAlmostComboPage() {
  if (ociAlmostComboPage.value > 1) {
    ociAlmostComboPage.value -= 1;
    scrollOciPaginationToTop(ociMissingProcedureSectionRef, ociMissingProcedureListRef);
  }
}

function goToNextOciAlmostComboPage() {
  if (ociAlmostComboPage.value < ociAlmostComboTotalPages.value) {
    ociAlmostComboPage.value += 1;
    scrollOciPaginationToTop(ociMissingProcedureSectionRef, ociMissingProcedureListRef);
  }
}

function goToPreviousOciInvalidCidPage() {
  if (ociInvalidCidPage.value > 1) {
    ociInvalidCidPage.value -= 1;
    scrollOciPaginationToTop(ociInvalidCidSectionRef, ociInvalidCidListRef);
  }
}

function goToNextOciInvalidCidPage() {
  if (ociInvalidCidPage.value < ociInvalidCidTotalPages.value) {
    ociInvalidCidPage.value += 1;
    scrollOciPaginationToTop(ociInvalidCidSectionRef, ociInvalidCidListRef);
  }
}

function goToPreviousOciInvalidAuthPage() {
  if (ociInvalidAuthPage.value > 1) {
    ociInvalidAuthPage.value -= 1;
    scrollOciPaginationToTop(ociInvalidAuthSectionRef, ociInvalidAuthListRef);
  }
}

function goToNextOciInvalidAuthPage() {
  if (ociInvalidAuthPage.value < ociInvalidAuthTotalPages.value) {
    ociInvalidAuthPage.value += 1;
    scrollOciPaginationToTop(ociInvalidAuthSectionRef, ociInvalidAuthListRef);
  }
}

function scrollOciPaginationToTop(sectionRefValue, listRefValue) {
  nextTick(() => {
    listRefValue?.value?.scrollTo?.({ top: 0, behavior: 'smooth' });
    sectionRefValue?.value?.scrollIntoView?.({ behavior: 'smooth', block: 'start' });
  });
}

function selectModule(tab, subtab = 'main') {
  activeTab.value = tab;
  activeSubtab.value = subtab;
  showModuleInfo.value = false;

  if (tab === 'tratamento') {
    isTratamentoMenuOpen.value = true;
  }
  if (tab === 'combos') {
    isCombosMenuOpen.value = true;
  }
}

function toggleModuleSubmenu(tab) {
  if (tab === 'tratamento') {
    isTratamentoMenuOpen.value = !isTratamentoMenuOpen.value;
    return;
  }
  if (tab === 'combos') {
    isCombosMenuOpen.value = !isCombosMenuOpen.value;
  }
}

function formatDateTime(value) {
  const date = new Date(value);
  return `${date.toLocaleDateString('pt-BR')} ${date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;
}

function formatPatientDob(value) {
  const raw = String(value || '').trim();
  if (!raw) return '-';

  const digits = raw.replace(/\D/g, '');
  if (digits.length === 8) {
    const year = digits.slice(0, 4);
    const month = digits.slice(4, 6);
    const day = digits.slice(6, 8);
    return `${day}/${month}/${year}`;
  }

  return raw;
}

function maskHealthIdentifier(value, type = 'generic') {
  const digits = String(value || '').replace(/\D/g, '');
  if (!digits) return '';
  if (type === 'cpf' && digits.length === 11) {
    return `***.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
  }
  if (type === 'cns' && digits.length === 15) {
    return `${digits.slice(0, 3)}********${digits.slice(-4)}`;
  }
  if (digits.length > 4) {
    return `${'*'.repeat(Math.max(digits.length - 4, 4))}${digits.slice(-4)}`;
  }
  return digits;
}

function formatMaskedPatientIdentifiers(patient) {
  const masked = isPatientMasked(patient);
  const cpf = masked ? maskHealthIdentifier(patient?.cpf, 'cpf') : (patient?.cpf || '');
  const cns = masked ? maskHealthIdentifier(patient?.cns, 'cns') : (patient?.cns || '');
  const parts = [];
  if (cpf) parts.push(`CPF ${cpf}`);
  if (cns) parts.push(`CNS ${cns}`);
  return parts.join(' | ');
}

function formatCompetencias(competencias) {
  if (!competencias || !competencias.length) return 'Não identificada';
  return competencias.join(', ');
}

function truncate(value, maxLength) {
  if (!value || value.length <= maxLength) return value;
  return `${value.slice(0, maxLength - 1)}…`;
}

function rowClass(status) {
  return ociRowClass(status);
}

function rowStatusClass(status) {
  return ociRowStatusClass(status);
}

function rowStatusLabel(status) {
  if (status === 'removed') return 'Excluído';
  if (status === 'altered') return 'Qtd. alterada';
  return 'Mantido';
}

onMounted(async () => {
  await ensureCsrfReady();
  fetchHistory();
  fetchOciComboHistory();
  if (userStore.hasModuleItemAccess('integra_oci', 'auditoria')) {
    fetchAuditEventTypes();
    if (activeTab.value === 'auditoria') {
      fetchAuditLogs();
    }
  }
});
</script>

<style scoped>
.integra-oci-shell {
  min-height: 0;
}

@media (min-width: 1024px) {
  :global(main:has(.integra-oci-shell)) {
    overflow: hidden;
  }
}

.info-float {
  animation: infoFloat 3.2s ease-in-out infinite;
}

.module-tab-enter-active,
.module-tab-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.module-tab-enter-from,
.module-tab-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@keyframes infoFloat {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

</style>
