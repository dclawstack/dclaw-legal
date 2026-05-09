"use client";

import { useEffect, useRef, useState } from "react";
import { CheckCircle2, FileText, Loader2, Scale, Upload, XCircle } from "lucide-react";
import { toast } from "sonner";
import { type BatchJob, getBatch, uploadBatch } from "@/lib/api";

export default function BatchPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [job, setJob] = useState<BatchJob | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  function startPolling(jobId: string) {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const fresh = await getBatch(jobId);
        setJob(fresh);
        if (
          fresh.status !== "pending" &&
          fresh.status !== "processing"
        ) {
          if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
          }
        }
      } catch {
        /* keep polling */
      }
    }, 1500);
  }

  async function handleUpload() {
    if (files.length === 0) return;
    setUploading(true);
    try {
      const created = await uploadBatch(files);
      setJob(created);
      setFiles([]);
      toast.success("Batch queued", {
        description: `${created.total} files`,
      });
      startPolling(created.id);
    } catch (err) {
      toast.error("Upload failed", {
        description: err instanceof Error ? err.message : "",
      });
    } finally {
      setUploading(false);
    }
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragActive(false);
    const dropped = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...dropped]);
  }

  const progress = job
    ? job.total === 0
      ? 0
      : Math.round(((job.completed + job.failed) / job.total) * 100)
    : 0;

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-[#1E3A5F] px-6 py-4 flex items-center gap-3">
        <Scale className="h-6 w-6 text-white" />
        <h1 className="text-xl font-semibold text-white">DClaw Legal — Batch</h1>
        <a
          href="/dashboard"
          className="ml-auto text-sm text-white/80 hover:text-white"
        >
          Dashboard →
        </a>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-8 space-y-8">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          className={`rounded-lg border-2 border-dashed p-10 text-center transition-colors ${
            dragActive
              ? "border-[#1E3A5F] bg-blue-50"
              : "border-gray-300 bg-white"
          }`}
        >
          <Upload className="h-10 w-10 text-gray-400 mx-auto mb-3" />
          <p className="text-sm text-gray-600 mb-2">
            Drag and drop contract files here, or
          </p>
          <label className="inline-block cursor-pointer rounded-md bg-[#1E3A5F] px-4 py-2 text-white text-sm font-medium hover:bg-[#152a45]">
            Browse files
            <input
              type="file"
              multiple
              accept=".txt,.zip"
              className="hidden"
              onChange={(e) => {
                if (e.target.files) {
                  setFiles((prev) => [...prev, ...Array.from(e.target.files!)]);
                }
              }}
            />
          </label>
          <p className="text-xs text-gray-400 mt-3">
            .txt or .zip — max 25 MB total
          </p>
        </div>

        {files.length > 0 && (
          <div className="rounded-lg bg-white border border-gray-200 p-4">
            <h2 className="text-sm font-medium text-gray-700 mb-3">
              Queued: {files.length} file(s)
            </h2>
            <ul className="space-y-1 mb-4">
              {files.map((f, i) => (
                <li
                  key={i}
                  className="flex items-center gap-2 text-xs text-gray-600"
                >
                  <FileText className="h-3 w-3" />
                  <span className="flex-1 truncate">{f.name}</span>
                  <span className="text-gray-400">
                    {(f.size / 1024).toFixed(1)} KB
                  </span>
                  <button
                    onClick={() =>
                      setFiles((prev) => prev.filter((_, idx) => idx !== i))
                    }
                    className="text-gray-400 hover:text-red-600"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full rounded-md bg-emerald-600 px-4 py-2 text-white text-sm font-medium hover:bg-emerald-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {uploading && <Loader2 className="h-4 w-4 animate-spin" />}
              Upload and review
            </button>
          </div>
        )}

        {job && (
          <div className="rounded-lg bg-white border border-gray-200 p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-medium text-gray-900">{job.name}</h2>
              <span
                className={`text-xs px-2 py-1 rounded-full ${
                  job.status === "completed"
                    ? "bg-emerald-100 text-emerald-700"
                    : job.status === "failed"
                      ? "bg-rose-100 text-rose-700"
                      : job.status === "partial"
                        ? "bg-amber-100 text-amber-700"
                        : "bg-blue-100 text-blue-700"
                }`}
              >
                {job.status}
              </span>
            </div>

            <div>
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>
                  {job.completed + job.failed} / {job.total}
                </span>
                <span>{progress}%</span>
              </div>
              <div className="h-2 rounded-full bg-gray-200 overflow-hidden">
                <div
                  className="h-2 bg-[#1E3A5F] transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            <table className="w-full text-xs">
              <thead className="text-left text-gray-500">
                <tr>
                  <th className="py-2">File</th>
                  <th className="py-2">Status</th>
                  <th className="py-2">Review</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {job.items.map((item) => (
                  <tr key={item.id}>
                    <td className="py-2 truncate max-w-xs">{item.filename}</td>
                    <td className="py-2">
                      {item.status === "completed" ? (
                        <span className="inline-flex items-center gap-1 text-emerald-700">
                          <CheckCircle2 className="h-3 w-3" />
                          completed
                        </span>
                      ) : item.status === "failed" ? (
                        <span className="inline-flex items-center gap-1 text-rose-700">
                          <XCircle className="h-3 w-3" />
                          failed
                        </span>
                      ) : (
                        <span className="text-blue-700">{item.status}</span>
                      )}
                    </td>
                    <td className="py-2">
                      {item.contract_review_id ? (
                        <a
                          href={`/dashboard`}
                          className="text-[#1E3A5F] hover:underline"
                        >
                          view
                        </a>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
