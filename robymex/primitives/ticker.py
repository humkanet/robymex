from decimal  import Decimal
from .symbol  import Symbol

try:
	import ujson
except ModuleNotFoundError:
	import json


class Ticker:

	@property
	def symbol(self)->Symbol:
		return self.__symbol

	@property
	def open(self)->Decimal:
		return self.__open

	@property
	def close(self)->Decimal:
		return self.__close

	@property
	def high(self)->Decimal:
		return self.__high

	@property
	def low(self)->Decimal:
		return self.__low

	@property
	def buy(self)->Decimal:
		return self.__buy

	@property
	def sell(self)->Decimal:
		return self.__sell


	def __init__(self,
		symbol: Symbol,
		open  : Decimal,
		close : Decimal,
		high  : Decimal,
		low   : Decimal,
		buy   : Decimal,
		sell  : Decimal
	)->None:
		self.__symbol = symbol
		self.__open   = symbol.quantize(open)
		self.__close  = symbol.quantize(close)
		self.__high   = symbol.quantize(high)
		self.__low    = symbol.quantize(low)
		self.__buy    = buy
		self.__sell   = sell


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
