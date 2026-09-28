import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    nome: '',
    autenticado: false,
    grupos: [],
    modulePermissions: {},
    isStaff: false,
    isSuperuser: false,
  }),

  getters: {
    /**
     * Verifica acesso a um módulo.
     * Superuser e staff têm acesso a tudo.
     * Se não há permissões configuradas para o módulo, libera (comportamento padrão).
     */
    hasModuleAccess: (state) => (moduleKey) => {
      if (state.isSuperuser || state.isStaff) return true;
      const permission = state.modulePermissions?.[moduleKey];
      // Sem permissões configuradas → libera (padrão aberto)
      if (!permission) return true;
      return permission.allowed === true || permission.can_do === true || permission.can_view === true;
    },

    /**
     * Verifica acesso a um item específico de um módulo.
     *
     * Regras (espelha backend integra_oci_audit.user_has_integra_oci_item):
     * 1. Sem itemKey → true
     * 2. Superuser/staff → true
     * 3. Sem modulePermissions configuradas → true (padrão aberto)
     * 4. Módulo existe mas allowed_items vazio → true
     * 5. allowed_items preenchido → verifica se itemKey está na lista
     */
    hasModuleItemAccess: (state) => (moduleKey, itemKey) => {
      if (!itemKey) return true;
      if (state.isSuperuser || state.isStaff) return true;

      const permission = state.modulePermissions?.[moduleKey];

      // Nenhuma permissão configurada para o módulo → libera tudo
      if (!permission) return true;

      // Módulo existe mas sem restrição de itens → libera tudo
      const allowedItems = Array.isArray(permission?.allowed_items) ? permission.allowed_items : [];
      if (allowedItems.length === 0) return true;

      // Verifica se o itemKey está na lista de itens permitidos
      return allowedItems.some((item) => String(item?.item_key || '') === String(itemKey));
    },
  },

  actions: {
    login(nome, { grupos = [], modulePermissions = {}, isStaff = false, isSuperuser = false } = {}) {
      this.nome = nome;
      this.autenticado = true;
      this.grupos = grupos;
      this.modulePermissions = modulePermissions;
      this.isStaff = isStaff;
      this.isSuperuser = isSuperuser;
    },

    /**
     * Aplica as permissões retornadas pela API após o login.
     * O backend retorna um objeto { integra_oci: { can_view, can_do, allowed_items } }
     */
    setPermissions(permissions) {
      this.modulePermissions = permissions || {};
    },

    logout() {
      this.nome = '';
      this.autenticado = false;
      this.grupos = [];
      this.modulePermissions = {};
      this.isStaff = false;
      this.isSuperuser = false;
    },
  },

  persist: true,
});
