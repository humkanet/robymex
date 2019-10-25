from .websocket   import WebsocketConnector
from .http        import HttpConnector
from ..primitives import Symbol, Trade, Side
from decimal      import Decimal
from typing       import List
import asyncio
import aiohttp
import websockets

try:
	import ujson as json
except ModuleNotFoundError:
	import json


HTTP_ENDPOINT = "https://api.binance.com/api/v3"
WS_ENDPOINT  = "wss://stream.binance.com:9443"


class BinanceConnector(WebsocketConnector, HttpConnector):

	def __init__(self):
		# Наследование
		WebsocketConnector.__init__(self, uri=WS_ENDPOINT, name="binance")
		HttpConnector.__init__(self)


	async def on_recv(self, msg:str, queue:asyncio.Queue)->None:
		# Разбираем сообщение
		args = json.loads(msg)
		# Обрабатываем сделку (trade)
		s = args.get("stream")
		if s:
			s = s.split("@trade")[0].upper()
			symbol = self.symbols.get(s)
			if symbol:
				data  = args["data"]
				side  = Side.SELL if data["m"] else Side.BUY
				await queue.put(
					Trade(symbol=symbol, size=Decimal(data["q"]), side=side, price=symbol.quantize(data["p"]))
				)


	async def start(self, queue:asyncio.Queue)->None:
		# Загружаем список инструментов
		await self.load_symbols()
		# Формируем адрес подключения
		streams = "/".join([ f"{x.name.lower()}@trade" for x in self.symbols.values()])
		self._uri = f"{self._uri}/stream?streams={streams}"
		# Наследование
		await super().start(queue)


	async def _load_symbols(self)->List[Symbol]:
		symbols :List[Symbol] = []
		async with self._http.get(f"{HTTP_ENDPOINT}/exchangeInfo") as r:
			data = await r.json(loads=json.loads)
			for s in data["symbols"]:
				# Отсекаем ненужные инструменты
				if s.get("status")!="TRADING": continue
				# Определяем шаг цены
				step = None
				for f in s["filters"]:
					if f["filterType"]=="PRICE_FILTER":
						step = f["tickSize"]
						if "." in step: step = step.rstrip("0")
						break
				else: continue
				# Запоминаем инструмент
				symbols.append(
					Symbol(name=s["symbol"], step=Decimal(step))
				)
		return symbols
