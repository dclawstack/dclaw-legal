"use client";

import { useEffect, useState } from "react";
import { Scale, Trash2, Loader2 } from "lucide-react";
import { listReviews, createReview, deleteReview, type ContractReview } from "@/lib/api";
import { toast } from "sonner";
import { SignaturePanel } from "./SignaturePanel";

export default function Dashboard() {
  const [contractText, setContractText] = useState("");
  const [reviews, setReviews] = useState<ContractReview[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedReview, setSelectedReview] = useState<ContractReview | null>(null);

  useEffect(() => {
    loadReviews();
  }, []);

  async function loadReviews() {
    try {
      const data = await listReviews();
      setReviews(data.items);
      if (data.items.length > 0 && !selectedReview) {
        setSelectedReview(data.items[0]);
      }
    } catch (err) {
      toast.error("Failed to load reviews", { description: err instanceof Error ? err.message : "" });
    }
  }

  async function handleReview() {
    if (!contractText.trim()) return;
    setLoading(true);
    try {
      const review = await createReview({ contract_text: contractText.trim() });
      setReviews((prev) => [review, ...prev]);
      setSelectedReview(review);
      setContractText("");
      toast.success("Review complete", { description: `Risk score: ${review.risk_score}` });
    } catch (err) {
      toast.error("Review failed", { description: err instanceof Error ? err.message : "" });
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteReview(id);
      setReviews((prev) => prev.filter((r) => r.id !== id));
      if (selectedReview?.id === id) {
        setSelectedReview(null);
      }
      toast.success("Review deleted");
    } catch (err) {
      toast.error("Failed to delete review");
    }
  }

  const riskColor = (score: number) => {
    if (score > 60) return "text-red-600";
    if (score > 30) return "text-yellow-600";
    return "text-green-600";
  };

  const riskBarColor = (score: number) => {
    if (score > 60) return "bg-red-600";
    if (score > 30) return "bg-yellow-600";
    return "bg-green-600";
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-[#1E3A5F] px-6 py-4 flex items-center gap-3">
        <Scale className="h-6 w-6 text-white" />
        <h1 className="text-xl font-semibold text-white">DClaw Legal</h1>
        <nav className="ml-auto flex items-center gap-4 text-sm text-white/80">
          <a href="/templates" className="hover:text-white">Templates</a>
          <a href="/compare" className="hover:text-white">Compare</a>
          <a href="/batch" className="hover:text-white">Batch</a>
        </nav>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-2xl font-bold text-gray-900">Contract Review</h2>
          <textarea
            className="w-full h-64 rounded-lg border border-gray-300 p-4 text-sm focus:border-[#1E3A5F] focus:ring-1 focus:ring-[#1E3A5F] outline-none resize-none"
            placeholder="Paste contract text here..."
            value={contractText}
            onChange={(e) => setContractText(e.target.value)}
          />
          <button
            onClick={handleReview}
            disabled={loading || !contractText.trim()}
            className="w-full rounded-md bg-[#1E3A5F] px-6 py-3 text-white font-medium hover:bg-[#152a45] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            Review Contract
          </button>

          <div className="space-y-2 pt-4">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">History</h3>
            {reviews.length === 0 ? (
              <p className="text-sm text-gray-400">No reviews yet.</p>
            ) : (
              reviews.map((r) => (
                <div
                  key={r.id}
                  onClick={() => setSelectedReview(r)}
                  className={`cursor-pointer rounded-lg border p-3 text-sm transition-colors ${selectedReview?.id === r.id ? "border-[#1E3A5F] bg-white shadow-sm" : "border-gray-200 bg-white hover:bg-gray-50"}`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900 truncate">{r.title}</span>
                    <span className={`text-xs font-bold ${riskColor(r.risk_score)}`}>{r.risk_score}</span>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-500">{new Date(r.created_at).toLocaleDateString()}</span>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(r.id); }}
                      className="text-gray-400 hover:text-red-600"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-2xl font-bold text-gray-900">Results</h2>
          {!selectedReview ? (
            <div className="rounded-lg bg-white p-12 shadow-sm border border-gray-200 text-center text-gray-500">
              Run a contract review to see results
            </div>
          ) : (
            <div className="space-y-6">
              <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">Risk Score</h3>
                <div className="flex items-center gap-4">
                  <div className={`text-3xl font-bold ${riskColor(selectedReview.risk_score)}`}>
                    {selectedReview.risk_score}
                  </div>
                  <div className="h-2 flex-1 rounded-full bg-gray-200">
                    <div
                      className={`h-2 rounded-full ${riskBarColor(selectedReview.risk_score)}`}
                      style={{ width: `${selectedReview.risk_score}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Key Clauses</h3>
                <ul className="space-y-2">
                  {selectedReview.findings.length > 0 ? (
                    selectedReview.findings.map((f) => (
                      <li key={f.id} className="text-gray-800 text-sm">
                        <span className="font-medium">{f.clause_type}</span>
                        <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${f.risk_level === "high" || f.risk_level === "critical" ? "bg-red-100 text-red-700" : f.risk_level === "medium" ? "bg-yellow-100 text-yellow-700" : "bg-green-100 text-green-700"}`}>
                          {f.risk_level}
                        </span>
                        <p className="text-gray-600 mt-0.5">{f.clause_text}</p>
                      </li>
                    ))
                  ) : (
                    <li className="text-gray-500 text-sm">No specific clauses identified.</li>
                  )}
                </ul>
              </div>

              <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Recommendations</h3>
                <ul className="space-y-2">
                  {selectedReview.findings.some((f) => f.recommendation) ? (
                    selectedReview.findings
                      .filter((f) => f.recommendation)
                      .map((f) => (
                        <li key={f.id} className="text-gray-800 text-sm">• {f.recommendation}</li>
                      ))
                  ) : (
                    <li className="text-gray-500 text-sm">Consider professional legal review.</li>
                  )}
                </ul>
              </div>

              <SignaturePanel
                review={selectedReview}
                onUpdated={(next) => {
                  setSelectedReview(next);
                  setReviews((prev) =>
                    prev.map((r) => (r.id === next.id ? next : r)),
                  );
                }}
              />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
