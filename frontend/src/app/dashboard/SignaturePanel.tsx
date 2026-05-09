"use client";

import { useState } from "react";
import { Loader2, PenLine } from "lucide-react";
import { toast } from "sonner";
import { type ContractReview, sendForSignature } from "@/lib/api";

interface Props {
  review: ContractReview;
  onUpdated: (next: ContractReview) => void;
}

const STATUS_STYLES: Record<string, string> = {
  sent: "bg-blue-100 text-blue-800",
  delivered: "bg-indigo-100 text-indigo-800",
  signed: "bg-emerald-100 text-emerald-800",
  declined: "bg-rose-100 text-rose-800",
  voided: "bg-gray-100 text-gray-700",
};

export function SignaturePanel({ review, onUpdated }: Props) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [sending, setSending] = useState(false);

  async function handleSend() {
    if (!email.trim() || !name.trim()) return;
    setSending(true);
    try {
      const result = await sendForSignature(review.id, email.trim(), name.trim());
      onUpdated({
        ...review,
        envelope_id: result.envelope_id,
        signer_email: email.trim(),
        signature_status: result.signature_status,
      });
      toast.success("Sent for signature", {
        description: `Envelope ${result.envelope_id}`,
      });
    } catch (err) {
      toast.error("Send failed", {
        description: err instanceof Error ? err.message : "",
      });
    } finally {
      setSending(false);
    }
  }

  if (review.envelope_id) {
    const status = review.signature_status || "sent";
    const pillClass = STATUS_STYLES[status] || "bg-gray-100 text-gray-700";
    return (
      <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
          Signature
        </h3>
        <div className="flex items-center gap-3 text-sm">
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${pillClass}`}>
            {status}
          </span>
          <span className="text-gray-600">{review.signer_email}</span>
        </div>
        <p className="text-xs text-gray-400 mt-2 font-mono break-all">
          {review.envelope_id}
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-white p-6 shadow-sm border border-gray-200">
      <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
        Send for Signature
      </h3>
      <div className="space-y-2">
        <input
          type="text"
          placeholder="Signer name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-[#1E3A5F] focus:ring-1 focus:ring-[#1E3A5F] outline-none"
        />
        <input
          type="email"
          placeholder="signer@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-md border border-gray-300 p-2 text-sm focus:border-[#1E3A5F] focus:ring-1 focus:ring-[#1E3A5F] outline-none"
        />
        <button
          onClick={handleSend}
          disabled={sending || !email.trim() || !name.trim()}
          className="w-full rounded-md bg-[#1E3A5F] px-4 py-2 text-white text-sm font-medium hover:bg-[#152a45] disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {sending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <PenLine className="h-4 w-4" />
          )}
          Send via DocuSign
        </button>
      </div>
    </div>
  );
}
