import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Projects Dashboard | Juan David Cano",
  description: "Interactive portfolio dashboard of Juan David Cano's civil engineering & CAD/BIM projects.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-bg text-gray-100">{children}</body>
    </html>
  );
}
