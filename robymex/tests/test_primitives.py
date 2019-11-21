from robymex.primitives import Symbol, Trade, Ticker
from unittest           import TestCase
from decimal            import Decimal
import asyncio


class PrimitivesTestCase(TestCase):

	def setUp(self):
		self.loop   = asyncio.get_event_loop()
		self.symbol = Symbol(name="TEST", step="0.05")


	def test_symbol(self):
		items = (
			(0.123, Decimal("0.12")),
			(0.178, Decimal("0.18")),
			(-0.123, Decimal("-0.12")),
			(-0.178, Decimal("-0.18"))
		)
		for val, q in items:
			self.assertEqual(q, self.symbol.quantize(val))
