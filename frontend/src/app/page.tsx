import Link from "next/link";
import { Scale } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-white px-4">
      <Scale className="h-16 w-16 text-[#1E3A5F] mb-6" />
      <h1 className="text-4xl font-bold text-[#1E3A5F] mb-4">DClaw Legal</h1>
      <p className="text-lg text-gray-600 mb-8">AI contract review & case law research</p>
      <Link
        href="/dashboard"
        className="rounded-md bg-[#1E3A5F] px-6 py-3 text-white font-medium hover:bg-[#152a45] transition-colors"
      >
        Open Dashboard
      </Link>
    </main>
  );
}
