const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface ContractReview {
  id: string;
  title: string;
  contract_text: string;
  risk_score: number;
  status: string;
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
