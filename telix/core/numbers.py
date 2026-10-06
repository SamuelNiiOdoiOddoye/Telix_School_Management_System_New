"""Tolerant numeric conversion for values read from storage."""

from decimal import Decimal, InvalidOperation


ZERO_AMOUNT = Decimal("0.00")


def parse_amount(value: object) -> Decimal | None:
    """Return a finite, cent-quantized Decimal, or None for an unreadable value."""
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return amount if amount.is_finite() else None


def as_amount(value: object) -> Decimal:
    """Convert stored money values to Decimal; unreadable values count as zero."""
    amount = parse_amount(value or 0)
    return amount if amount is not None else ZERO_AMOUNT
