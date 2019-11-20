from dataclasses import dataclass, field
from typing      import Union
from decimal     import Decimal


@dataclass(frozen=True)
class Symbol:

	name: str
	step: Decimal


	def __post_init__(self):
		object.__setattr__(self, "step", Decimal(self.step))


	def quantize(self, value:Union[float,Decimal,str])->Decimal:
		return Decimal(value).quantize(self.step)


	def __str__(self)->str:
		return f"Symbol<name={self.name}, step={self.step}>"
