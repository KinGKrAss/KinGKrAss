import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Z1 Löwenherz OS",
  description: "Dashboard für Immobilien, Energie, Finanzen und Dokumente",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  );
}
