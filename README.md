# IntegraOCI

Sistema de apoio ao faturamento SUS conforme as regras de **BPA / APAC** do DATASUS, com suporte a detecção, validação e exportação de **Combos OCI** (Oferta de Cuidado Integrado).

Desenvolvido pela Coordenação Geral do Super Centro Carioca de Saúde para a **Secretaria Municipal de Saúde do Rio de Janeiro**.

---

## Visão Geral

O IntegraOCI resolve dois problemas centrais do faturamento ambulatorial SUS:

| Funcionalidade | Descrição |
|---|---|
| **BPA Inteligente** | Cruza o arquivo BPA-I com a APAC do período, identifica e remove automaticamente as linhas de pacientes que já têm OCI (Oferta de Cuidado Integrado) formada, gerando um BPA "limpo" para importação no DATASUS (BPA Mag). |
| **Validação de Combos OCI** | Analisa os procedimentos realizados por cada paciente, verifica quais combos OCI foram formados (regras de CBO, CID e autorização), quais estão incompletos, e gera exportações em BPA ou planilha para acompanhamento. |

### Regras SUS implementadas

- Prefixos de procedimentos OCI: `09`, `05`, `01`
- 30+ combos OCI cobertos: mama, colo de útero, próstata, cólon/reto, cardiologia, ortopedia, otorrinolaringologia, oftalmologia, ginecologia
- Layouts posicionais DATASUS: BPA-C, BPA-I, APAC (corpo + procedimentos)
- Cruzamento por CPF, CNS e similaridade de nome (threshold 0,85)
- Validação de CNES contra base local

---

## Estrutura do Projeto

```
IntegraOCI/
├── backend/                    ← Django 5 + Django Ninja
│   ├── core/                   ← Configuração, auth, auditoria, permissões
│   │   ├── settings.py         ← Settings Django standalone
│   │   ├── urls.py             ← Roteador principal
│   │   ├── api.py              ← Endpoints de autenticação (login, logout, user)
│   │   ├── auth.py             ← JWTCookieAuth (cookie access_token)
│   │   ├── audit.py            ← log_audit_event (auditoria geral)
│   │   ├── middleware.py       ← ForceCSRFMiddleware
│   │   ├── models.py           ← AuditLog + GroupModulePermission
│   │   ├── permissions.py      ← Catálogo de módulos e itens de permissão
│   │   └── wsgi.py
│   ├── BpaApac/                ← Módulo principal de lógica de negócio
│   │   ├── api.py              ← 5.900+ linhas: toda a lógica BPA/APAC/OCI
│   │   ├── models.py           ← BpaApacImportHistory, OciComboAnalysisHistory, IntegraOciAuditLog
│   │   ├── integra_oci_audit.py← Auditoria específica do módulo OCI
│   │   ├── details_storage.py  ← Persistência compactada (gzip) de detalhes
│   │   ├── cnes_units.json     ← Base de unidades CNES do município
│   │   ├── oci_cbo_cid_rules.json ← Regras de CBO/CID por combo OCI
│   │   ├── unidade_202606191548.txt ← Base secundária de validação de CNES
│   │   ├── MODELO_BPA_IMPORTACAO.xlsx  ← Template de importação BPA
│   │   ├── MODELO_APAC_IMPORTACAO.xlsx ← Template de importação APAC
│   │   ├── management/commands/cleanup_bpa_apac_artifacts.py
│   │   └── migrations/
│   ├── bpa_apac_details/       ← Detalhes compactados (gerado em runtime)
│   ├── bpa_apac_outputs/       ← Arquivos BPA tratados (gerado em runtime)
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/                   ← Vue 3 + Tailwind CSS
    ├── src/
    │   ├── views/
    │   │   ├── faturamento/
    │   │   │   ├── BpaApacUpload.vue   ← Interface principal do módulo
    │   │   │   └── oci/                ← Componentes OCI (Alert, Badge, StatCard, TabNav, Theme)
    │   │   ├── login/
    │   │   │   └── LoginScreen.vue     ← Tela de autenticação
    │   │   └── templates/
    │   │       └── BaseTemplate.vue    ← Template base (navbar + layout)
    │   ├── router/index.js             ← Rotas (/ → /faturamento/bpa-apac, /login)
    │   ├── stores/userStore.js         ← Pinia store de autenticação
    │   ├── services/authService.js     ← Axios com CSRF/JWT automático
    │   └── assets/tailwind.css
    ├── package.json
    ├── vue.config.js
    ├── tailwind.config.js
    └── .env.example
```

---

## Requisitos

### Backend

| Tecnologia | Versão |
|---|---|
| Python | 3.11+ |
| Django | 5.1.3 |
| Django Ninja | 1.3.0 |
| Redis | 6+ (obrigatório para rate-limiting e limpeza automática) |
| PostgreSQL | 14+ (produção) / SQLite (desenvolvimento) |
| MySQL | 5.7+ (opcional, banco externo SIGTAP) |

### Frontend

| Tecnologia | Versão |
|---|---|
| Node.js | 18+ |
| Vue | 3.5+ |
| Tailwind CSS | 3.4+ |

---

## Instalação e Configuração

### 1. Backend

```bash
cd backend

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Execute as migrations
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser

# Inicie o servidor de desenvolvimento
python manage.py runserver
```

### 2. Frontend

```bash
cd frontend

# Instale as dependências
npm install

# Configure as variáveis de ambiente
cp .env.example .env
# Ajuste VUE_APP_API_URL para apontar para o backend

# Inicie o servidor de desenvolvimento
npm run serve

# Build para produção
npm run build
```

---

## Variáveis de Ambiente

### Backend (`.env`)

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave secreta Django | Insegura — alterar em produção |
| `DEBUG` | Modo debug | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos | `*` |
| `DB_ENGINE` | Engine do banco | `sqlite3` |
| `DB_NAME` | Nome do banco | `db.sqlite3` |
| `DB_USER` | Usuário do banco | — |
| `DB_PASSWORD` | Senha do banco | — |
| `DB_HOST` | Host do banco | — |
| `DB_PORT` | Porta do banco | — |
| `REDIS_HOST` | Host do Redis | `127.0.0.1` |
| `REDIS_PORT` | Porta do Redis | `6379` |
| `REDIS_CACHE_DB` | Database do Redis | `1` |
| `TOKEN_EXPIRATION_TIME` | Duração do access token (segundos) | `86400` |
| `JWT_ACCESS_MINUTES` | Duração do JWT access (minutos) | `60` |
| `MYSQL_DATA_HOST` | Host do MySQL externo (SIGTAP) | — |
| `MYSQL_DATA_USER` | Usuário MySQL | — |
| `MYSQL_DATA_PASSWORD` | Senha MySQL | — |
| `MYSQL_DATA_DB` | Banco MySQL | — |
| `MYSQL_DATA_PORT` | Porta MySQL | `3306` |
| `BPA_APAC_ARTIFACT_RETENTION_DAYS` | Dias de retenção de artefatos | `90` |
| `BPA_APAC_AUTO_CLEANUP` | Limpeza automática de artefatos | `True` |
| `CORS_ALLOWED_ORIGINS` | Origens CORS permitidas | — |
| `CSRF_TRUSTED_ORIGINS` | Origens CSRF confiáveis | — |
| `FRONTEND_URL` | URL do frontend | `http://localhost:5173` |

### Frontend (`.env`)

| Variável | Descrição | Padrão |
|---|---|---|
| `VUE_APP_API_URL` | URL base da API Django | `http://localhost:8000` |
| `BASE_URL` | URL base da aplicação | `/` |

---

## API — Endpoints

### Autenticação

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/auth/` | Login — emite cookies JWT |
| `POST` | `/api/v1/auth/refresh/` | Renova o access_token |
| `POST` | `/api/v1/auth/logout/` | Logout — remove cookies |
| `GET` | `/api/v1/auth/user/` | Dados do usuário autenticado |

### BPA / APAC / OCI

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/bpa-apac/units/` | Lista unidades CNES disponíveis |
| `POST` | `/api/v1/bpa-apac/analyze-file/` | Analisa arquivo BPA ou APAC antes do processamento |
| `POST` | `/api/v1/bpa-apac/process/` | Processa BPA + APAC → gera BPA limpo (streaming) |
| `POST` | `/api/v1/bpa-apac/oci-combos/analyze/` | Valida combos OCI a partir de BPA(s) + planilha CCE (streaming) |
| `GET` | `/api/v1/bpa-apac/history/` | Histórico de importações BPA/APAC |
| `GET` | `/api/v1/bpa-apac/history/{id}/details/` | Detalhes de uma importação |
| `GET` | `/api/v1/bpa-apac/oci-combos/history/` | Histórico de validações OCI |
| `GET` | `/api/v1/bpa-apac/oci-combos/history/{id}/details/` | Detalhes de uma validação OCI |
| `GET` | `/api/v1/bpa-apac/download/{file_id}/` | Download do arquivo BPA tratado ou removidos |
| `GET` | `/api/v1/bpa-apac/integra-oci/audit/` | Logs de auditoria do módulo |
| `GET` | `/api/v1/bpa-apac/integra-oci/audit/event-types/` | Tipos de eventos de auditoria |

> Todos os endpoints (exceto autenticação) exigem cookie `access_token` válido.

---

## Autenticação

O sistema usa **JWT via cookie HTTP-only** (`access_token`). O fluxo é:

1. `POST /api/v1/auth/` → Django seta os cookies `access_token` e `refresh_token`
2. O frontend envia os cookies automaticamente em todas as requisições (`withCredentials: true`)
3. O Django Ninja valida o cookie via `JWTCookieAuth` antes de cada endpoint
4. Em caso de expiração, o frontend tenta `/api/v1/auth/refresh/` automaticamente

---

## Controle de Permissões

O módulo `integra_oci` tem 5 itens de permissão granular, configuráveis por grupo de usuário via Django Admin:

| Item | Descrição |
|---|---|
| `bpa_limpo` | Acesso ao BPA Inteligente (processamento BPA + APAC) |
| `formar_combos` | Acesso à Validação de Combos OCI |
| `dashboard` | Acesso ao Dashboard Analítico |
| `historico` | Acesso ao Histórico e Exportações |
| `auditoria` | Acesso aos logs de auditoria do módulo |

Configurar via: **Django Admin → Core → Permissões de Módulo por Grupo**

---

## Formatos de Arquivo Suportados

| Tipo | Formatos aceitos |
|---|---|
| BPA-I | `.txt` (posicional DATASUS), `.xlsx` (modelo IntegraOCI) |
| APAC | `.txt` (posicional DATASUS), `.xlsx` (modelo IntegraOCI) |
| Planilha CCE (combos) | `.xlsx`, `.xls` |

Templates de importação estão disponíveis em:
- `backend/BpaApac/MODELO_BPA_IMPORTACAO.xlsx`
- `backend/BpaApac/MODELO_APAC_IMPORTACAO.xlsx`

---

## Operações de Manutenção

### Limpeza manual de artefatos

```bash
# Remove artefatos com mais de 90 dias (padrão)
python manage.py cleanup_bpa_apac_artifacts

# Remove artefatos com mais de 30 dias
python manage.py cleanup_bpa_apac_artifacts --days 30

# Apenas compacta JSONs legados (sem deletar)
python manage.py cleanup_bpa_apac_artifacts --compress-only
```

A limpeza automática é executada uma vez ao dia se `BPA_APAC_AUTO_CLEANUP=True`.

---

## Banco de Dados Externo (SIGTAP — Opcional)

O IntegraOCI pode conectar a um banco MySQL externo para resolver nomes de procedimentos pelo código. Configure as variáveis `MYSQL_DATA_*` no `.env`.

Tabelas detectadas automaticamente (em ordem de preferência):
`procedimento_sigtap`, `vw_procedimento_sigtap`, `sisreg_dim_procedimento_interno`, `dim_procedimento`, `procedimento`, `sigtap_procedimento`

Se não configurado, os nomes de procedimentos aparecem como o código numérico.

---

## Integração com Plataformas Externas

O IntegraOCI foi projetado para ser consumido via API por plataformas que:

1. Consultam o SISREG / Datalake municipal para identificar pacientes candidatos a OCI
2. Enviam o resultado dessa análise para o IntegraOCI via `POST /api/v1/bpa-apac/process/` ou `/oci-combos/analyze/`
3. Recebem o BPA tratado para importação no DATASUS (BPA Mag)

**Fluxo recomendado:**

```
Plataforma parceira
  ↓  Consulta SISREG/Datalake
  ↓  Detecta pacientes OCI
  ↓  Gera BPA + APAC do período
  ↓
IntegraOCI (esta aplicação)
  ↓  POST /api/v1/bpa-apac/process/    → BPA limpo (sem linhas OCI)
  ↓  POST /api/v1/bpa-apac/oci-combos/analyze/ → Validação de combos
  ↓  GET  /api/v1/bpa-apac/download/{id}/      → Download do arquivo
  ↓
DATASUS / BPA Mag
  ↓  Importação do arquivo BPA tratado
```

---

## Desenvolvimento

### Estrutura da Lógica de Negócio

Toda a lógica BPA/APAC/OCI está em `backend/BpaApac/api.py`. Funções principais:

| Função | Responsabilidade |
|---|---|
| `_process_files_internal` | Core do BPA Inteligente: cruza APAC × BPA, remove/ajusta linhas OCI |
| `_evaluate_oci_combos` | Motor de validação de combos: avalia CBO, CID, autorização e faixa etária |
| `_merge_many_patient_maps` | Deduplicação de pacientes por CPF, CNS e similaridade de nome |
| `_aggregate_bpa_patient_procedures_*` | Agrega procedimentos do BPA por paciente (Excel e posicional) |
| `_aggregate_apac_patient_procedures_*` | Agrega procedimentos da APAC por paciente |
| `_generate_treated_bpa_from_oci_analysis` | Gera BPA tratado a partir da análise de combos |
| `keep_alive_json_streaming` | Streaming com keep-alive para evitar timeout em operações longas |
| `parse_fixed_width` / `format_fixed_width_record` | Parse e serialização dos layouts posicionais DATASUS |

### Layouts DATASUS Implementados

- `BPA_HEADER_LAYOUT` — cabeçalho do arquivo BPA
- `BPA_C_LAYOUT` — BPA Consolidado
- `BPA_I_LAYOUT` — BPA Individualizado (39 campos)
- `APAC_CORPO_LAYOUT` — corpo da APAC (47 campos)
- `APAC_PROC_LAYOUT` — procedimentos da APAC (15 campos)

---

## Licença

Uso interno — Secretaria Municipal de Saúde do Rio de Janeiro / CCDTI.
