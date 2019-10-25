from typing      import List, Awaitable, Optional
from .helpers    import wait_first
from .primitives import Trade, Ticker, Candle
from .connectors import WebsocketConnector
import logging
import asyncio
import aioredis


class Worker:

	@property
	def show_trades(self)->bool:
		return self.__show_trades

	@property
	def show_candles(self)->bool:
		return self.__show_candles

	@property
	def period(self)->int:
		return self.__period

	@property
	def redis(self)->bool:
		return self.__redis is not None

	@property
	def logger(self)->logging.Logger:
		return self.__logger

	def __init__(self,
		show_trades :bool=False,
		show_candles:bool=False,
		redis_uri   :Optional[str]=None,
		period      :int=5
	)->None:
		self.__lock         = asyncio.Lock()
		self.__estop        = asyncio.Event()
		self.__tasks        :List[Awaitable] = []
		self.__connectors   :List[WebsocketConnector] = []
		self.__candles      = {}
		self.__period       = period
		self.__show_trades  = show_trades
		self.__show_candles = show_candles
		self.__logger  = logging.LoggerAdapter(
			logger=logging.getLogger("module"),
			extra={
				"module-name": f"worker"
			}
		)
		self.__lock_candles = asyncio.Lock()


	async def __task_trade_receiver(self,
		name   :str,
		qtrade :asyncio.Queue,
		qcandle:asyncio.Queue
	)->None:
		# Обрабатываем сделки
		while not self.__estop.is_set():
			# Ждем сделку
			flag,trade = await wait_first([
				qtrade.get(),
				self.__estop.wait()
			])
			if not flag: break
			# Обновляем свечу
			key = f"{name}:{trade.symbol.name}"
			async with self.__lock:
				candle = self.__candles.get(key)
				if not candle:
					candle = self.__candles[key] = Candle(trade.symbol, self.period)
					self.__tasks.append(
						asyncio.create_task(candle.start(qcandle))
					)
			await candle.update(trade)
			# Показываем сделку
			if self.show_trades: self.logger.info(f"Trade <{name}>: {trade}")
			# Отправляем в redis
#			channel = f"trade:{key}"
#			await redis.publish(channel, str(trade))


	async def __task_candle_receiver(self, name:str, queue:str)->None:
		# Обрабатываем свечи
		while not self.__estop.is_set():
			# Ждем сделку
			flag,ticker = await wait_first([
				queue.get(),
				self.__estop.wait()
			])
			if not flag: break
			# Журнал
			if self.show_candles: self.logger.info(f"Candle <{name}>: {ticker}")



	async def start(self)->None:
		# Сбрасываем флаг остановки
		self.__estop.clear()
		# Ждем сигнала остановки
		await self.__estop.wait()
		# Останавливаем коннекторы
		for connector in self.__connectors:
			connector.stop()
		# Останавливаем свечи
		for candle in self.__candles.values(): candle.stop()
		# Ждем завершения задач
		for task in self.__tasks: await task
		


	async def run(self, connector:WebsocketConnector)->None:
		# Журнал
		self.logger.info(f"Run connector <{connector.name}> ...")
		# Запускаем коннектор и обработку сделок
		qtrade  = asyncio.Queue()
		qcandle = asyncio.Queue()
		self.__tasks += [
			asyncio.create_task(connector.start(qtrade)),
			asyncio.create_task(self.__task_trade_receiver(connector.name, qtrade, qcandle)),
			asyncio.create_task(self.__task_candle_receiver(connector.name, qcandle))
		]
		# Сохраняем коннектор
		self.__connectors.append(connector)


	def stop(self)->None:
		# Включаем флаг остановки
		self.__estop.set()
