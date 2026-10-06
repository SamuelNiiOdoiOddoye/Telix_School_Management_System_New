"""Display formatting."""

from decimal import Decimal
from typing import SupportsFloat


def format_currency(value: Decimal | SupportsFloat) -> str:
    amount = value if isinstance(value, Decimal) else Decimal(str(value))
    return f"GHS {amount:,.2f}"
