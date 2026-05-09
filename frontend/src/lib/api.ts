const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface ContractReview {
  id: string;
  title: string;
  contract_text: string;
  risk_score: number;
  status: string;
  envelope_id?: string | null;
  signer_email?: string | null;
  signature_status?: string | null;
  findings: ClauseFinding[];
  created_at: string;
  updated_at: string;
}

export interface ClauseFinding {
  id: string;
  contract_review_id: string;
  clause_text: string;
  clause_type: string;
  risk_level: string;
  recommendation: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContractReviewCreate {
  title?: string;
  contract_text: string;
}

export interface ContractReviewList {
  items: ContractReview[];
  total: number;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API error ${res.status}: ${text || res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export async function listReviews(): Promise<ContractReviewList> {
  return apiFetch<ContractReviewList>("/api/v1/contracts/reviews");
}

export async function createReview(data: ContractReviewCreate): Promise<ContractReview> {
  return apiFetch<ContractReview>("/api/v1/contracts/review", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteReview(id: string): Promise<void> {
  await apiFetch<void>(`/api/v1/contracts/reviews/${id}`, { method: "DELETE" });
}

// ---------- Document Templates ----------

export interface TemplateVariable {
  label: string;
  type: "text" | "textarea" | "date" | "number";
  required: boolean;
}

export interface DocumentTemplate {
  id: string;
  name: string;
  category: string;
  description: string | null;
  template_text: string;
  variables: Record<string, TemplateVariable>;
  created_at: string;
  updated_at: string;
}

export interface DocumentTemplateList {
  items: DocumentTemplate[];
  total: number;
}

export interface TemplateGenerateResult {
  template_id: string;
  rendered_text: string;
  missing_variables: string[];
}

export async function listTemplates(): Promise<DocumentTemplateList> {
  return apiFetch<DocumentTemplateList>("/api/v1/templates");
}

export async function getTemplate(id: string): Promise<DocumentTemplate> {
  return apiFetch<DocumentTemplate>(`/api/v1/templates/${id}`);
}

export async function generateFromTemplate(
  id: string,
  values: Record<string, string>,
): Promise<TemplateGenerateResult> {
  return apiFetch<TemplateGenerateResult>(`/api/v1/templates/${id}/generate`, {
    method: "POST",
    body: JSON.stringify({ values }),
  });
}

// ---------- Contract Compare ----------

export type DiffOp = "equal" | "insert" | "delete" | "replace";

export interface DiffBlock {
  op: DiffOp;
  a_lines: string[];
  b_lines: string[];
}

export interface DiffSummary {
  added: number;
  removed: number;
  modified: number;
  unchanged: number;
}

export interface CompareResult {
  label_a: string;
  label_b: string;
  blocks: DiffBlock[];
  summary: DiffSummary;
}

export async function compareContracts(
  text_a: string,
  text_b: string,
  label_a = "Version A",
  label_b = "Version B",
): Promise<CompareResult> {
  return apiFetch<CompareResult>("/api/v1/legal/compare", {
    method: "POST",
    body: JSON.stringify({ text_a, text_b, label_a, label_b }),
  });
}

// ---------- Batch Processing ----------

export interface BatchJobItem {
  id: string;
  batch_job_id: string;
  filename: string;
  status: string;
  contract_review_id: string | null;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface BatchJob {
  id: string;
  name: string;
  status: string;
  total: number;
  completed: number;
  failed: number;
  items: BatchJobItem[];
  created_at: string;
  updated_at: string;
}

export async function uploadBatch(files: File[]): Promise<BatchJob> {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  const res = await fetch(`${API_BASE}/api/v1/legal/batch`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Upload failed ${res.status}: ${text || res.statusText}`);
  }
  return res.json() as Promise<BatchJob>;
}

export async function getBatch(id: string): Promise<BatchJob> {
  return apiFetch<BatchJob>(`/api/v1/legal/batch/${id}`);
}

// ---------- E-Signature ----------

export interface SignatureResponse {
  review_id: string;
  envelope_id: string;
  signature_status: string;
}

export async function sendForSignature(
  reviewId: string,
  signer_email: string,
  signer_name: string,
  subject = "Please sign this contract",
): Promise<SignatureResponse> {
  return apiFetch<SignatureResponse>(
    `/api/v1/contracts/reviews/${reviewId}/sign`,
    {
      method: "POST",
      body: JSON.stringify({ signer_email, signer_name, subject }),
    },
  );
}
