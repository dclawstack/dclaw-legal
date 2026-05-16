# DClaw Legal — v1.2 Feature Roadmap

> 📘 **REVISED PRD v2.3 available:** See `REVISED-PRD.md` for complete gap analysis, current state, and full feature roadmap.


> Based on: Y Combinator vertical SaaS principles, trending GitHub repos (legal-document-manager), AI product research (Harvey, Lexion, Ironclad, SpotDraft)

## Pre-Flight Checklist

- [ ] `frontend/package-lock.json` committed after any `npm install` / dependency change
- [ ] `frontend/next-env.d.ts` exists and is committed
- [ ] `docker-compose.yml` healthchecks correct
- [ ] `frontend/Dockerfile` declares `ARG NEXT_PUBLIC_API_URL` before `RUN npm run build`

## v1.0 Feature Inventory (Current)

- [ ] Matter/case management
- [ ] Document storage & version control
- [ ] Contact management (clients, opposing counsel)
- [ ] Time tracking & billing
- [ ] Real backend CRUD (no mocks)
- [ ] Docker + Helm deployment
- [ ] Alembic migrations
- [ ] Backend tests

---

## v1.2 Roadmap

### P0 — Must Have (Ship in v1.0, demo-ready)

#### 1. AI Legal Copilot (Document Analyst)
**Description:** AI assistant that reads contracts, identifies risks, answers legal questions, and suggests clauses. "What are the termination risks in this agreement?"
- **AI Angle:** Contract parsing (LLM). Risk classification. RAG over legal knowledge base.
- **Backend:** `/api/v1/ai/legal-chat` endpoint. Document analysis pipeline.
- **Frontend:** AI sidebar in document viewer. Highlighted risk annotations.
- **Files:** `backend/app/services/legal_ai.py`, `frontend/src/components/legal-copilot.tsx`

#### 2. Contract Review & Risk Scoring
**Description:** Upload contracts. AI extracts key terms, flags risks, compares to company playbook.
- **AI Angle:** Clause extraction + risk scoring against precedent database.
- **Backend:** `/api/v1/ai/analyze-contract` endpoint.
- **Frontend:** Contract upload → analysis report with risk heatmap.
- **Files:** `backend/app/services/contract_analyzer.py`

#### 3. Matter Management & Workflow
**Description:** Track cases/matters with stages, deadlines, tasks, and document associations.
- **Backend:** Matter lifecycle workflow. Deadline reminders.
- **Frontend:** Matter board (Kanban). Calendar view of deadlines.
- **Files:** `backend/app/services/matters.py`

#### 4. Time Tracking & Invoicing
**Description:** Track billable hours by matter. Generate invoices with rate cards. UTBMS coding.
- **Backend:** Timer + manual entry. Invoice generation.
- **Frontend:** Time entry widget. Invoice preview.
- **Files:** `backend/app/services/billing.py`

### P1 — Should Have (v1.1–1.2)

#### 5. Clause Library & Playbook
**Description:** Curated clause library with fallback positions. AI suggests clauses based on contract type.
- **Backend:** Clause database with versioning. Playbook rules engine.
- **Frontend:** Clause browser. Drag-and-drop into contract editor.

#### 6. E-Signature & Approval Workflow
**Description:** Route documents for internal and external approval. E-signature (DocuSign/HelloSign).
- **Backend:** Approval chain engine. E-sign webhook handling.
- **Frontend:** Approval workflow designer. Signature status tracker.

#### 7. Legal Research & Case Law
**Description:** Search case law, statutes, and regulations. AI summarizes relevant precedents.
- **AI Angle:** Case law search + LLM summarization.
- **Backend:** Legal search API integration.
- **Frontend:** Research workspace with AI summaries.

#### 8. Regulatory Compliance Tracker
**Description:** Track compliance deadlines, filing requirements, and regulatory changes.
- **Backend:** Regulatory event monitoring. Deadline alerts.
- **Frontend:** Compliance calendar. Risk register.

### P2 — Could Have (v1.3+)

#### 9. AI Contract Drafting
**Description:** Generate first-draft contracts from briefs and templates.

#### 10. Litigation Analytics
**Description:** Predict case outcomes based on judge, jurisdiction, and case type.

#### 11. IP Portfolio Management
**Description:** Track trademarks, patents, and filings with deadline management.

#### 12. Client Portal
**Description:** Secure client-facing portal for document sharing and matter updates.

---

## Implementation Priority

1. **Week 1–2:** AI Legal Copilot (P0.1) + Contract Review (P0.2)
2. **Week 3–4:** Matter Management (P0.3) + Time Tracking (P0.4)
3. **Week 5–6:** Clause Library (P1.5) + E-Signature (P1.6)
4. **Week 7–8:** Legal Research (P1.7) + Compliance Tracker (P1.8)
