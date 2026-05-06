import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DClaw Legal",
  description: "AI contract review & case law research",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
