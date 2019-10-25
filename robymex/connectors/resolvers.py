from typing    import Optional, List, Dict, Any
import asyncio
import aiohttp
import socket
import string
import random

try:
	import ujson as json
except ModuleNotFoundError:
	import json


PADDING_LETTERS = string.ascii_letters+string.digits+string.punctuation
PADDING_MIN     = 5
PADDING_MAX     = 20


class GoogleDNSResolver(aiohttp.abc.AbstractResolver):

	async def resolve(self, host:str, port:0, family:int=socket.AF_INET)->List[Dict[str,Any]]:
		# family
		if family==socket.AF_UNSPEC: family = socket.AF_INET
		# dns.google
		if host=="dns.google":
			if family==socket.AF_INET: return [
				{"hostname": host, "host": "8.8.8.8", "port": port, "family": family,
					"flags": socket.AI_NUMERICHOST, "proto": socket.IPPROTO_IP},
				{"hostname": host, "host": "8.8.4.4", "port": port, "family": family,
					"flags": socket.AI_NUMERICHOST, "proto": socket.IPPROTO_IP}
			]
			elif family==socket.AF_INET6: return [
				{"hostname": host, "host": "2001:4860:4860::8888", "port": port, "family": family,
					"flags": socket.AI_NUMERICHOST, "proto": socket.IPPROTO_IP},
				{"hostname": host, "host": "2001:4860:4860::8844", "port": port, "family": family,
					"flags": socket.AI_NUMERICHOST, "proto": socket.IPPROTO_IP}
			]
		# Хост не найден
		return list()

	async def close(self)->None:
		""" Do nothing """



class GoogleDOHResolver(aiohttp.abc.AbstractResolver):

	def __init__(self)->None:
		self.__connector = aiohttp.TCPConnector(
			resolver      = GoogleDNSResolver(),
			use_dns_cache = True, # Use DNS cache
			ttl_dns_cache = None  # never expired
		)
		self.__session = aiohttp.ClientSession(
			connector       = self.__connector,
			connector_owner = False,
			json_serialize  = json.dumps,
		)

	async def resolve(self, host:str, port:0, family:int=socket.AF_INET)->List[Dict[str,Any]]:
		# inet4/inet6
		if family in {socket.AF_INET, socket.AF_UNSPEC}: qtype = 1
		elif family==socket.AF_INET6: qtype = 28
		else: return list()
		# Cлучайные данные
		padding = random.choices(
			PADDING_LETTERS,
			k=random.randint(PADDING_MIN, PADDING_MAX)
		)
		# Отправляем запрос
		params = {
			"name": host,
			"type": qtype,
			"random_padding": "".join(padding)
		}
		async with self.__session.get(
			"https://dns.google/resolve",
			params = params
		) as r:
			answer = await r.json(loads=json.loads, content_type=None)
		# Формируем список хостов
		if answer["Status"]==0:
			# Присоединяем данные к ответу
			return [ {
				"hostname": host,
				"host"    : x["data"],
				"port"    : port,
				"family"  : family,
				"flags"   : socket.AI_NUMERICHOST,
				"proto"   : socket.IPPROTO_IP
			} for x in answer["Answer"] if x["type"]==qtype ]
		return list()

	async def close(self)->None:
		if not self.__connector.closed:
			await self.__connector.close()
		if not self.__session.closed:
			await self.__session.close()
