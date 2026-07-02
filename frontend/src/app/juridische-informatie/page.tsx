import Link from "next/link";
import { PRODUCT_LIMITATIONS } from "@/content/legalDisclaimers";
import { LegalFooter } from "@/components/LegalFooter";
import styles from "./page.module.css";

export default function JuridischeInformatiePage() {
  return (
    <main className={`container ${styles.page}`}>
      <header>
        <h1>Juridische informatie</h1>
        <p>
          Dit platform helpt bij EU-juridisch onderzoek. Het vervangt geen professioneel
          juridisch advies.
        </p>
      </header>

      <section aria-labelledby="escalation-heading">
        <h2 id="escalation-heading">Escalatiepad naar een jurist</h2>
        <ol>
          <li>Controleer de getoonde EUR-Lex-bronnen en versie-informatie.</li>
          <li>Formuleer uw vraag opnieuw met specifieke CELEX- of artikelverwijzing.</li>
          <li>Raadpleeg bij dossier-impact een advocaat, jurist of compliance officer.</li>
          <li>Gebruik feedback in de chat om bron- of kwaliteitsproblemen te melden.</li>
        </ol>
        <p>
          Voor urgente zaken: neem direct contact op met uw interne legal counsel of
          externe advocaat.
        </p>
      </section>

      <section aria-labelledby="limitations-heading">
        <h2 id="limitations-heading">Beperkingen en uitzonderingen</h2>
        <ul>
          {PRODUCT_LIMITATIONS.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <p>
        <Link href="/">Terug naar de zoekpagina</Link>
      </p>

      <LegalFooter />
    </main>
  );
}
