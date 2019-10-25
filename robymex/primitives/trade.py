from .symbol import Symbol
from decimal import Decimal
from enum    import Enum


class Side(Enum):
	BUY  = "buy"
	SELL = "sell"


class Trade:

	@property
	def symbol(self)->Symbol:
		return self.__symbol

	@property
	def size(self)->Decimal:
		return self.__size

	@property
	def side(self)->Side:
		return self.__side

	@property
	def price(self)->Decimal:
		return self.__price


	def __init__(self, symbol:Symbol, size:Decimal, side:Side, price:Decimal)->None:
		self.__symbol = symbol
		self.__size   = size
		self.__price  = price
		self.__side   = side


	def __str__(self)->str:
		return f"Trade<symbol={self.symbol.name}, size={self.size}, side={self.side.value}, price={self.price}>"
