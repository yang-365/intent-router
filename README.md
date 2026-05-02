# intent-router

Intent Router MVP for intent registration, intent recognition, task dispatching, and SSE task state delivery.

Includes a **掌银智能助手** (Mobile Banking Intelligent Assistant) that supports user intent recognition, task planning, skill-based parameter extraction, and API tool calling for common banking operations.

## Project Structure

- `backend/`: FastAPI services, router core, admin API, tests
  - `backend/src/skills/`: Skill framework for parameter extraction and business workflow execution
  - `backend/src/api_tools/`: API tool layer for simulating business API calls
  - `backend/src/intent_agents/`: Intent agent services (transfer, bill payment, fund recommendation, consultation, menu navigation)
- `frontend/`: chat web, admin web, shared packages
- `docs/`: product and architecture docs
- `k8s/`: deployment manifests
- `scripts/`: local verification and cluster helper scripts

## Target Service Topology

The target architecture separates control plane and runtime plane:

- `admin-api` service:
  - owns intent registry CRUD and activation
  - single replica by default
- `router-api` service:
  - owns session/message ingress, intent recognition, and agent dispatch
  - can scale to multiple replicas
- `intent-agent-*` services:
  - one business capability per endpoint
  - fallback must also be an independent agent service

Critical boundary:

- Router only does recognition + dispatch + task state orchestration.
- Router does not execute business intent logic itself.
- When no active business intent matches, router dispatches to fallback agent.
- The default Minikube stack ships built-in demo agents for order status and appointment cancellation; register/deploy fallback separately when needed.

## Ingress Path Rules

Required ingress path conventions:

- `/admin` -> Admin Web
- `/chat` -> Chat Web
- `/api/admin/*` -> Admin API
- `/api/router/*` -> Router API

This keeps UI routes and API routes explicit, and avoids mixing admin and chat traffic.

## Runtime and LLM Wiring

Connection secrets must stay in local env files or shell env vars. This repo ignores `.env` and `.env.*` by default.

Router and agents support OpenAI-compatible model access via `langchain`:

- Router recognizer: `router_core`
- Built-in agents: `intent_agents.order_status_app`, `intent_agents.cancel_appointment_app`, `intent_agents.fallback_app`
- Banking agents: `intent_agents.bill_payment_app`, `intent_agents.fund_recommendation_app`, `intent_agents.consultation_app`, `intent_agents.menu_recognition_app`

Minimum runtime env:

1. Copy `.env.example` to `.env` or `.env.local`.
2. Set:
   - `ROUTER_LLM_API_BASE_URL`
   - `ROUTER_LLM_API_KEY`
   - `ROUTER_LLM_MODEL`
   - `ADMIN_REPOSITORY_BACKEND=database`
   - `ADMIN_DATABASE_URL` (SQLite or MySQL DSN)
3. Set recognizer backend with `ROUTER_RECOGNIZER_BACKEND=llm` (or `rules`).

Supported `agent_url`:

- `http://...` / `https://...`

Intent lifecycle:

- New intent defaults to `inactive`.
- Admin activates/deactivates intents explicitly.
- Router recognizes only active non-fallback intents.
- Fallback intent is excluded from recognizer candidates and dispatched only when no match is selected.

## Deployment Requirements

Kubernetes deployments must define resource `requests` at minimum:

- `resources.requests.cpu`
- `resources.requests.memory`

Rationale:

- predictable scheduling and memory pressure control
- safer multi-replica router scaling
- cleaner SLO isolation between admin and router workloads

## Local Development

Install backend dependencies:

```bash
python -m pip install -e .[dev]
```

Run split backend services:

```bash
uvicorn admin_entry:app --app-dir backend/src --reload --port 8011
uvicorn router_entry:app --app-dir backend/src --reload --port 8012
```

Run built-in agents:

```bash
uvicorn intent_agents.order_status_app:app --app-dir backend/src --reload --port 8101
uvicorn intent_agents.cancel_appointment_app:app --app-dir backend/src --reload --port 8102
```

Run banking assistant agents:

```bash
uvicorn intent_agents.bill_payment_app:app --app-dir backend/src --reload --port 8103
uvicorn intent_agents.fund_recommendation_app:app --app-dir backend/src --reload --port 8104
uvicorn intent_agents.consultation_app:app --app-dir backend/src --reload --port 8105
uvicorn intent_agents.menu_recognition_app:app --app-dir backend/src --reload --port 8106
uvicorn intent_agents.fallback_app:app --app-dir backend/src --reload --port 8107
```

Run tests:

```bash
pytest
```

Compatibility note:

- `backend/src/app.py` still exists as an aggregate app for local integration tests.
- Deployment entrypoints should use `admin_entry:app` and `router_entry:app`.

Run frontends:

```bash
cd frontend
npm install
npm run dev:chat
npm run dev:admin
```

## Banking Assistant Architecture

The banking assistant extends the intent router with three layers:

### Skills Layer (`backend/src/skills/`)

Skills handle parameter extraction and business workflow orchestration. Each skill defines:
- **Slot definitions**: Required parameters with types and descriptions
- **Extract logic**: Rule-based slot extraction from user input
- **Execute logic**: Business workflow execution via API tools

Built-in skills:
| Skill Code | Name | Description |
|---|---|---|
| `transfer_money` | 转账 | Collects recipient info and amount, executes transfer |
| `bill_payment` | 生活缴费 | Handles utility bill payments (electricity, water, gas, phone) |
| `fund_recommendation` | 基金推荐 | Recommends funds based on risk preference |
| `consultation` | 业务咨询 | Answers common banking FAQ questions |
| `menu_recognition` | 菜单导航 | Navigates users to the right feature/menu |

### API Tools Layer (`backend/src/api_tools/`)

Tools simulate actual business API calls. Each tool defines parameters, validation, and execution logic.

Built-in tools:
| Tool Code | Name | Description |
|---|---|---|
| `transfer_api` | 转账接口 | Simulates bank transfer operations |
| `bill_payment_api` | 缴费接口 | Simulates utility bill payments |
| `fund_query_api` | 基金查询接口 | Queries and recommends fund products |
| `account_query_api` | 账户查询接口 | Queries account balance |

### Assistant API Endpoints

The router exposes assistant endpoints under `/api/router/assistant/`:

- `GET /api/router/assistant/skills` — List all available skills
- `GET /api/router/assistant/tools` — List all available API tools
- `POST /api/router/assistant/skills/{skill_code}/extract` — Extract slots from user input
- `POST /api/router/assistant/skills/{skill_code}/execute` — Execute a skill with extracted parameters
- `POST /api/router/assistant/tools/{tool_code}/call` — Directly call an API tool
