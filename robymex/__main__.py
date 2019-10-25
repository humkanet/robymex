from .worker     import Worker
from .connectors import BinanceConnector, OkexConnector
import asyncio
import signal
import logging.config
import aioredis
import argparse


LOGGING = {
	"version" : 1,

	"formatters": {
		"console": {
			"format" : "[{asctime}, {module-name}, {levelname}] {message}",
			"datefmt": "%d.%m.%Y %H:%M:%S",
			"style"  : "{"
		}
	},

	"handlers": {
		"console": {
			"class"    : "logging.StreamHandler",
			"stream"   : "ext://sys.stdout",
			"formatter": "console"
		},
	},

	"loggers": {
		"module": {
			"level"    : "DEBUG",
			"handlers" : ["console"]
		},
	}
}


async def main():
	# Параметры
	parser = argparse.ArgumentParser(description="Crypto-exchanges connector")
	parser.add_argument(
		"-e", "--exchange", type=str, nargs="+", required=True,
		help="Connec to specified exchange (binance, okex)"
	)
	parser.add_argument(
		"-t", "--show-trades", action="store_true", default=False,
		help="Show trades (default=%(default)s)"
	)
	parser.add_argument(
		"-c", "--show-candles", action="store_true", default=False,
		help="Show candles (default=%(default)s)"
	)
	parser.add_argument(
		"-p", "--period", type=int, default=5,
		help="Candle period in seconds (default=%(default)s)"
	)
	args = parser.parse_args()
	# Настриваем журнал
	logging.config.dictConfig(LOGGING)
	# Обработка сделок/свечей
	worker = Worker(
		show_trades  = args.show_trades,
		show_candles = args.show_candles,
		period       = args.period
	)
	# Перехиватываем SIGINT/SIGTERM для остановки коннекторов
	loop  = asyncio.get_running_loop()
	def stop():
		# Убираем обработку сигналов
		for sig in [ signal.SIGINT, signal.SIGTERM ]:
			loop.remove_signal_handler(sig)
		# Останавливаем коннекторы
		worker.stop()
	for sig in [ signal.SIGINT, signal.SIGTERM ]:
		loop.add_signal_handler(sig, stop)
	# Запускаем коннекторы
	redis = await aioredis.create_redis_pool(
		"/www/robymex.com/var/redis.socket"
	)
	tasks = [
		worker.start()
	]
	# Подключаемся к биржам
	for x in args.exchange:
		if   x=="binance": tasks.append(worker.run(BinanceConnector()))
		elif x=="okex"   : tasks.append(worker.run(OkexConnector()))
	await asyncio.gather(*tasks)


if __name__=="__main__":
	asyncio.run(main())
