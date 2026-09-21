# Modelkort: SU-regression

## Formål
Et undervisningseksperiment til porteføljen: Kan en trænet regression efterligne
beregnerens gæld ved studieslut? Modellen påvirker ikke brugerens låneplan.
Den er IKKE en model for misligholdelse, betalingsproblemer eller overraskelse.

## Data og reproduktion
5.000 simulerede scenarier genereres med NumPy 2.3.5 og seed 42.
Månedligt lån: heltal 0–3.799 kr.; studiemåneder: 1–84; startgæld: 0–100.000 kr.
Alle input trækkes uafhængigt fra en diskret uniform fordeling. Fordelingerne
er valgte modelantagelser og er ikke empirisk kalibreret til danske studerende.
Facit: 4 % årlig rente divideret med 12, månedsvis tilskrivning efter nyt lån,
afrundet til øre. Lånet tilføjes ved månedens begyndelse.

Kør `python -m pip install -r ml/requirements.txt` og `python ml/train_model.py`
fra web-mappen. Det genskaber data, modelparametre og evaluering.

## Træning og test
Tilfældig opdeling: 4.000 træning / 1.000 test. Inputskalaer og gennemsnit
estimeres kun på træningsdata. Seks features: lån, måneder, startgæld,
lån × måneder, startgæld × måneder og lån × måneder². Lineær regression
med intercept, løst med mindste kvadraters metode. Ingen hyperparametertuning.
Negative forudsigelser klippes til nul i både evaluering og webvisning.

Baseline: altid gennemsnittet af træningssættets målvariabel.
MAE på test: 103,49 kr. RMSE: 138,83 kr. Største fejl: 651,84 kr.
Baseline-MAE: 70.579,03 kr. Præcis beregner: 0 kr. ift. det genererede facit.

## Konklusion og begrænsninger
Modellen efterligner facit, men forbedrer det ikke. Den præcise beregner er
både gennemskuelig og tilstrækkeligt hurtig og bruges derfor i produktet.
Testresultater beskriver kun denne syntetiske fordeling; de siger ikke noget
om personers økonomi. Testfejl er ikke en garanteret fejlgrænse for nye input.
Webben afviser ML-forudsigelser uden for træningsområdets grænser.
Fremtidige regelændringer kræver en opdateret beregner, data og træning.

## Verifikation
15 eksisterende Python-tests, fem web/Python-paritetscases og en uafhængig
kontrol af artefaktens målvariable, testsplit og rapporterede MAE.
Browserkontrol af scenarier, sammenligning, quiz og regnestykker.
