from typing       import List, Dict, Set, Awaitable
from ..helpers    import wait_first
from ..primitives import Symbol
import websockets
import logging
import asyncio


CLOSE_TIMEOUT = 3


class WebsocketConnector:

	@property
	def uri(self)->str:
		return self._uri

	@property
	def name(self)->str:
		return self.__name

	@property
	def logger(self)->logging.LoggerAdapter:
		return self.__logger

	@property
	def symbols(self)->Dict[str,Symbol]:
		return self.__symbols

	@property
	def trades(self)->Set[str]:
		return self.__trades


	def __init__(self,
		uri:str,
		name:str,
		reconnect_timeout:int=5
	)->None:
		self._uri     = uri
		self.__symbols:Dict[str,Symbol] = {}
		self.__trades :Set[str] = set()
		self.__name   = name
		self.__estop  :asyncio.Event = asyncio.Event()
		self.__qsend  :asyncio.Queue = asyncio.Queue()
		self.__reconnect_timeout = reconnect_timeout
		self.__logger = logging.LoggerAdapter(
			logger=logging.getLogger("module"),
			extra={
				"modulename": name
			}
		)


	async def on_connect(self)->None:
		pass


	async def on_recv(self, msg:bytes, queue:asyncio.Queue)->None:
		pass


	async def __task_reader(self, ws:websockets.WebSocketClientProtocol, queue:asyncio.Queue)->None:
		self.logger.debug("[reader] Started")
		while not ws.closed:
			# Ждем сообщение
			flag,args = await wait_first([
				ws.recv(),
				ws.wait_closed(),
				self.__estop.wait()
			])
			if not flag: break
			# Обрабатываем сообщение
			try:
				await self.on_recv(args, queue)
			except Exception as e:
				self.logger.warn(f"[reader] on_recv() failed: <{type(e).__name__}> {e}, flag: {flag}, args: {args}")
		# Закрываем подключение
		if not ws.closed:
			self.logger.info("[reader] Close connection")
			await ws.close()
		# Журнал
		self.logger.debug("[reader] Stopped")


	async def __task_writer(self, ws:websockets.WebSocketClientProtocol)->None:
		self.logger.debug("[writer] Started")
		while not ws.closed:
			# Ждем сообщение
			flag,msg = await wait_first([
				self.__qsend.get(),
				ws.wait_closed(),
				self.__estop.wait()
			])
			if not flag: break
			# Передаем сообщение
			await ws.send(msg)
		self.logger.debug("[writer] Stopped")


	async def start(self, queue:asyncio.Queue)->None:
		# Журнал
		self.logger.info("Started")
		# Сбрасываем флаг остановки
		self.__estop.clear()
		# Пока не включен флаг остановки
		while not self.__estop.is_set():
			tasks :List[Awaitable] = []
			try:
				# Подключаемся к websocket
				async with websockets.connect(self.uri, close_timeout=CLOSE_TIMEOUT) as ws:
					# Журнал
					self.logger.info("Connection opened")
					# Запускаем задачи
					tasks = [
						asyncio.create_task(self.__task_reader(ws, queue)),
						asyncio.create_task(self.__task_writer(ws))
					]
					# Действия после подключения
					await self.on_connect()
					# Ждем закрытия подключения
					await ws.wait_closed()
			# Нестандартное завершения подключения
			except websockets.ConnectionClosedError as e:
				self.logger.error("Connection lost, trying reconnect ...")
				await asyncio.sleep(self.__reconnect_timeout)
			# Прочие ошибки
			except Exception as e:
				self.logger.error(f"<{type(e).__name__}> {e}")
				break
			# Ждем завершения задач
			finally:
				# Закрываем подключение
				if len(tasks)>0:
					await asyncio.gather(*tasks)
		# Журнал
		self.logger.info("Stopped")


	def stop(self)->None:
		self.__estop.set()
		self.logger.info("Stop ...")


	async def send(self, msg:str)->None:
		await self.__qsend.put(msg)


	async def _load_symbols(self)->List[Symbol]:
		pass


	async def _subscribe(self, trades:List[str])->None:
		pass


	async def _unsubscribe(self, trades:List[str])->None:
		pass


	async def load_symbols(self):
		self.logger.info("Loading symbols ...")
		symbols = await self._load_symbols()
		self.__symbols = { x.name.upper():x for x in symbols }
		self.logger.info(f"{len(symbols)} symbols loaded")


	async def subscribe(self, trades:List[str])->None:
		symbols = [ x for x in trades if x not in self.trades ]
		if len(symbols)>0:
			self.logger.info(f"Subscribe to trades: {', '.join(symbols)} ...")
			await self._subscribe(symbols)
			self.trades.update(symbols)


	async def unsubscribe(self, trades:List[str])->None:
		if len(trades)>0:
			self.logger.info(f"Unsubscribe from trades: {', '.join(trades)} ...")
			await self._unsubscribe(trades)
