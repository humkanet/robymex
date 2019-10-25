from typing       import List
from .websocket   import WebsocketConnector
from .http        import HttpConnector
from ..primitives import Symbol, Trade, Side
from decimal      import Decimal
import aiohttp
import websockets
import asyncio
import zlib


try:
	import ujson as json
except ModuleNotFoundError:
	import json


HTTP_ENDPOINT = "https://www.okex.com"
WS_ENDPOINT   = "wss://real.okex.com:8443/ws/v3"
HEADERS       = {
	"content-type": "application/json"
}


class OkexConnector(WebsocketConnector, HttpConnector):

	def __init__(self):
		# Наследование
		WebsocketConnector.__init__(self, uri=WS_ENDPOINT, name="okex")
		HttpConnector.__init__(self, headers=HEADERS)


	async def on_recv(self, msg:str, queue:asyncio.Queue)->None:
		# Распаковываем сообщение
		data = zlib.decompress(msg, -zlib.MAX_WBITS)
		args = json.loads(data)
		# Обрабатываем сделку
		if args.get("table")=="spot/trade":
			# Обрабатываем строки таблицы
			for row in args["data"]:
				# Проверяем символ
				symbol = self.symbols.get(row["instrument_id"])
				if not symbol: continue
				# buy/sell
				if   row["side"]=="buy" : side=Side.BUY
				elif row["side"]=="sell": side=Side.SELL
				else: continue
				# Возвращаем сделку
				await queue.put(
					Trade(symbol=symbol, size=Decimal(row["size"]), side=side, price=symbol.quantize(row["price"]))
				)


	async def _subscribe(self, trades:List[str])->None:
		msg = json.dumps({
			"op"  : "subscribe",
			"args": [ f"spot/trade:{x}" for x in trades ]
		})
		await self.send(msg)


	async def on_connect(self)->None:
		# Подписываемся на сделки по всем инструментам
		await self.subscribe(self.symbols.keys())


	async def start(self, queue:asyncio.Queue)->None:
		# Загружаем список инструментов
		await self.load_symbols()
		# Наследование
		await super().start(queue)



	async def _load_symbols(self)->List[Symbol]:
		symbols :List[Symbol] = []
		async with self._http.get(f"{HTTP_ENDPOINT}/api/spot/v3/instruments") as r:
			data = await r.json(loads=json.loads)
		return [ Symbol(name=s["instrument_id"], step=s["tick_size"]) for s in data ]
