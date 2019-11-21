from dataclasses import dataclass
from .symbol     import Symbol
from decimal     import Decimal
from enum        import Enum


class Side(Enum):
	BUY  = "buy"
	SELL = "sell"


@dataclass(frozen=True)
class Trade:
	__slots__ = ("symbol", "size", "side", "price")

	symbol: Symbol
	size  : Decimal
	side  : Side
	price : Decimal
