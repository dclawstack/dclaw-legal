"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { FileText, Loader2, Scale, Sparkles } from "lucide-react";
import { toast } from "sonner";
import {
  type DocumentTemplate,
  createReview,
  generateFromTemplate,
  listTemplates,
} from "@/lib/api";

export default function TemplatesPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<DocumentTemplate[]>([]);
  const [selected, setSelected] = useState<DocumentTemplate | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [rendered, setRendered] = useState<string>("");
  const [generating, setGenerating] = useState(false);
  const [reviewing, setReviewing] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  async function loadTemplates() {
    try {
      const data = await listTemplates();
      setTemplates(data.items);
    } catch (err) {
      toast.error("Failed to load templates", {
        description: err instanceof Error ? err.message : "",
      });
    }
  }

  function handleSelect(template: DocumentTemplate) {
    setSelected(template);
    setValues({});
    setRendered("");
  }

  async function handleGenerate() {
    if (!selected) return;
    setGenerating(true);
    try {
      const result = await generateFromTemplate(selected.id, values);
      setRendered(result.rendered_text);
      if (result.missing_variables.length > 0) {
        toast.warning("Some required fields are missing", {
          description: result.missing_variables.join(", "),
        });
      } else {
        toast.success("Contract generated");
      }
    } catch (err) {
      toast.error("Generation failed", {
        description: err instanceof Error ? err.message : "",
      });
    } finally {
      setGenerating(false);
    }
  }

  async function handleSendForReview() {
    if (!rendered || !selected) return;
    setReviewing(true);
    try {
      const review = await createReview({
        title: selected.name,
        contract_text: rendered,
      });
      toast.success("Review created", {
        description: `Risk score: ${review.risk_score}`,
      });
      router.push("/dashboard");
    } catch (err) {
      toast.error("Review failed", {
        description: err instanceof Error ? err.message : "",
      });
    } finally {
      setReviewing(false);
    }
  }

  const grouped = templates.reduce<Record<string, DocumentTemplate[]>>(
    (acc, t) => {
      (acc[t.category] ||= []).push(t);
      return acc;
    },
    {},
  );

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-[#1E3A5F] px-6 py-4 flex items-center gap-3">
        <Scale className="h-6 w-6 text-white" />
        <h1 className="text-xl font-semibold text-white">DClaw Legal — Templates</h1>
        <a
          href="/dashboard"
          className="ml-auto text-sm text-white/80 hover:text-white"
        >
          Dashboard →
        </a>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Gallery */}
        <aside className="lg:col-span-3 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Gallery</h2>
          {Object.keys(grouped).length === 0 ? (
            <p className="text-sm text-gray-400">No templates available.</p>
          ) : (
            Object.entries(grouped).map(([category, items]) => (
              <div key={category} className="space-y-2">
                <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {category}
                </h3>
                {items.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => handleSelect(t)}
                    className={`w-full text-left rounded-lg border p-3 text-sm transition-colors ${
                      selected?.id === t.id
                        ? "border-[#1E3A5F] bg-white shadow-sm"
                        : "border-gray-200 bg-white hover:bg-gray-50"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-gray-500 shrink-0" />
                      <span className="font-medium text-gray-900 truncate">
                        {t.name}
                      </span>
                    </div>
                    {t.description && (
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                        {t.description}
                      </p>
                    )}
                  </button>
                ))}
              </div>
            ))
          )}
        </aside>

        {/* Form builder */}
        <section className="lg:col-span-4 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Fill in</h2>
          {!selected ? (
            <div className="rounded-lg bg-white p-6 border border-gray-200 text-sm text-gray-500">
              Select a template to get started.
            </div>
          ) : (
            <div className="rounded-lg bg-white p-5 border border-gray-200 space-y-4">
              <div>
                <h3 className="font-medium text-gray-900">{selected.name}</h3>
                {selected.description && (
                  <p className="text-xs text-gray-500 mt-1">
                    {selected.description}
                  </p>
                )}
              </div>

              {Object.entries(selected.variables).map(([name, spec]) => (
                <div key={name} className="space-y-1">
                  <label className="text-xs font-medium text-gray-700">
                    {spec.label}
                    {spec.required && (
                      <span className="text-red-500 ml-0.5">*</span>
                    )}
                  </label>
                  {spec.type === "textarea" ? (
                    <textarea
                      className="w-full h-24 rounded-md border border-gray-300 p-2 text-sm focus:border-[#1E3A5F] focus:ring-1 focus:ring-[#1E3A5F] outline-none resize-none"
                      value={values[name] || ""}
                      onChange={(e) =>
                        setValues((p) => ({ ...p, [name]: e.target.value }))
                      }
                    />
                  ) : (
                    <input
                      type={
                        spec.type === "number"
                          ? "number"
                          : spec.type === "date"
                            ? "date"
                            : "text"
                      }
                      className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-[#1E3A5F] focus:ring-1 focus:ring-[#1E3A5F] outline-none"
                      value={values[name] || ""}
                      onChange={(e) =>
                        setValues((p) => ({ ...p, [name]: e.target.value }))
                      }
                    />
                  )}
                </div>
              ))}

              <button
                onClick={handleGenerate}
                disabled={generating}
                className="w-full rounded-md bg-[#1E3A5F] px-4 py-2 text-white text-sm font-medium hover:bg-[#152a45] disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {generating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
                Generate
              </button>
            </div>
          )}
        </section>

        {/* Preview */}
        <section className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Preview</h2>
            {rendered && (
              <button
                onClick={handleSendForReview}
                disabled={reviewing}
                className="rounded-md bg-emerald-600 px-3 py-1.5 text-white text-xs font-medium hover:bg-emerald-700 disabled:opacity-50 flex items-center gap-1"
              >
                {reviewing && <Loader2 className="h-3 w-3 animate-spin" />}
                Send to Review
              </button>
            )}
          </div>
          {!rendered ? (
            <div className="rounded-lg bg-white p-6 border border-gray-200 text-sm text-gray-500">
              Generated contract preview will appear here.
            </div>
          ) : (
            <pre className="rounded-lg bg-white p-5 border border-gray-200 text-xs text-gray-800 whitespace-pre-wrap font-mono max-h-[70vh] overflow-auto">
              {rendered}
            </pre>
          )}
        </section>
      </div>
    </main>
  );
}
