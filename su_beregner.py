"""SU-lån under studiet: en månedlig scenarieberegning uden eksterne pakker."""
import argparse
import csv
import json
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

SATSER = json.loads(Path(__file__).with_name("satser.json").read_text(encoding="utf-8"))
ORE = Decimal("0.01")


def beloeb(value):
    try:
        result = Decimal(str(value).replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError("Beløb skal være tal, fx 1500 eller 1500,50.") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("Beløb skal være endelige og mindst 0.")
    try:
        rounded = result.quantize(ORE)
    except InvalidOperation as exc:
        raise ValueError("Beløbet er for stort til beregningen.") from exc
    if result != rounded:
        raise ValueError("Beløb må højst have to decimaler.")
    return result


def maaned(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", value):
        raise ValueError("Datoer skal skrives ÅÅÅÅ-MM, fx 2026-09.")
    year, month = map(int, value.split("-"))
    if year < 1:
        raise ValueError("Årstallet skal være mindst 1.")
    return year * 12 + month - 1


def beregn(gaeld, laan, start, slut):
    """Saldo ved startmånedens begyndelse; begge måneder medregnes.

    Modelantagelse: lån først på måneden, rente 4 % / 12 ved månedens
    slutning, afrundet til øre. Dette er ikke en officiel saldoopgørelse.
    """
    saldo, laan = beloeb(gaeld), beloeb(laan)
    first, last = maaned(start), maaned(slut)
    if last < first:
        raise ValueError("Slutmåneden må ikke ligge før startmåneden.")
    if last - first >= 600:
        raise ValueError("Perioden må højst være 600 måneder.")
    if laan > Decimal(SATSER["almindeligt_laan"]["maks_pr_maaned"]):
        raise ValueError("Denne version bruger 2026-loftet på 3.799 kr. for almindeligt SU-lån.")
    rate = Decimal(SATSER["studierente"]["aarlig"])
    rows = []
    for index in range(first, last + 1):
        year, month = divmod(index, 12)
        interest = ((saldo + laan) * rate / 12).quantize(ORE, rounding=ROUND_HALF_UP)
        saldo += laan + interest
        rows.append({"maaned": f"{year:04d}-{month + 1:02d}", "nyt_laan": laan,
                     "renter": interest, "gaeld": saldo})
    return rows


def kroner(value):
    return f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".") + " kr."


def main():
    parser = argparse.ArgumentParser(description="Estimer din SU-gæld ved studieslut.")
    parser.add_argument("--gaeld", default="0", help="Saldo inklusive renter ved startmånedens begyndelse")
    parser.add_argument("--laan", required=True, help="Fast månedligt lån i kroner")
    parser.add_argument("--start", required=True, help="Første beregnings- og lånemåned, ÅÅÅÅ-MM")
    parser.add_argument("--slut", required=True, help="Sidste studiemåned, ÅÅÅÅ-MM (medregnes)")
    parser.add_argument("--csv", type=Path, help="Gem månedsoversigt som CSV")
    parser.add_argument('--rente-efter', default=None, help='Fast scenarierente efter studiet i procent, fx 4,5')
    parser.add_argument('--interval', type=int, choices=(1, 2), default=2, help='Måneder mellem betalinger')
    parser.add_argument('--betaling-csv', type=Path, help='Gem tilbagebetalingsoversigt')
    parser.add_argument('--netto', help='Forventet månedlig indkomst efter skat under tilbagebetalingen')
    parser.add_argument('--udgifter', help='Månedlige udgifter uden dette SU-lån, inklusive mad og øvrigt forbrug')
    args = parser.parse_args()
    from tilbagebetaling import tilbagebetal
    from budget import beregn_budget
    try:
        if (args.netto is None) != (args.udgifter is None):
            raise ValueError('Angiv både --netto og --udgifter for at beregne budgettet.')
        rows = beregn(args.gaeld, args.laan, args.start, args.slut)
        lower = max(Decimal("0"), beloeb(args.laan) - 500)
        comparison = beregn(args.gaeld, lower, args.start, args.slut)
        repayment = tilbagebetal(rows[-1]['gaeld'], args.slut, args.rente_efter, args.interval)
        budget = beregn_budget(args.netto, args.udgifter, repayment) if args.netto is not None else None
    except (ValueError, InvalidOperation) as exc:
        parser.error(str(exc))
    print("SU-lån – estimat ved studieslut")
    print(f"Periode: {args.start} til {args.slut}, inklusive ({len(rows)} måneder)")
    print("Startgæld:             " + kroner(beloeb(args.gaeld)))
    print("Nye lån i perioden:    " + kroner(sum(r["nyt_laan"] for r in rows)))
    print("Renter i perioden:     " + kroner(sum(r["renter"] for r in rows)))
    print("Gæld ved studieslut:   " + kroner(rows[-1]["gaeld"]))
    print(f"\nMed {kroner(lower)} i lån pr. måned:")
    print("Gæld ved studieslut:   " + kroner(comparison[-1]["gaeld"]))
    print("Reduktion i slutgæld:  " + kroner(rows[-1]["gaeld"] - comparison[-1]["gaeld"]))
    print("Heraf færre renter:    " + kroner(sum(r["renter"] for r in rows) - sum(r["renter"] for r in comparison)))
    print("\nAntagelser: lån først i måneden; månedsrente 4 % / 12; afrunding til øre.")
    print("Fast lånebeløb og studierente under uddannelsen.")
    print("\nTilbagebetaling – scenarie med fast rente på " + str(repayment['rente']).replace('.', ',') + " %")
    if repayment['start']:
        print("Første betalingsmåned: " + repayment['start'])
        print("Renter i ventetiden:   " + kroner(repayment['renter_ventetid']))
        print("Gæld ved årets start:  " + kroner(repayment['startgaeld']))
        print(f"Valgt maksimal løbetid: {repayment['aar']} år (estimat ud fra gæld ved betalingsstart)")
        print(f"Ydelse hver {args.interval}. måned: " + kroner(repayment['ydelse']) + " + " + kroner(repayment['gebyr']) + " gebyr")
        reserve = beregn_budget(0, 0, repayment)['maanedlig_reserve']
        print("Budget pr. måned:      " + kroner(reserve))
        print("Forventet gældfri:     " + repayment['slut'])
        print("Renter efter studiet:  " + kroner(repayment['renter']))
        print("Alle nye renter:       " + kroner(sum(r['renter'] for r in rows) + repayment['renter']))
        print("Gebyrer i alt:         " + kroner(repayment['gebyrer']))
        print("Tilbagebetaling i alt: " + kroner(repayment['samlet_betaling']))
        print("Sidste ydelse kan være mindre. Budgetbeløbet er et månedligt gennemsnit.")
    else:
        print("Ingen gæld at betale tilbage.")
    print("Rente og gebyr holdes faste som scenarie; fremtidige satser er ukendte.")
    print("Betaling modelleres ved månedens slutning. Beløb er før rentefradrag.")
    print("Den faktiske betalingsplan fastsættes af Udbetaling Danmark.")
    if budget is not None:
        print('\nDit budget under tilbagebetalingen – egne forventede tal')
        print('Indkomst efter skat:   ' + kroner(budget['netto']))
        print('Udgifter uden SU-lån:  ' + kroner(budget['udgifter']))
        print('Tilbage før SU-lån:    ' + kroner(budget['foer']))
        print('Afsæt til SU pr. md.:  ' + kroner(budget['maanedlig_reserve']))
        print('Tilbage efter reserve:' + ' ' + kroner(budget['efter_reserve']))
        print('Største opkrævning:    ' + kroner(budget['stoerste_opkraevning']))
        print('Tilbage den måned uden opsparet reserve: ' + kroner(budget['efter_opkraevning']))
        if budget['andel_af_netto'] is not None:
            print(f"SU-reserve i % af netto: {budget['andel_af_netto']:.1f} %")
        else:
            print('Andel af netto kan ikke beregnes ved 0 kr. i indkomst.')
        if budget['efter_reserve'] < 0:
            print('Budgettet har underskud med de indtastede tal.')
        print('Medtag bolig, mad, transport, andre lån og øvrigt forbrug i udgifterne.')
        print('Reserven fordeler største opkrævning over betalingsintervallet; sidste betaling kan være mindre.')
        print('Beregningen tager kun højde for de udgifter, du har indtastet. Dette er ikke en ML-risikovurdering.')
    if args.betaling_csv:
        with args.betaling_csv.open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=['maaned', 'renter', 'betaling', 'gebyr', 'gaeld'], delimiter=';')
            writer.writeheader()
            for row in repayment['rows']:
                writer.writerow({key: str(value).replace('.', ',') for key, value in row.items()})
        print(f"Tilbagebetalingsoversigt gemt: {args.betaling_csv}")
    if args.start[:4] != "2026" or args.slut[:4] != "2026":
        print("Perioden rækker uden for 2026: 2026-loftet bruges som scenarie, ikke som sats for andre år.")
    print("Kilder og kontroltidspunkt findes i satser.json.")
    if args.csv:
        with args.csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter=";")
            writer.writeheader()
            for row in rows:
                writer.writerow({key: str(value).replace(".", ",") for key, value in row.items()})
        print(f"Månedsoversigt gemt: {args.csv}")


if __name__ == "__main__":
    main()

