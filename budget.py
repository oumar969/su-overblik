"""Budget baseret på brugerens egne forventninger under tilbagebetalingen."""
from decimal import Decimal
from su_beregner import beloeb


def beregn_budget(nettoloen, udgifter, betalingsplan):
    netto, udgifter = beloeb(nettoloen), beloeb(udgifter)
    payments = [r['betaling'] + r['gebyr'] for r in betalingsplan['rows'] if r['betaling'] > 0]
    # Brug faktisk største opkrævning, også ved en lille restgæld.
    payment = max(payments, default=Decimal('0'))
    monthly = payment / betalingsplan['interval']
    return {
        'netto': netto, 'udgifter': udgifter,
        'foer': netto - udgifter,
        'maanedlig_reserve': monthly,
        'efter_reserve': netto - udgifter - monthly,
        'stoerste_opkraevning': payment,
        'efter_opkraevning': netto - udgifter - payment,
        'andel_af_netto': monthly / netto * 100 if netto else None,
    }
