# SU Overblik

Et interaktivt værktøj, der hjælper studerende med at forstå SU-lån, renter,
tilbagebetaling og budget. Bo, en illustreret guide, forklarer tallene undervejs.

## Det kan projektet

- Beregne gæld og tilbagebetaling måned for måned.
- Sammenligne to planer og prøve mindre lån, længere studietid eller højere rente.
- Vise gældsgraf, budget, konkrete regnestykker og en læringsquiz.
- Demonstrere en trænet ML-model i et særskilt laboratorium med 5.000 simulerede scenarier.

**ML er et undervisningseksperiment, ikke en model for betalingsrisiko.**
Produktet bruger den præcise beregner. Modellen efterligner gæld ved studieslut
og evalueres på 1.000 testscenarier: MAE 103,49 kr. Se [modelkortet](web/ml/MODEL_CARD.md).
Alle beregninger er estimater med dokumenterede antagelser.

## Prøv brugerfladen lokalt

Åbn `web/dist/index.html` direkte i din browser. Ingen installation er nødvendig.
Alternativt: `python -m http.server 8000 --directory web/dist` og åbn
http://localhost:8000. Brugerens tal beregnes i browseren og sendes ikke til en backend.

## Projektstruktur

| Mappe / fil | Formål |
| --- | --- |
| `su_beregner.py`, `tilbagebetaling.py`, `budget.py` | Python-beregner |
| `satser.json` | Dokumenterede satser og kilder |
| `web/dist/` | Brugerflade, illustration og browserberegning |
| `web/ml/` | Reproducerbar træning, evaluering og modelkort |
| `test_*.py`, `verify_web.py` | Tests og kontrol af web/Python-overensstemmelse |

## Test og ML-træning

Python 3.10+ og Node.js kræves til alle kontroller. Selve beregneren bruger
kun Python-standardbiblioteket. ML-træning og ML-testen kræver NumPy:

```sh
python -m pip install -r requirements-dev.txt
python -m unittest -v
python verify_web.py
python web/ml/train_model.py
```

Der er 16 tests og fem sammenligninger af browserberegningen med Python.
GitHub Actions kører dem ved push og pull requests.
Den private Sites-demo kræver ejeradgang; den lokale udgave kan prøves uden login.

---

# SU-låneberegner

Første version beregner et estimat for gæld ved studieslut og sammenligner med
op til 500 kr. mindre i månedligt lån. Kræver Python 3.10 eller nyere, ingen ekstra pakker.

## Kør et eksempel

```powershell
python su_beregner.py --gaeld 0 --laan 2000 --start 2026-09 --slut 2029-06 --csv eksempel.csv
```

Erstat tallene med dine egne. `--gaeld` er saldo inklusive eksisterende renter
ved begyndelsen af startmåneden. Start- og slutmåned medregnes begge.
Lån optages i hver måned af perioden. Ved et ophold før nye lån starter kan
denne version ikke særskilt angive saldoens dato og første lånemåned.

Resultatet viser nye lån, renter i beregningsperioden og samlet slutgæld.
Startgælden kan allerede indeholde renter; derfor kaldes nye lån ikke samlet
oprindeligt lånt beløb. CSV er semikolonsepareret med decimalkomma.

## Kilder og antagelser

Officielle oplysninger kontrolleret 20. september 2026 og gemt i `satser.json`:

- [SU.dk: satser](https://www.su.dk/satser/satser-for-su-laan): almindeligt lån op til 3.799 kr./måned i 2026.
- [SU.dk: renter](https://www.su.dk/su-laan/naar-du-skal-betale-laan-tilbage/renter-paa-dit-su-laan): 4 % årlig rente under studiet; løbende renter og renters rente.

**Modelantagelser:** Lånet tilføjes først på måneden. Månedens rente er
(saldo + nyt lån) × 0,04 / 12, afrundet til øre. Disse detaljer om timing,
renteomregning og afrunding er vores approximation; de citerede sider fastslår
ikke den præcise tekniske bogføringsmetode. Resultatet er derfor et estimat,
ikke Udbetaling Danmarks officielle gældsopgørelse.

Vi holder lånebeløbet og studierenten faste i hele scenariet. 2026-loftet
bruges også som scenariegrænse uden for 2026, hvor programmet giver besked.
Det er ikke en påstand om fremtidige eller historiske satser. Retten til lån,
SU-klip, studieskift, supplerende lån indgår ikke i studieberegningen.
Hele perioden antages at være under uddannelse.

## Kontrol

```powershell
python -m unittest -v
```

Kontrollerne dækker håndberegnede renteeksempler, årsskifte, renters rente,
saldoafstemning, nulbeløb og ugyldige input. De validerer modellen, ikke en
overensstemmelse med en officiel konto.

Næste trin: afklare præcis rentebogføring og tilføje
budget. Der bruges ingen persondata eller ML.

På denne computer kan du også køre: `.\start.ps1 -Laan 2000 -Start 2026-09 -Slut 2029-06`. Scriptet finder den medfølgende Python, hvis python ikke findes på PATH.


## Tilbagebetaling

Samme kommando viser nu også ventetid, renter, ydelse inklusive gebyr,
forventet gældfri måned og samlet tilbagebetaling. Regler kontrolleret
20. september 2026 hos [Borger.dk](https://www.borger.dk/oekonomi-skat-su/gaeld/studiegaeld/til-dig-med-su-laan).

- Start i januar i afslutningsåret + 2.
- Normalt betaling hver anden måned; månedlig betaling kan vælges.
- Maksimal løbetid 7 år under 40.000 kr., derefter et ekstra år pr.
  20.000 kr. op til 15 år fra 180.000 kr.
- Minimum 200 kr. pr. ordinær ydelse, dog mindre ved sidste restbetaling.
- Aktuel rente efter studiet 2,85 % fra juli 2026, aktuelt gebyr 15 kr. pr. opkrævning.

Modellen vælger løbetid ud fra saldo ved starten af første betalingsår.
Rente og gebyr fastholdes gennem hele scenariet, også i ventetiden. Det er
ikke en prognose for fremtidige satser eller en historisk renteberegning.
Rente efter studiet anvendes fra måneden efter sidste studiemåned.
Betaling placeres ved månedens slutning; den officielle forfaldsdag kan afvige.
Ydelsen beregnes som en annuitet over den valgte periode. Sidste ydelse
udligner saldoen og eventuelle øreafrundinger. Gebyr betales separat og
forrentes ikke. Rentefradrag, misligholdelse og udsættelser indgår ikke.
En fremtidig renteændring kræver en særskilt model; et nyt scenarie beregner
her en ny startydelse. I en eksisterende officiel plan kan en renteændring
ændre løbetiden uden at ændre ydelsen. Udbetaling Danmark fastsætter planen.

Prøv månedlig betaling eller en anden fast rente:

```powershell
.\start.ps1 -Laan 2000 -Start 2026-09 -Slut 2029-06 -Interval 1 -RenteEfter '4,5'
```

Python-kommandoen understøtter også `--betaling-csv tilbagebetaling.csv` til
månedsoversigten efter studiet. `--csv` gemmer fortsat kun studieperioden.
11 automatiske tests kontrollerer blandt andet grænser for løbetid,
ventetid, nulrente, minimumsydelse, sidste betaling og saldoafstemning.

## Budget under tilbagebetalingen

Angiv din forventede månedlige indkomst efter skat og dine samlede månedlige
udgifter på det tidspunkt, hvor du betaler tilbage. Begge felter skal angives;
udelades begge, fungerer beregneren som før. Eksempel med fiktive budgettal:

```powershell
.\start.ps1 -Laan 2000 -Start 2026-09 -Slut 2029-06 -Netto 22000 -Udgifter 16000
```

Udgifter skal inkludere bolig, mad, transport, andre lån og øvrigt forbrug,
men ikke dette SU-lån. Årlige udgifter kan fordeles over 12 måneder.
Programmet viser beløbet tilbage efter en månedlig reserve til SU-lånet
inklusive gebyr. Reserven er største beregnede opkrævning divideret med
betalingsintervallet; det er et forsigtigt budgetbeløb, ikke gennemsnittet
over hele lånets levetid. Der vises også beløbet tilbage i måneden med den
største opkrævning uden brug af opsparet reserve. De to beløb er alternative
visninger og skal ikke trækkes fra budgettet samtidig.

Ved nul gæld opkræves intet gebyr. Ved nul indkomst vises ingen procentandel.
Negative budgetresultater vises som underskud. Dette er regnestykker baseret
på brugerens forventninger, ikke en ML-model eller en valideret risikoscore.
Der er nu 15 automatiske tests. Næste produkttrin er en brugerflade; derefter
et særskilt, tydeligt mærket ML-eksperiment med simulerede data.

## Brugerflade med Bo

Webudgaven findes i `web/dist/index.html` og kan åbnes direkte i en browser.
Den indeholder formular, gældsgraf, budget, sammenligning og Bo, en illustreret
bogfigur med tre forklaringer, der bruger det aktuelle scenaries tal.
Beregningen kører lokalt i browseren uden at sende indtastede beløb til en server.

Kør `python verify_web.py` for at sammenligne fem webscenarier med Python.
Webudgaven har sit eget Git-repository i `web` til Sites-udgivelsen.

