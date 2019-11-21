from dataclasses import dataclass
from typing      import Union
from decimal     import Decimal


@dataclass(frozen=True)
class Symbol:
	__slots__ = ("name", "step")

	name: str
	step: Decimal


	def __post_init__(self):
		object.__setattr__(self, "step", Decimal(self.step))


	def quantize(self, value:Union[float,Decimal,str])->Decimal:
		return Decimal(value).quantize(self.step)
