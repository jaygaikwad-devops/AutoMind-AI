# AutoMind AI

> **Your Autonomous AI Marketing Team.** Generate AI videos, automate social media, launch campaigns, orchestrate AI agents, and scale your marketing — automatically.

A production-grade, billion-dollar-startup-feel AI SaaS platform for autonomous marketing.

---

## ✨ Features

- 🎬 **AI Video Generation** — text-to-reel in 4K
- 🤖 **AI Agent Network** — 6 specialized agents working 24/7
- 📲 **Autonomous Social Publishing** — IG, FB, LinkedIn, TikTok, YouTube Shorts, Meta Ads
- 🪄 **AI Content Studio** — captions, hashtags, scripts, threads
- 🧠 **Visual Workflow Builder** — n8n / Zapier-style canvas for AI pipelines
- 🎯 **AI Lead Generation** — smart funnels with no spam
- 📈 **Realtime Analytics** — sub-second telemetry over WebSocket
- 🔥 **Viral Content Engine** — predicts hits before posting
- 💼 **Multi-platform Publishing** — one click, every channel
- 🚀 **Campaign Automation** — self-tuning ad spend

---

## 🛠 Tech Stack

**Frontend** — React 19 · TanStack Start v1 (Next.js-compatible architecture) · Tailwind CSS v4 · Motion (Framer Motion) · Shadcn/UI · Lucide Icons · Zustand · Axios

**Backend** — FastAPI · PostgreSQL · Redis · Celery workers · JWT auth · WebSockets · SQLAlchemy 2

**Infrastructure** — Docker · docker-compose · Kubernetes / ECS ready · Vercel / Railway deploy-ready

---

## 📁 Folder structure

```
.
├── frontend/                 # Containerized frontend (mirrors /src in Lovable)
│   └── Dockerfile
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py           # FastAPI entrypoint
│       ├── core/             # config, security
│       ├── models/           # SQLAlchemy models
│       ├── schemas/          # Pydantic schemas
│       ├── routers/          # auth, videos, social, agents, workflows, analytics, ws
│       └── workers/          # Celery tasks (video render, publishing)
├── src/                      # Live Lovable frontend (TanStack Start + React 19)
│   ├── routes/               # File-based routing
│   ├── components/landing/   # Hero, Features, Pricing, AgentNetwork, etc.
│   └── styles.css            # Design system (oklch dark theme, neon gradients)
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🚀 Quick start

### 1. One-command Docker setup (recommended)

Clone the repo, then run:

```bash
./setup.sh
```

That single command will:
1. Check Docker and Docker Compose are installed
2. Create `.env` from `.env.example` with a secure auto-generated `JWT_SECRET`
3. Build all containers (frontend, backend, worker, postgres, redis)
4. Start everything in detached mode
5. Wait for the API to respond, then print all access URLs

| Service   | URL                       |
| --------- | ------------------------- |
| Frontend  | http://localhost:3000     |
| Backend   | http://localhost:8000     |
| API docs  | http://localhost:8000/docs |
| Postgres  | localhost:5432            |
| Redis     | localhost:6379            |

**Makefile helpers** (run from repo root):

```bash
make up      # same as ./setup.sh up
make down    # stop all services
make logs    # follow all logs
make clean   # stop + remove volumes + reset env
```

### 2. Docker Compose manually

If you prefer the classic approach:

```bash
cp .env.example .env
docker compose up --build
```

### 3. Local dev (no Docker)

**Frontend** (run from repo root):
```bash
bun install
bun run dev          # http://localhost:5173
```

**Backend**:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Celery worker**:
```bash
cd backend
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

---

## 🔑 Environment variables

See `.env.example`. Required:

| Var | Description |
|---|---|
| `DATABASE_URL` | Postgres connection (asyncpg) |
| `REDIS_URL` | Redis + Celery broker |
| `JWT_SECRET` | Long random string |
| `OPENAI_API_KEY` | LLM provider |
| `REPLICATE_API_TOKEN` | Video model provider |
| `META_APP_ID` / `TIKTOK_CLIENT_KEY` / `LINKEDIN_CLIENT_ID` / `YOUTUBE_API_KEY` | Social publishing OAuth |

---

## ☁️ Deployment

### Vercel (frontend)
```bash
vercel --prod
```
Set `NEXT_PUBLIC_API_URL` to your backend URL.

### Railway (full stack)
1. Connect repo
2. Add Postgres + Redis plugins
3. Deploy `backend/` and `frontend/` as separate services
4. Copy `DATABASE_URL` and `REDIS_URL` from plugins into backend env

### AWS (production)
- **Frontend**: S3 + CloudFront (or Amplify)
- **Backend**: ECS Fargate behind ALB
- **Workers**: ECS Fargate (separate task definition for Celery)
- **DB**: RDS Postgres Multi-AZ
- **Queue**: ElastiCache Redis
- **Storage**: S3 for rendered videos
- **CDN**: CloudFront for `videos/*`

### Kubernetes
Helm chart layout (not bundled):
```
charts/automind/
  templates/
    backend-deployment.yaml
    worker-deployment.yaml
    frontend-deployment.yaml
    postgres-statefulset.yaml
    redis-deployment.yaml
    ingress.yaml
```

---

## 🧠 Architecture

```
            ┌──────────────┐
            │   Frontend   │  (Next.js / TanStack Start)
            └──────┬───────┘
                   │  HTTPS + WS
            ┌──────▼───────┐
            │  API Gateway │  (FastAPI · Uvicorn)
            └──┬───────┬───┘
       JWT │       │  WebSocket
   ┌───────▼─┐  ┌──▼────────┐
   │ Postgres│  │  Redis    │ ──► Celery Workers
   └─────────┘  └───────────┘       ├─ Video renderer
                                    ├─ Social publisher
                                    └─ Agent orchestrator
```

---

## 📜 License

MIT © AutoMind AI
