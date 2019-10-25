from typing     import Dict, Optional
from aiohttp    import ClientSession, TCPConnector
from .resolvers import GoogleDOHResolver
import aiohttp


try:
	import ujson as json
except ModuleNotFoundError:
	import json # type: ignore


class HttpConnector:

	@property
	def _http(self)->ClientSession:
		return self.__session

	def __init__(self, headers:Optional[Dict[str,str]]=None)->None:
		self.__connector = TCPConnector(
			resolver = GoogleDOHResolver(),
			use_dns_cache = True, # Use DNS cache
			ttl_dns_cache = 60*60 # for 1 hour
		)
		self.__session = ClientSession(
			connector       = self.__connector,
			connector_owner = False,
			json_serialize  = json.dumps,
			headers         = headers
		)
