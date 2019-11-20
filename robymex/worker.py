from typing      import Dict, List, Awaitable, Optional, Tuple
from .helpers    import wait_first
from .primitives import Trade, Ticker, Candle, Symbol
from .connectors import WebsocketConnector
import logging
import asyncio
import aioredis


class Perfomance:

	@property
	def period(self)->int:
		return self.__period

	@property
	def logger(self)->logging.LoggerAdapter:
		return self.__logger

	def __init__(self, period:int=1)->None:
		self.__lock   = asyncio.Lock()
		self.__lock1  = asyncio.Lock()
		self.__lock2  = asyncio.Lock()
		self.__estop  = asyncio.Event()
		self.__period = period
		self.__metrics :Dict[str, List[asyncio.Lock, int]] = {}
		self.__logger = logging.LoggerAdapter(
			logger=logging.getLogger("module"),
			extra={
				"modulename": "perfomance"
			}
		)

	async def add(self, metric:str, inc:int=1)->int:
		async with self.__lock:
			m = self.__metrics.get(metric)
			if not m:
				m = self.__metrics[metric] = [ asyncio.Lock(), 0 ]
		async with m[0]:
			m[1] += inc
			return m[1]

	async def start(self)->None:
		self.logger.info("Start ...")
		self.__estop.clear()
		while not self.__estop.is_set():
			flag,_ = await wait_first([
				asyncio.sleep(self.period),
				self.__estop.wait()
			])
			if not flag: break
			metrics :List[Tuple[str,int]] = []
			async with self.__lock:
				for k, v in self.__metrics.items():
					async with v[0]:
						metrics.append((k, v[1]))
						v[1] = 0
			if metrics:
				txt = ", ".join([ f"{x[0]}: {x[1]:5}" for x in metrics])
				self.logger.debug(f"Metrics, {txt}")
		self.logger.info("Stopped")

	def stop(self)->None:
		self.__estop.set()


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
		return hasattr(self, "__redis")

	@property
	def logger(self)->logging.LoggerAdapter:
		return self.__logger

	def __init__(self,
		show_trades :bool=False,
		show_candles:bool=False,
		redis_uri   :Optional[str]=None,
		period      :int=5,
		perfomance  :Optional[int]=None
	)->None:
		self.__lock         = asyncio.Lock()
		self.__estop        = asyncio.Event()
		self.__tasks        :List[Awaitable] = []
		self.__connectors   :List[WebsocketConnector] = []
		self.__candles      :Dict[str,Candle] = {}
		self.__period       = period
		self.__show_trades  = show_trades
		self.__show_candles = show_candles
		self.__perfomance   = Perfomance(perfomance) if perfomance else None
		self.__logger  = logging.LoggerAdapter(
			logger=logging.getLogger("module"),
			extra={
				"modulename": "worker"
			}
		)

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
			# Сбор статистики
			if self.__perfomance:
				await self.__perfomance.add("trades")
			# Показываем сделку
			if self.show_trades: self.logger.info(f"Trade <{name}>: {trade}")
			# Отправляем в redis
#			channel = f"trade:{key}"
#			await redis.publish(channel, str(trade))


	async def __task_candle_receiver(self, name:str, queue:asyncio.Queue)->None:
		# Обрабатываем свечи
		while not self.__estop.is_set():
			# Ждем сделку
			flag,ticker = await wait_first([
				queue.get(),
				self.__estop.wait()
			])
			if not flag: break
			# Сбор статистики
			if self.__perfomance: await self.__perfomance.add("candles")
			# Журнал
			if self.show_candles: self.logger.info(f"Candle <{name}>: {ticker}")



	async def start(self)->None:
		# Сбрасываем флаг остановки
		self.__estop.clear()
		# Запускаем сбор статистики
		if self.__perfomance: self.__tasks.append(
			asyncio.create_task(self.__perfomance.start())
		)
		# Ждем сигнала остановки
		await self.__estop.wait()
		# Останавливаем сбор статистики
		if self.__perfomance: self.__perfomance.stop()
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
		qtrade  :asyncio.Queue = asyncio.Queue()
		qcandle :asyncio.Queue = asyncio.Queue()
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
