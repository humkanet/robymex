from typing  import Dict, Optional
from aiohttp import ClientSession, TCPConnector
import aiohttp


try:
	import ujson as json
except ModuleNotFoundError:
	import json



class HttpConnector:


	@property
	def _http(self)->ClientSession:
		return self.__session


	def __init__(self, headers:Optional[Dict[str,str]]=None)->None:
		self.__session = ClientSession(
			connector       = TCPConnector(),
			connector_owner = False,
			json_serialize  = json.dumps,
			headers         = headers
		)
