from typing    import Optional
from .ticker   import Ticker
from .symbol   import Symbol
from ..helpers import wait_first
from .trade    import Trade, Side
from decimal   import Decimal
import asyncio


class Candle:

	@property
	def symbol(self)->Symbol:
		return self.__symbol

	@property
	def period(self)->int:
		return self.__period


	def __init__(self, symbol:Symbol, period:int)->None:
		self.__lock   = asyncio.Lock()
		self.__estop  = asyncio.Event()
		self.__symbol = symbol
		self.__open   : Optional[Decimal] = None
		self.__close  : Optional[Decimal] = None
		self.__high   : Optional[Decimal] = None
		self.__low    : Optional[Decimal] = None
		self.__buy    : Decimal = Decimal(0)
		self.__sell   : Decimal = Decimal(0)
		self.__period = period


	async def update(self, trade:Trade)->None:
		# Сажаем блокировку и обрабатываем данные
		async with self.__lock:
			if self.__open is None:
				self.__open  = trade.price
				self.__close = trade.price
				self.__low   = trade.price
				self.__high  = trade.price
				self.__buy   = Decimal(0)
				self.__sell  = Decimal(0)
			else:
				# Обрабатываем цену
				self.__close = trade.price
				if   trade.price>self.__high: self.__high = trade.price # type: ignore
				elif trade.price<self.__low : self.__low  = trade.price # type: ignore
				# Обрабатываем объем
				if   trade.side==Side.BUY : self.__buy  += trade.size
				elif trade.side==Side.SELL: self.__sell += trade.size


	async def start(self, queue:asyncio.Queue)->None:
		self.__estop.clear()
		while not self.__estop.is_set():
			# Обнуляем параметры
			async with self.__lock:
				self.__open = None
			# Ждем указанные период
			flag,_ = await wait_first([
				asyncio.sleep(self.__period),
				self.__estop.wait()
			])
			if not flag: break
			# Возвращаем свечу
			async with self.__lock:
				# Нет данных, пропускаем
				if not self.__open: continue
				# Формируем и возвращаем свечу
				await queue.put(Ticker(
					symbol = self.symbol,
					open   = self.__open,
					close  = self.__close,
					high   = self.__high,
					low    = self.__low,
					buy    = self.__buy,
					sell   = self.__sell
				))


	def stop(self)->None:
		self.__estop.set()


	def __str__(self)->str:
		return f"Candle<symbol={self.symbol.name}, period={self.period}>"
