import type { Metadata } from "next";
import { Hanken_Grotesk } from "next/font/google";
import "./globals.css";

const hanken = Hanken_Grotesk({
  subsets: ["latin"],
  variable: "--font-hanken",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Projects Dashboard | Juan David Cano",
  description: "Interactive portfolio dashboard of Juan David Cano's civil engineering & CAD/BIM projects.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={hanken.variable}>
      <body className="bg-bg text-gray-100">{children}</body>
    </html>
  );
}
