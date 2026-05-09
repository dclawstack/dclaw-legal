"use client";

import { useState } from "react";
import { GitCompareArrows, Loader2, Scale } from "lucide-react";
import { toast } from "sonner";
import { compareContracts, type CompareResult } from "@/lib/api";

export default function ComparePage() {
  const [textA, setTextA] = useState("");
  const [textB, setTextB] = useState("");
  const [labelA, setLabelA] = useState("Version A");
  const [labelB, setLabelB] = useState("Version B");
  const [result, setResult] = useState<CompareResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleCompare() {
    if (!textA.trim() || !textB.trim()) return;
    setLoading(true);
    try {
      const data = await compareContracts(textA, textB, labelA, labelB);
      setResult(data);
    } catch (err) {
      toast.error("Compare failed", {
        description: err instanceof Error ? err.message : "",
      });
    } finally {
      setLoading(false);
    }
  }

  function rowClassFor(op: string): string {
    if (op === "insert") return "bg-emerald-50 border-l-2 border-emerald-500";
    if (op === "delete") return "bg-rose-50 border-l-2 border-rose-500";
    if (op === "replace") return "bg-amber-50 border-l-2 border-amber-500";
    return "";
  }

  function lineColorFor(side: "a" | "b", op: string): string {
    if (op === "insert" && side === "b") return "text-emerald-700";
    if (op === "delete" && side === "a") return "text-rose-700 line-through";
    if (op === "replace") return side === "a" ? "text-rose-700" : "text-emerald-700";
    return "text-gray-700";
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-[#1E3A5F] px-6 py-4 flex items-center gap-3">
        <Scale className="h-6 w-6 text-white" />
        <h1 className="text-xl font-semibold text-white">DClaw Legal — Compare</h1>
        <a
          href="/dashboard"
          className="ml-auto text-sm text-white/80 hover:text-white"
        >
          Dashboard →
        </a>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <input
              type="text"
              value={labelA}
              onChange={(e) => setLabelA(e.target.value)}
              className="w-full rounded-md border border-gray-300 p-2 text-sm font-medium focus:border-[#1E3A5F] focus:ring-1 focus:ring-[#1E3A5F] outline-none"
            />
            <textarea
              className="w-full h-64 rounded-lg border border-gray-300 p-3 text-sm font-mono focus:border-[#1E3A5F] focus:ring-1 focus:ring-[#1E3A5F] outline-none resize-none"
              placeholder="Paste original contract here..."
              value={textA}
              onChange={(e) => setTextA(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <input
              type="text"
              value={labelB}
              onChange={(e) => setLabelB(e.target.value)}
              className="w-full rounded-md border border-gray-300 p-2 text-sm font-medium focus:border-[#1E3A5F] focus:ring-1 focus:ring-[#1E3A5F] outline-none"
            />
            <textarea
              className="w-full h-64 rounded-lg border border-gray-300 p-3 text-sm font-mono focus:border-[#1E3A5F] focus:ring-1 focus:ring-[#1E3A5F] outline-none resize-none"
              placeholder="Paste revised contract here..."
              value={textB}
              onChange={(e) => setTextB(e.target.value)}
            />
          </div>
        </div>

        <button
          onClick={handleCompare}
          disabled={loading || !textA.trim() || !textB.trim()}
          className="rounded-md bg-[#1E3A5F] px-6 py-3 text-white text-sm font-medium hover:bg-[#152a45] disabled:opacity-50 flex items-center gap-2"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <GitCompareArrows className="h-4 w-4" />
          )}
          Compare
        </button>

        {result && (
          <div className="space-y-4">
            <div className="flex flex-wrap gap-3 text-xs">
              <span className="rounded-full bg-emerald-100 text-emerald-800 px-3 py-1">
                +{result.summary.added} added
              </span>
              <span className="rounded-full bg-rose-100 text-rose-800 px-3 py-1">
                −{result.summary.removed} removed
              </span>
              <span className="rounded-full bg-amber-100 text-amber-800 px-3 py-1">
                ~{result.summary.modified} modified
              </span>
              <span className="rounded-full bg-gray-100 text-gray-700 px-3 py-1">
                {result.summary.unchanged} unchanged
              </span>
            </div>

            <div className="rounded-lg bg-white border border-gray-200 overflow-hidden">
              <div className="grid grid-cols-2 text-xs font-medium bg-gray-100 border-b border-gray-200">
                <div className="px-4 py-2 border-r border-gray-200">{result.label_a}</div>
                <div className="px-4 py-2">{result.label_b}</div>
              </div>
              <div className="divide-y divide-gray-100 max-h-[60vh] overflow-auto">
                {result.blocks.map((block, idx) => {
                  const rowCount = Math.max(
                    block.a_lines.length,
                    block.b_lines.length,
                    1,
                  );
                  return Array.from({ length: rowCount }).map((_, lineIdx) => {
                    const aLine = block.a_lines[lineIdx];
                    const bLine = block.b_lines[lineIdx];
                    return (
                      <div
                        key={`${idx}-${lineIdx}`}
                        className={`grid grid-cols-2 text-xs font-mono ${rowClassFor(block.op)}`}
                      >
                        <div
                          className={`px-4 py-1 border-r border-gray-100 whitespace-pre-wrap ${lineColorFor("a", block.op)}`}
                        >
                          {aLine ?? ""}
                        </div>
                        <div
                          className={`px-4 py-1 whitespace-pre-wrap ${lineColorFor("b", block.op)}`}
                        >
                          {bLine ?? ""}
                        </div>
                      </div>
                    );
                  });
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
