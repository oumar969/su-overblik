# SU Overblik – webudgave

Statisk brugerflade med lokal beregning; input sendes ikke til en backend og gemmes ikke.
Åbn dist/index.html direkte i en browser eller servér dist med en lokal HTTP-server.

Beregninger: dist/calculator.js bruger heltalsøre og samme månedlige antagelser som Python.
Kør verify_web.py i projektets overordnede mappe for fem paritetskontroller.

Bo forklarer låneoptagelse, renter i ventetiden og budgetreserve med brugerens aktuelle scenarie.
Formularen kræver en eksplicit beregning, og ændringer markeres, indtil resultatet opdateres.

WebMCP: calculate_su_scenario er valideret i den lokale browser med gyldigt og ugyldigt input.
Den bruger samme beregning og opdaterer samme formular og resultater.

Figur: dist/guide.png genereret med OpenAI imagegen (built-in) 21. september 2026.
Prompt: Exactly one original friendly cobalt-blue little anthropomorphic book character,
with simple eyes, small arms and sneakers, holding a small yellow pencil. Warm approachable
young-adult editorial 3D clay illustration, polished soft rounded forms. Full body, centered
square with comfortable margins. Genuinely transparent background. Soft studio lighting,
cheerful and reassuring. No text, logos, watermark, other objects or characters.

Satser og kilder er dokumenteret i brugerfladen og i hovedprojektets satser.json.
Webversionen er et estimat, ikke en officiel plan eller en ML-risikovurdering.

## Læring og scenarier

- Hvad nu hvis: lavere lån, et ekstra studieår eller højere rente; alle tager udgangspunkt i plan A.
- Plan A kan fastlåses fra senest beregnede tal; plan B følger formular og scenarier.
- Bo har tre kapitler og forklarer aktuelle regnestykker.
- Quizzen bruger et separat eksempel, uafhængigt af brugerens budget.
- ML-laboratoriet bruger en faktisk trænet regression, 4.000 træningsscenarier
  og 1.000 testscenarier. Se ml/MODEL_CARD.md og ml/evaluation.json.
- CSV, modelkort og træningskode kan downloades fra laboratoriet.
  Downloadet kode kræver NumPy 2.3.5 og skriver til ml-output ved siden af filen.

ML er kun en illustration af efterligning; alle produktresultater bruger
den præcise beregner. Der er ingen virkelig betalingsrisikomodel.
