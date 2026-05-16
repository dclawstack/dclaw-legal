---
tags: [meta, prd, revised, swarm]
version: 2.3
date: 2026-05-16
app_id: legal
app_name: DClaw Legal
category: Legal
status: Future
---

# 📘 DClaw Legal — Revised PRD v2.3

> **The single document every agent must read before writing code for this app.**
> Generated from DClaw Master PRD v2.2. Read the Master PRD first: https://raw.githubusercontent.com/dclawstack/dclaw-prd/main/DClaw-Master-PRD.md

---

## 1. Product Identity

| Field | Value |
|-------|-------|
| **App ID** | `legal` |
| **Name** | DClaw Legal |
| **Category** | Legal |
| **Tagline** | Contract review, case law |
| **Color** | #6366F1 |
| **Phase** | Future |
| **Port (Frontend Dev)** | 3051 (TBD — assign before build) |
| **Port (Backend Dev)** | 18121 (TBD — assign before build) |
| **Maturity Tier** | 🔴 Tier 3 — Minimal Scaffold |

---

## 2. Current State Assessment

### 2.1 Scaffold Status
| Component | Status | Notes |
|-----------|--------|-------|
| `frontend/` | ✅ | Next.js 14+ app |
| `backend/` | ✅ | FastAPI + SQLAlchemy 2.0 |
| `docs/` | ✅ | getting-started, guides, reference, releases |
| `helm/` | ✅ | K8s deployment manifests |
| `.github/workflows/` | ✅ | CI/CD + Claude integration |
| `AGENTS.md` | ✅ | Per-repo agent instructions |
| `PLAN-v1.2.md` | ✅ | Feature roadmap |
| `docker-compose.yml` | ✅ | Local dev stack |
| `tests/` | ✅ | pytest + pytest-asyncio |
| `alembic/` | ✅ | Database migrations |
| `dclaw-manifest.json` | ❌ | DPanel registration |

### 2.2 Code Maturity
| Metric | Value |
|--------|-------|
| Python source files (backend) | ~18 |
| TypeScript/TSX files (frontend) | ~5 |
| Total source files | ~23 |
| Tests | ✅ Present |
| Alembic migrations | ✅ Present |
| DPanel manifest | ❌ Missing |

### 2.3 Feature Maturity
- **P0 Foundation:** Not yet implemented
- **P1 Platform:** Not yet started
- **P2 Vertical:** Not yet started

---

## 3. Gap Analysis

| # | Gap | Severity | Fix |
|---|-----|----------|-----|
| 1 | Missing `dclaw-manifest.json` | 🔴 | Create frontend/public/dclaw-manifest.json for DPanel |
| 2 | Minimal source code — mostly template scaffold | 🔴 | Implement P0 backend models, API routes, and frontend pages |

---

## 4. Sacred Architecture & Tech Stack

> **NON-NEGOTIABLE. Every DClaw product MUST use this exact stack.**

| Layer | Technology | Version |
|-------|------------|---------|
| **Frontend** | Next.js 14+ | App Router, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI | Pydantic v2, SQLAlchemy 2.0, asyncpg |
| **Database** | PostgreSQL 16 | CloudNativePG operator in K8s |
| **Vector DB** | Qdrant / pgvector | Only if RAG / semantic search |
| **Cache / Bus** | Redis | 7.x |
| **Object Storage** | MinIO | Latest |
| **Workflow** | Temporal.io | Only if automation/orchestration |
| **Auth** | Logto | JWT validation on all protected routes |
| **Billing** | Stripe | Metered or per-seat |
| **K8s Operator** | Go + controller-runtime | 0.18 |
| **LLM Local** | Ollama | Apple Silicon |
| **LLM Cloud** | OpenRouter + Kimi K2.5 | Fallback |
| **Monitoring** | Prometheus + Grafana | Latest |

### 4.1 Python Rules
- `ruff` formatting enforced
- Type hints on ALL public APIs
- `pydantic` v2 for schemas
- `sqlalchemy` 2.0 style (`Mapped`, `mapped_column`)
- `pytest` + `pytest-asyncio` for tests
- Functions < 50 lines
- No `print()` — use `structlog`

### 4.2 TypeScript / Next.js Rules
- Strict TypeScript (`strict: true`)
- Tailwind for ALL styling
- `cn()` utility for conditional classes
- No `any` without `// @ts-ignore`

### 4.3 Docker Standards
- Port mappings MUST match container listen port
- Healthchecks MUST use binaries present in base image
- `docker compose config` must pass before shipping
- Service type MUST be `ClusterIP`
- TLS required on all ingress

---

## 5. P0 Foundation Features (Must Have — Demo Ready)

> **Every P0 MUST include an AI Copilot per YC S25/W26 RFS.**

| # | Feature | Description | AI Component | Acceptance Criteria |
|---|---------|-------------|--------------|---------------------|
| P0.1 | **AI Legal Copilot** | Review contracts, answer legal questions, and draft clauses. | Legal-BERT + RAG over case law + contract analysis | Review 50-page contract in <60s; flag 10+ risk types |
| P0.2 | **Contract Repository** | Store, version, and search all contracts with AI tagging. | AI clause-extraction + obligation mapping | Upload 100+ contracts; auto-tag by type; full-text search |
| P0.3 | **Case Law Research** | Search and summarize relevant case law and statutes. | RAG over legal corpus + LLM synthesis | Search 1M cases; summarize top 5 precedents; cite correctly |
| P0.4 | **Clause Library** | Reusable clause templates with AI-powered customization. | AI clause-drafting from context + risk assessment | 100+ clauses; auto-adapt to jurisdiction; risk scoring |

---

## 6. P1 Platform Features (Should Have — v1.1–1.2)

| # | Feature | Description | AI Component | Acceptance Criteria |
|---|---------|-------------|--------------|---------------------|
| P1.1 | **Contract Comparison** | Side-by-side comparison of contract versions and templates. | AI difference-highlighting + risk-change detection | Highlight additions/deletions; flag risk-increasing changes |
| P1.2 | **eSignature Integration** | Send contracts for signature via DocuSign / HelloSign. | AI signer-sequence optimization + reminder scheduling | 3 eSignature providers; track status; auto-remind |
| P1.3 | **Compliance Checking** | Verify contracts against regulatory requirements (GDPR, SOX, etc.). | AI regulation-mapping + gap analysis | Check 20+ regulations; generate compliance report |
| P1.4 | **Matter Management** | Track legal matters, deadlines, and billing. | AI deadline-risk prediction + resource allocation | Kanban view; deadline alerts; time tracking; invoicing |

---

## 7. P2 Vertical / Scale Features (Could Have — v1.3+)

| # | Feature | Description | AI Component | Acceptance Criteria |
|---|---------|-------------|--------------|---------------------|
| P2.1 | **NDA Automation** | Auto-generate and send NDAs with recipient-specific terms. | AI term-customization + jurisdiction adaptation | Generate NDA in <30s; auto-send; track execution |
| P2.2 | **Litigation Support** | Organize discovery documents and generate deposition summaries. | AI document-clustering + timeline generation | Cluster 10K documents; generate chronology; entity linking |
| P2.3 | **IP Portfolio** | Track trademarks, patents, and copyrights with renewal alerts. | AI renewal-risk scoring + filing-deadline prediction | Portfolio dashboard; expiry alerts; filing history |
| P2.4 | **Legal Spend Analytics** | Analyze outside counsel spend and matter profitability. | AI budget-variance prediction + rate benchmarking | Track spend by firm/matter; benchmark rates; predict overruns |

---

## 8. Scaffold Checklist

Before marking this app "shipped", confirm:

- [ ] `frontend/` with Next.js 14+, Tailwind, shadcn/ui
- [ ] `backend/` with FastAPI, Pydantic v2, SQLAlchemy 2.0, asyncpg
- [ ] `docs/` with getting-started, guides, reference, releases, troubleshooting
- [ ] `helm/` with Chart.yaml, values.yaml, templates (deployment, service, ingress, cloudnativepg)
- [ ] `.github/workflows/` with build-backend.yml, build-frontend.yml, deploy.yml, claude.yml
- [ ] `frontend/public/dclaw-manifest.json` for DPanel registration
- [ ] `backend/tests/` with pytest + pytest-asyncio
- [ ] `backend/alembic/` with initial migration
- [ ] `Dockerfile` + `docker-compose.yml` with correct healthchecks
- [ ] Health endpoint at `/health` returning `{"status":"ok"}`
- [ ] `AGENTS.md` with per-repo instructions
- [ ] `PLAN-v1.2.md` with feature roadmap
- [ ] Port assigned from registry and documented
- [ ] No hardcoded secrets — use `.env.example` + K8s Secrets
- [ ] Non-root containers in Dockerfile

---

## 9. AI Copilot Mandate (YC S25/W26 Requirement)

Every DClaw app MUST have an AI Copilot as its first P0 feature. The copilot must:
1. Be contextually aware of the app's domain data
2. Use RAG over the app's knowledge base where applicable
3. Suggest next actions, not just answer questions
4. Be accessible from every page via floating chat or sidebar
5. Fall back to local Ollama when cloud is unavailable

---

## 10. Next Tasks for Vibe Coders

1. **Scaffold the backend**: Create `backend/app/` with models, schemas, API routes, and services per the P0 features above.
2. **Scaffold the frontend**: Create `frontend/src/app/` with pages for each P0 feature using Next.js 14 App Router + shadcn/ui.
3. **Add infrastructure**: Create `helm/`, `docker-compose.yml`, `.github/workflows/`, and `docs/` following dclaw-scaffold conventions.
4. **Write tests**: Add `backend/tests/` with pytest + pytest-asyncio covering all P0 API endpoints.

---

## 11. Domain Research Notes

Inspired by Ironclad, Lexion, Harvey AI, CoCounsel. Legal AI is a $50B+ TAM with clear ROI.

---

## 12. Links & Resources

| Resource | URL |
|----------|-----|
| **Master PRD** | https://raw.githubusercontent.com/dclawstack/dclaw-prd/main/DClaw-Master-PRD.md |
| **GitHub Org** | https://github.com/dclawstack |
| **DPanel** | https://dpanel.dclawstack.io |
| **Port Registry** | See `dclaw-platform/PORT_REGISTRY.md` |
| **App PRD Template** | Obsidian Vault → `00-META/📐 App PRD Template.md` |
| **Scaffold Source** | `dclaw-scaffold/` in DClaw-Stack |

---

*Revised PRD version: 2.3*
*Generated: 2026-05-16 by DClaw Stack Generator*
*Next review: When P0 features are complete or architecture changes*
