# DClaw Legal — v1.2 Feature Roadmap

> **For coding agents:** Pick features from this list, implement them fully, and update this doc with a checkmark.
> **Do NOT change the basic stack.** See `AGENTS.md` for architecture lock.

## v1.0 Feature Inventory (Current)

- [x] Contract review with AI analysis
- [x] Risk score calculation (0-100)
- [x] Clause detection with risk levels
- [x] Recommendations per clause
- [x] Review history sidebar
- [x] Real backend CRUD (no mocks)
- [x] Ollama/OpenRouter/keyword fallback analysis
- [x] Docker + Helm deployment
- [x] Alembic migrations
- [x] Backend tests

---

## v1.2 Roadmap

### P0 — Must Have

#### 1. Document Templates
**Description:** Pre-defined contract templates (NDA, MSA, SOW, Employment Agreement) that users can fill in and review.
- **Backend:** Add `DocumentTemplate` model (`id`, `name`, `category`, `template_text`, `variables` JSON). Add `POST /api/v1/templates/{id}/generate` that accepts variable values and returns filled contract text.
- **Frontend:** Template gallery page. Form builder from template variables. Generate → Review workflow.
- **Files to touch:** `backend/app/models/document_template.py`, `backend/app/repositories/template_repo.py`, `backend/app/api/v1/legal.py`, `frontend/src/app/templates/page.tsx`

#### 2. E-Signature Integration (DocuSign API)
**Description:** Send reviewed contracts for signature via DocuSign.
- **Backend:** Integrate DocuSign eSignature REST API. Store `envelope_id`, `signer_email`, `status` in `ContractReview`. Webhook handler for status updates.
- **Frontend:** "Send for Signature" button after review. Status tracking (sent, delivered, signed, declined).
- **Files to touch:** `backend/app/services/docusign_service.py`, `backend/app/api/v1/legal/signatures.py`, `frontend/src/app/dashboard/SignaturePanel.tsx`

#### 3. Contract Comparison (Redlining / Diff)
**Description:** Compare two versions of a contract side-by-side with highlighted differences.
- **Backend:** Use `difflib` or Google `diff-match-patch` to compute line-level diffs. `POST /api/v1/legal/compare` accepts two texts, returns diff blocks.
- **Frontend:** Side-by-side diff viewer with green (added), red (removed), yellow (modified) highlights.
- **Files to touch:** `backend/app/services/diff_service.py`, `backend/app/api/v1/legal.py`, `frontend/src/app/compare/page.tsx`

#### 4. Batch Document Processing
**Description:** Upload multiple contracts at once and review them all.
- **Backend:** `POST /api/v1/legal/batch` accepts ZIP or multiple files. Queue processing with background tasks (Celery or asyncio tasks). Store batch job status.
- **Frontend:** Drag-and-drop multi-file upload. Progress bar. Results table with batch overview.
- **Files to touch:** `backend/app/services/batch_service.py`, `backend/app/api/v1/legal.py`, `frontend/src/app/batch/page.tsx`

### P1 — Should Have

#### 5. Party Extraction
**Description:** Automatically identify all parties (companies, individuals) mentioned in a contract.
- **Backend:** Use LLM prompt: "Extract all parties from this contract. Return JSON with name, role, and address." Store in `ContractParty` model.
- **Frontend:** Party list panel in review results. Click to highlight mentions in original text.
- **Files to touch:** `backend/app/models/contract_party.py`, `backend/app/services/party_extraction_service.py`, `frontend/src/app/dashboard/PartiesPanel.tsx`

#### 6. Compliance Checklists
**Description:** Run contract against regulatory frameworks (GDPR, SOC2, HIPAA, CCPA).
- **Backend:** Pre-defined checklists with required clauses. `POST /api/v1/legal/compliance-check` returns pass/fail per checklist item with missing clauses.
- **Frontend:** Compliance badge on review. Detailed checklist view.
- **Files to touch:** `backend/app/services/compliance_service.py`, `backend/app/api/v1/legal.py`, `frontend/src/app/dashboard/CompliancePanel.tsx`

#### 7. Export to Word / PDF
**Description:** Download reviewed contracts as formatted Word or PDF documents.
- **Backend:** Use `python-docx` for Word, `weasyprint` or `pdfkit` for PDF. Include review annotations as comments/side notes.
- **Frontend:** Export dropdown (Word, PDF, Markdown) in review results.
- **Files to touch:** `backend/app/services/export_service.py`, `backend/app/api/v1/legal.py`, `frontend/src/app/dashboard/ExportButton.tsx`

#### 8. Case Law Search
**Description:** Search relevant case law based on contract clauses.
- **Backend:** Integrate with CourtListener API or similar. `GET /api/v1/legal/case-law?q=query`.
- **Frontend:** "Related Cases" section in review results. Citation cards.
- **Files to touch:** `backend/app/services/case_law_service.py`, `backend/app/api/v1/legal.py`, `frontend/src/app/dashboard/CaseLawPanel.tsx`

### P2 — Could Have

#### 9. Contract Negotiation Playbook
**Description:** AI-generated negotiation strategy based on contract terms.
- **Backend:** LLM prompt for negotiation tips per clause. Store in `NegotiationTip` model.
- **Frontend:** "Negotiate" tab with bullet-point strategies.

#### 10. Third-Party Risk Assessment
**Description:** Assess counterparty risk using public data (credit ratings, litigation history).
- **Backend:** Integrate with business intelligence APIs (e.g., Clearbit, OpenCorporates).
- **Frontend:** Risk badge next to each detected party.

---

## Implementation Priority

1. Document Templates (productivity)
2. Contract Comparison (core legal workflow)
3. Batch Document Processing (scalability)
4. E-Signature Integration (workflow completion)
5. Party Extraction (data enrichment)
6. Compliance Checklists (regulatory value)
7. Export to Word/PDF (output flexibility)
8. Case Law Search (legal research)
9. Contract Negotiation Playbook (advanced AI)
10. Third-Party Risk Assessment (enterprise)
