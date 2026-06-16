import type { Metadata } from "next";
import { Sidebar } from "@/components/layout/Sidebar";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "YASINT",
  description: "YASINT — pasif OSINT kişi analiz ve profil raporu",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body className="min-h-screen bg-bg-primary">
        <Sidebar />
        <main className="ml-60 min-h-screen p-6 md:p-8 max-md:ml-0 max-md:pt-16">
          {children}
        </main>
      </body>
    </html>
  );
}
