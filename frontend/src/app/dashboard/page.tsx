"use client";

import { useState } from "react";
import { Scale } from "lucide-react";

export default function Dashboard() {
  const [contractText, setContractText] = useState("");
  const [results, setResults] = useState<{
    riskScore: number;
    keyClauses: string[];
    recommendations: string[];
  } | null>(null);

  const handleReview = () => {
    setResults({
      riskScore: 42,
      keyClauses: ["Indemnification Clause", "Limitation of Liability", "Termination for Convenience"],
      recommendations: ["Clarify indemnification scope", "Cap liability at 12 months fees", "Add 30-day cure period"],
    });
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-[#1E3A5F] px-6 py-4 flex items-center gap-3">
        <Scale className="h-6 w-6 text-white" />
        <h1 className="text-xl font-semibold text-white">DClaw Legal</h1>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-gray-900">Contract Review</h2>
          <textarea
            className="w-full h-96 rounded-lg border border-gray-300 p-4 text-sm focus:border-[#1E3A5F] focus:ring-1 focus:ring-[#1E3A5F] outline-none resize-none"
            placeholder="Paste contract text here..."
            value={contractText}
            onChange={(e) => setContractText(e.target.value)}
          />
          <button
            onClick={handleReview}
            className="rounded-md bg-[#1E3A5F] px-6 py-3 text-white font-medium hover:bg-[#152a45] transition-colors"
          >
            Review Contract
          </button>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900">Results</h2>
          {results ? (
            <div className="space-y-6">
              <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">Risk Score</h3>
                <div className="flex items-center gap-4">
                  <div className={`text-3xl font-bold ${results.riskScore > 60 ? "text-red-600" : results.riskScore > 30 ? "text-yellow-600" : "text-green-600"}`}>
                    {results.riskScore}
                  </div>
                  <div className="h-2 flex-1 rounded-full bg-gray-200">
                    <div
                      className={`h-2 rounded-full ${results.riskScore > 60 ? "bg-red-600" : results.riskScore > 30 ? "bg-yellow-600" : "bg-green-600"}`}
                      style={{ width: `${results.riskScore}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Key Clauses</h3>
                <ul className="space-y-2">
                  {results.keyClauses.map((clause, i) => (
                    <li key={i} className="text-gray-800 text-sm">• {clause}</li>
                  ))}
                </ul>
              </div>

              <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Recommendations</h3>
                <ul className="space-y-2">
                  {results.recommendations.map((rec, i) => (
                    <li key={i} className="text-gray-800 text-sm">• {rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="rounded-lg bg-white p-12 shadow-sm border border-gray-200 text-center text-gray-500">
              Run a contract review to see results
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
