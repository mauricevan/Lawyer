import type { Metadata } from "next";
import "@/styles/tokens.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "EU-regels helder uitgelegd — EUR-Lex",
  description:
    "Stel uw vraag over EU-wetgeving en ontvang een begrijpelijk antwoord op basis van officiële EUR-Lex-bronnen",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="nl">
      <body>{children}</body>
    </html>
  );
}
