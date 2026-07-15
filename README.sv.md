# Python-kurs

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad är det här?
En praktisk Python-kurs steg för steg (perfekt för ~14 år). Varje kapitel har:
- Ett tydligt mål
- Korta exempel du kan köra
- Små utmaningar med TODOs och tips
- Vanliga misstag (så du inte fastnar länge)

## Så använder du den (ingen stress)
1. Börja med **Kapitel 1** och gör datorn redo.
2. Läs ett kapitel och kör exemplen.
3. Gör övningarna: fel är en del av lärandet.
4. Om du fastnar, kolla **Vanliga misstag** i kapitlet.

## Välj en lärväg
Den numrerade innehållslistan är fortfarande den stabila referensordningen och innehåller kapitellänkarna för varje väg. En lärväg visar vad som krävs och var du tryggt kan stanna; valfria förhandsblickar och hero-material blockerar aldrig nästa grundläggande kontrollpunkt. Har du redan erfarenhet kan du öppna den namngivna kontrollpunkten via listan, göra självbedömningen och börja på nästa väg om du uppfyller kriterierna.

- **Grundläggande bas · 14–21 pass på 45–70 min.** Förkunskaper: inga. Slutför Kapitel 1–11, sedan grundvägen i Kapitel 26 om iteration och därefter Kapitel 12. Resultat: bygg och förklara ett litet lokalt program med data, beslut, upprepning, iterationsverktyg, funktioner och en klass. Du kan stanna tryggt efter varje kontrollpunkt; de professionella och avancerade delarna i Kapitel 26 är valfria.
- **Praktisk Python · 6–10 pass på 50–80 min.** Förkunskap: kontrollpunkten i Kapitel 12. Fortsätt genom Kapitel 13–18 och avsluta ”Kontrollpunkt och bedömningsmatris” i Kapitel 18. Resultat: strukturera, lagra, testa och återskapa ett lokalt projekt. Kapitel 18 är en fullständig stoppunkt.
- **System-Python · 5–9 pass plus nätverkslabben.** Förkunskap: kontrollpunkten i Kapitel 18. Fortsätt genom Kapitel 19–23 och avsluta ”Bedömningsmatris” i Kapitel 23. Resultat: diagnostisera avgränsade lokala program för HTTP, loggning, asynkroni, introspektion och nätverk. Du kan stanna vid Kapitel 22 före den längre labben.
- **Brygga till gradvis typning · 4–7 pass på 50–75 min.** Förkunskaper: Kapitel 15, 18, 22 och 26. Följ Kapitel 27 genom dess grundläggande och professionella kontrollpunkter; labben med ett versionsbundet kontrollverktyg är valfri och kräver medveten installation av verktyget. Resultat: dokumentera och kontrollera typade gränser statiskt utan att blanda ihop annotationer med körtidsvalidering. Du kan stanna efter körtidsvägen.
- **Långsgående professionellt slutprojekt · självständigt stoppbara etapper.** Börja Kapitel 28:s grundetapp på 2–3 pass efter Kapitel 12. Dess praktiska etapp på 4–6 pass följer Kapitel 13–18 och kontrollpunkten för loggning i Kapitel 20. Den valfria systemetappen på 2–3 pass följer Kapitel 21 och 23; den separata paketeringsetappen på 2–3 pass följer den praktiska etappen och Kapitel 15–16 med exakt byggindata installerad. Resultat: utveckla en lokal orderhanterare från en oföränderlig tjänst i minnet till ett transaktionellt CLI och verifiera sedan valfritt en begränsad loopback-adapter och en distribuerbar artefakt. Varje slutförd etapp är en säker stoppunkt; ingenting laddas upp eller driftsätts.
- **Valfri hero-väg Python + C++ · 12–18 fokuserade pass.** Förkunskaper: Kapitel 16 och den professionella kontrollpunkten i Kapitel 27, som omfattar de tidigare bryggorna för moduler, testning, introspektion, iteration och typning. Följ Kapitel 24 och slutför projektet med en deklarerad testad verktygskedja. Resultat: bygg och verifiera ett typat C++-understött Python-tillägg. Rust krävs inte.
- **Valfri hero-väg Python + Rust · 12–18 fokuserade pass.** Förkunskaper: Kapitel 16 och den professionella kontrollpunkten i Kapitel 27, som omfattar de tidigare bryggorna för moduler, testning, introspektion, iteration och typning. Följ Kapitel 25 och slutför verifieringen med ett enda kommando i en deklarerad testad verktygskedja. Resultat: bygg och verifiera ett typat Rust-understött Python-tillägg. C++ krävs inte.
- **Fristående bilagor · 1–2 pass vardera.** CLI-bilagan börjar efter Kapitel 18 och 20. Algoritmbilagan börjar efter Kapitel 5, 7, 10 och 18. Varje bilaga har en egen kontrollpunkt och stoppunkt.

## Innehåll
Varje kapitel har en språkväljare högst upp.
- [Kapitel 1 · Introduktion och miljö](chapter-01-introduction/README.sv.md)
- [Kapitel 2 · Variabler och enkla datatyper](chapter-02-variables/README.sv.md)
- [Kapitel 3 · Listor](chapter-03-lists/README.sv.md)
- [Kapitel 4 · Ordböcker (nyckel–värde)](chapter-04-dictionaries/README.sv.md)
- [Kapitel 5 · Mängder (sets) och medlemskap](chapter-05-sets/README.sv.md)
- [Kapitel 6 · Tuples och immutabilitet](chapter-06-tuples/README.sv.md)
- [Kapitel 7 · Köer och stackar med `collections.deque`](chapter-07-queues/README.sv.md)
- [Kapitel 8 · Villkor, ternary och logik](chapter-08-conditionals/README.sv.md)
- [Kapitel 9 · Indata och säker validering](chapter-09-input/README.sv.md)
- [Kapitel 10 · Loopar och komplexitet](chapter-10-loops/README.sv.md)
- [Kapitel 11 · Funktioner och funktioner som argument](chapter-11-functions/README.sv.md)
- [Kapitel 12 · OOP: klasser och objekt](chapter-12-oop/README.sv.md)
- [Kapitel 13 · Filer och strömmar (streams)](chapter-13-files/README.sv.md)
- [Kapitel 14 · Undantag (exceptions): från nybörjare till hjälte](chapter-14-exceptions/README.sv.md)
- [Kapitel 15 · Moduler, paket och struktur](chapter-15-modulos/README.sv.md)
- [Kapitel 16 · Virtuella miljöer och beroenden](chapter-16-entornos/README.sv.md)
- [Kapitel 17 · Lätt persistens: CSV/JSON och SQLite](chapter-17-persistencia/README.sv.md)
- [Kapitel 18 · Testning med pytest](chapter-18-testing/README.sv.md)
- [Kapitel 19 · HTTP och API:er med Python](chapter-19-http/README.sv.md)
- [Kapitel 20 · Logging och konfiguration](chapter-20-logging/README.sv.md)
- [Kapitel 21 · Vänlig concurrency: intro till `asyncio`](chapter-21-async/README.sv.md)
- [Kapitel 22 · Introspektion: Python i detektivläge](chapter-22-introspection/README.sv.md)
- [Kapitel 23 · Nätverksprogrammering med Python](chapter-23-network-programming/README.sv.md)
- [Kapitel 24: Integration mellan Python och C++ — Från noll till hero](chapter-24-python-cpp-integration/README.sv.md)
- [Kapitel 25 · Python och Rust: från första crate till verifierad wheel](chapter-25-python-rust-integration/README.sv.md)
- [Kapitel 26 · Iteration, comprehensions, iteratorer och generatorer](chapter-26-iteration-generators/README.sv.md)
- [Kapitel 27 · Gradvis typning: körtidsgränser och statisk evidens](chapter-27-python-typing/README.sv.md)
- [Kapitel 28 · Professionellt slutprojekt: ett projekt i fyra etapper](chapter-28-professional-capstone/README.sv.md)
- [Bilaga A · Bygg CLI‑verktyg med standardbiblioteket](appendix-cli-parser/README.sv.md)
- [Bilaga B · Grundläggande algoritmer: sökning i Python](appendix-algorithms/README.sv.md)

## Dedikation
Till mina barn Noor, Frej och Taha: den här boken är till er. Jag hoppas att de här sidorna ger er verktyg att lära er livets intressanta saker, även om ni måste upptäcka dem utan mig. Varje exempel och övning är tänkt att hjälpa er utforska med nyfikenhet och mod. Jag älskar er.

## Licens
Materialet publiceras under [Creative Commons Attribution-ShareAlike 4.0 International](LICENSE), så att vem som helst kan studera, anpassa och dela det – och behålla samma frihet för andra.

<!-- bookcheck: visual-text-equivalent -->
<p align="center">
  <img src="icons/cc-by-sa.svg" alt="CC BY-SA 4.0" width="200">
</p>
