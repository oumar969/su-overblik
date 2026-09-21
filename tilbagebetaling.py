"""Estimeret tilbagebetaling med fast scenarierente og månedlig bogføring."""
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from su_beregner import beloeb, maaned, SATSER, ORE


def dato(index):
    year, month = divmod(index, 12)
    return f'{year:04d}-{month + 1:02d}'


def loebetid(saldo):
    saldo = beloeb(saldo)
    return min(15, 7 + max(0, int(saldo // 20000) - 1))


def tilbagebetal(gaeld, studieslut, rente=None, interval=2):
    saldo = beloeb(gaeld)
    slut = maaned(studieslut)
    if interval not in (1, 2):
        raise ValueError('Betalingsinterval skal være 1 eller 2 måneder.')
    procent = beloeb(SATSER['tilbagebetaling']['rente_procent'] if rente is None else rente)
    if procent > 100:
        raise ValueError('Scenarierenten skal være mellem 0 og 100 procent.')
    rate = procent / 100 / 12
    first = (slut // 12 + 2) * 12
    rows = []
    fee = Decimal(SATSER['tilbagebetaling']['gebyr'])
    zero = Decimal('0.00')
    def row(index, interest, payment=zero, charge=zero):
        return dict(maaned=dato(index), renter=interest, betaling=payment, gebyr=charge, gaeld=saldo)
    for index in range(slut + 1, first):
        interest = (saldo * rate).quantize(ORE, rounding=ROUND_HALF_UP)
        saldo += interest
        rows.append(row(index, interest))
    opening = saldo
    years = loebetid(saldo)
    count = years * 12 // interval
    # Første betaling ved slutningen af januar, derefter hvert interval.
    discount = sum((1 + rate) ** -(1 + k * interval) for k in range(count))
    regular = max(Decimal('200'), (saldo / discount).quantize(ORE, rounding=ROUND_CEILING)) if saldo else zero
    for offset in range(years * 12):
        if not saldo:
            break
        interest = (saldo * rate).quantize(ORE, rounding=ROUND_HALF_UP)
        saldo += interest
        payment = charge = zero
        if offset % interval == 0:
            # Sidste termin udligner eventuelle øreafvigelser fra renteafrunding.
            payment = saldo if offset == (count - 1) * interval else min(regular, saldo)
            saldo -= payment
            charge = fee
        rows.append(row(first + offset, interest, payment, charge))
    payments = [r for r in rows if r['betaling'] > 0]
    return dict(start=dato(first) if payments else None, slut=payments[-1]['maaned'] if payments else None,
                startgaeld=opening, aar=years, ydelse=regular, interval=interval,
                rente=procent, gebyr=fee, renter_ventetid=opening-beloeb(gaeld),
                renter=sum((r['renter'] for r in rows), zero),
                gebyrer=sum((r['gebyr'] for r in rows), zero),
                samlet_betaling=sum((r['betaling']+r['gebyr'] for r in rows), zero), rows=rows)
