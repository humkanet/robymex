from dataclasses import dataclass
from decimal     import Decimal
from .symbol     import Symbol


try:
	import ujson
except ModuleNotFoundError:
	import json


@dataclass(frozen=True)
class Ticker:
	__slots__ = ("symbol", "open", "close", "high", "low", "buy", "sell")

	symbol: Symbol
	open  : Decimal
	close : Decimal
	high  : Decimal
	low   : Decimal
	buy   : Decimal
	sell  : Decimal


	def __post_init__(self)->None:
		for x in ("open", "close", "high", "low"):
			object.__setattr__(self, x, self.symbol.quantize(self.__getattribute__(x)))


	def dumps(self)->str:
		return json.dumps({
			"symbol": self.symbol.name,
			"open"  : self.open,
			"close" : self.close,
			"low"   : self.low,
			"high"  : self.high,
			"buy"   : self.buy,
			"sell"  : self.sell
		})


	def __str__(self)->str:
		return f"Ticker<symbol={self.symbol.name}, open={self.open}, close={self.close}, low={self.low}, high={self.high}, buy={self.buy}, sell={self.sell}>"
