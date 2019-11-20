from dataclasses import dataclass
from .symbol     import Symbol
from decimal     import Decimal
from enum        import Enum


class Side(Enum):
	BUY  = "buy"
	SELL = "sell"


@dataclass(frozen=True)
class Trade:
	symbol: Symbol
	size  : Decimal
	side  : Side
	price : Decimal


	def __str__(self)->str:
		return f"Trade<symbol={self.symbol.name}, size={self.size}, side={self.side.value}, price={self.price}>"
