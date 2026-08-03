from decimal import ROUND_HALF_UP, Decimal


def round_money(value: float) -> float:
    """Round a dollar amount (or share quantity) to 2 decimal places using round-half-up - the
    convention retail brokerage/accounting systems use (e.g. 2.005 -> 2.01), unlike Python's
    built-in round() which defaults to banker's rounding (round-half-to-even: round(2.5) == 2).

    Converts through str first - Decimal(some_float) preserves that float's binary imprecision
    (e.g. Decimal(0.1) != Decimal('0.1')), so going through the float's string repr is what
    actually gets the intended decimal value before rounding it.
    """
    return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
