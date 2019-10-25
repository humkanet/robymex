from typing  import Union
from decimal import Decimal

class Symbol:

	@property
	def name(self)->str:
		return self.__name

	@property
	def step(self)->Decimal:
		return self.__step


	def __init__(self, name:str, step:Union[float,Decimal,str])->None:
		self.__name = name
		self.__step = Decimal(step)


	def quantize(self, value:Union[float,Decimal,str])->Decimal:
		return Decimal(value).quantize(self.step)


	def __str__(self)->str:
		return f"Symbol<name={self.name}, step={self.step}>"
