<p align="center">
  <img src="logo_sms_rio.png" alt="Prefeitura do Rio — Secretaria Municipal de Saúde / SUS" width="520"/>
</p>

<h1 align="center">IntegraOCI</h1>

<p align="center">
  Sistema de apoio ao faturamento SUS — <strong>BPA / APAC / Combos OCI</strong><br/>
  Secretaria Municipal de Saúde · Rio de Janeiro
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/Vue-3.5-42b983?logo=vue.js&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-17-336791?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/licença-Uso%20Interno-blue" />
</p>

---

## Sobre o projeto

O **IntegraOCI** automatiza duas etapas críticas do faturamento ambulatorial SUS seguindo as regras do **DATASUS** para BPA e APAC:

| Módulo | O que faz |
|---|---|
| **BPA Inteligente** | Cruza o BPA-I com a APAC do período, identifica pacientes com OCI formada e remove as linhas duplicadas, gerando um arquivo BPA tratado pronto para importação no BPA Mag (DATASUS). |
| **Validação de Combos OCI** | Analisa os procedimentos de cada paciente, verifica quais Combos OCI foram completamente formados segundo as regras de CBO, CID e autorização, e exporta o resultado em BPA ou planilha. |

---

## Funcionalidades

- **Leitura de BPA e APAC** nos formatos posicional DATASUS (`.txt`) e planilha (`.xlsx`)
- **Cruzamento inteligente** de pacientes por CPF, CNS e similaridade de nome
- **30+ Combos OCI** implementados com regras de CBO, CID, autorização e faixa etária:
  - Mama, colo de útero, próstata, gástrico, colorretal
  - Cardiologia (risco cirúrgico, SCC, insuficiência cardíaca)
  - Ortopedia, ORL, oftalmologia, ginecologia
- **Exportação** em arquivo BPA posicional ou planilha CSV
- **Histórico** de importações com detalhes completos por competência
- **Dashboard analítico** com séries históricas de processamentos
- **Auditoria** completa de eventos por usuário, unidade e CNES
- **Controle de acesso granular** por módulo (bpa_limpo, formar_combos, dashboard, historico, auditoria)

---

## Arquitetura

```
IntegraOCI/
├── backend/                        Django 5 + Django Ninja (API REST)
│   ├── core/                       Configuração, auth JWT, permissões, auditoria
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── api.py                  Login, logout, refresh, permissões
│   │   ├── auth.py                 JWTCookieAuth
│   │   ├── models.py               AuditLog + GroupModulePermission
│   │   └── permissions.py          Catálogo de módulos e itens
│   ├── BpaApac/                    Módulo principal de lógica de negócio
│   │   ├── api.py                  ~5.900 linhas — toda a lógica BPA/APAC/OCI
│   │   ├── models.py               BpaApacImportHistory, OciComboAnalysisHistory, IntegraOciAuditLog
│   │   ├── integra_oci_audit.py    Auditoria específica do módulo
│   │   ├── details_storage.py      Persistência compactada (gzip)
│   │   ├── cnes_units.json         Base de unidades CNES do município
│   │   ├── oci_cbo_cid_rules.json  Regras CBO/CID por combo OCI
│   │   ├── MODELO_BPA_IMPORTACAO.xlsx
│   │   └── MODELO_APAC_IMPORTACAO.xlsx
│   ├── requirements.txt
│   └── .env.example
└── frontend/                       Vue 3 + Tailwind CSS
    └── src/
        ├── views/faturamento/
        │   ├── BpaApacUpload.vue   Interface principal do módulo
        │   └── oci/                Componentes: Alert, Badge, StatCard, TabNav, Theme
        ├── views/login/            Tela de autenticação
        ├── views/templates/        BaseTemplate (navbar)
        ├── router/                 Rotas da SPA
        ├── stores/userStore.js     Pinia — estado e permissões
        └── services/authService.js Axios com CSRF/JWT automático
```

---

## Requisitos

### Backend

| Tecnologia | Versão mínima |
|---|---|
| Python | 3.10+ |
| Django | 5.1.3 |
| Django Ninja | 1.3.0 |
| Redis | 6+ |
| PostgreSQL | 14+ (produção) / SQLite (dev) |
| MySQL | 5.7+ (opcional — banco SIGTAP) |

### Frontend

| Tecnologia | Versão mínima |
|---|---|
| Node.js | 18+ |
| Vue | 3.5+ |
| Tailwind CSS | 3.4+ |

---

## Instalação

### Backend

```bash
cd backend

# Ambiente virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# Dependências
pip install -r requirements.txt

# Variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Banco de dados
python manage.py migrate

# Superusuário
python manage.py createsuperuser

# Servidor de desenvolvimento
python -m uvicorn core.asgi:application --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend

npm install

cp .env.example .env
# Ajuste VUE_APP_API_URL para a URL do backend

npm run serve
```

Acesse: **http://localhost:5173**

---

## Variáveis de Ambiente

### Backend — `.env`

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave secreta Django | — |
| `DEBUG` | Modo debug | `False` |
| `DB_ENGINE` | Engine do banco | `sqlite3` |
| `DB_NAME` | Nome do banco | `db.sqlite3` |
| `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | Conexão PostgreSQL | — |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_CACHE_DB` | Conexão Redis | `127.0.0.1 / 6379 / 1` |
| `TOKEN_EXPIRATION_TIME` | Duração do access token (s) | `86400` |
| `MYSQL_DATA_HOST` | Host MySQL externo (SIGTAP) | — |
| `BPA_APAC_ARTIFACT_RETENTION_DAYS` | Retenção de artefatos em dias | `90` |
| `CORS_ALLOWED_ORIGINS` | Origens permitidas | — |

### Frontend — `.env`

| Variável | Descrição | Padrão |
|---|---|---|
| `VUE_APP_API_URL` | URL base da API Django | `http://localhost:8000` |

---

## API — Endpoints principais

### Autenticação

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/auth/` | Login — emite cookies JWT |
| `POST` | `/api/v1/auth/refresh/` | Renova o access_token |
| `POST` | `/api/v1/auth/logout/` | Remove cookies |
| `GET` | `/api/v1/auth/user/` | Dados do usuário autenticado |
| `GET` | `/api/v1/auth/permissions/` | Permissões de módulo do usuário |

### BPA / APAC / OCI

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/bpa-apac/units/` | Lista unidades CNES |
| `POST` | `/api/v1/bpa-apac/analyze-file/` | Pré-análise de arquivo BPA ou APAC |
| `POST` | `/api/v1/bpa-apac/process/` | Gera BPA tratado (streaming) |
| `POST` | `/api/v1/bpa-apac/oci-combos/analyze/` | Valida combos OCI (streaming) |
| `GET` | `/api/v1/bpa-apac/history/` | Histórico de importações |
| `GET` | `/api/v1/bpa-apac/oci-combos/history/` | Histórico de validações OCI |
| `GET` | `/api/v1/bpa-apac/download/{file_id}/` | Download do arquivo gerado |
| `GET` | `/api/v1/bpa-apac/integra-oci/audit/` | Logs de auditoria |

> Todos os endpoints de BPA/APAC exigem cookie `access_token` válido.

---

## Formatos de arquivo suportados

| Tipo | Formatos |
|---|---|
| BPA-I | `.txt` posicional DATASUS · `.xlsx` modelo IntegraOCI |
| APAC | `.txt` posicional DATASUS · `.xlsx` modelo IntegraOCI |
| Planilha CCE (combos) | `.xlsx` · `.xls` |

Templates: `backend/BpaApac/MODELO_BPA_IMPORTACAO.xlsx` e `MODELO_APAC_IMPORTACAO.xlsx`

---

## Controle de Permissões

Configurável por grupo de usuário via Django Admin (`/admin/`):

| Item | Acesso liberado |
|---|---|
| `bpa_limpo` | BPA Inteligente |
| `formar_combos` | Validação de Combos OCI |
| `dashboard` | Dashboard Analítico |
| `historico` | Histórico e Exportações |
| `auditoria` | Logs de Auditoria |

---

## Manutenção

```bash
# Remove artefatos com mais de 90 dias (padrão)
python manage.py cleanup_bpa_apac_artifacts

# Define retenção customizada
python manage.py cleanup_bpa_apac_artifacts --days 30

# Apenas compacta JSONs legados
python manage.py cleanup_bpa_apac_artifacts --compress-only
```

---

## Integração com plataformas externas

O IntegraOCI foi desenhado para ser consumido por plataformas que:

1. Consultam o SISREG / Datalake municipal
2. Identificam pacientes candidatos a OCI
3. Enviam BPA + APAC para processamento
4. Recebem o arquivo BPA tratado para importação no DATASUS

```
Plataforma parceira
  └─ Consulta SISREG / Datalake
  └─ Detecta pacientes e procedimentos OCI
  └─ Gera BPA + APAC do período
         ↓
  IntegraOCI
  └─ POST /api/v1/bpa-apac/process/           → BPA limpo
  └─ POST /api/v1/bpa-apac/oci-combos/analyze/ → Validação de combos
  └─ GET  /api/v1/bpa-apac/download/{id}/      → Download
         ↓
  DATASUS / BPA Mag
  └─ Importação do arquivo BPA tratado
```

---


