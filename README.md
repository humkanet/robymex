# robymex
WebSocket connector for some crypto-exchanges

### Features
- Connector for Binance, Okex
- Build candles with specified period
- Log trades and candles

### Usage

```
% python -m robymex -h
usage: __main__.py [-h] -e EXCHANGE [EXCHANGE ...] [-t] [-c] [-p PERIOD]

Crypto-exchanges connector

optional arguments:
  -h, --help            show this help message and exit
  -e EXCHANGE [EXCHANGE ...], --exchange EXCHANGE [EXCHANGE ...]
                        Connec to specified exchange (binance, okex)
  -t, --show-trades     Show trades (default=False)
  -c, --show-candles    Show candles (default=False)
  -p PERIOD, --period PERIOD
                        Candle period in seconds (default=5)
```

Connect to Binance and dump trades/candles:
```
% python -m robymex -t -c -p 1 -e binance
[25.10.2019 11:17:04, worker, INFO] Run connector <binance> ...
[25.10.2019 11:17:04, binance, INFO] Loading symbols ...
[25.10.2019 11:17:07, binance, INFO] 570 symbols loaded
[25.10.2019 11:17:07, binance, INFO] Started
[25.10.2019 11:17:09, binance, INFO] Connection opened
[25.10.2019 11:17:09, binance, DEBUG] [reader] Started
[25.10.2019 11:17:09, binance, DEBUG] [writer] Started
[25.10.2019 11:17:09, worker, INFO] Trade <binance>: Trade<symbol=BTCUSDT, size=0.01340600, side=buy, price=7456.05>
[25.10.2019 11:17:09, worker, INFO] Trade <binance>: Trade<symbol=STXBTC, size=1579.00000000, side=sell, price=0.00003788>
[25.10.2019 11:17:09, worker, INFO] Trade <binance>: Trade<symbol=STXBTC, size=1094.00000000, side=sell, price=0.00003780>
[25.10.2019 11:17:09, worker, INFO] Trade <binance>: Trade<symbol=ZRXUSDT, size=47.27000000, side=buy, price=0.2926>
...
[25.10.2019 11:17:10, worker, INFO] Trade <binance>: Trade<symbol=TRXUSDT, size=420.00000000, side=sell, price=0.01528>
[25.10.2019 11:17:10, worker, INFO] Candle <binance>: Ticker<symbol=BTCUSDT, open=7456.01, close=7456.01, low=7456.01, high=7456.01, buy=0, sell=0>
[25.10.2019 11:17:10, worker, INFO] Trade <binance>: Trade<symbol=ETHUSDT, size=2.44041000, side=buy, price=162.16>
[25.10.2019 11:17:10, worker, INFO] Trade <binance>: Trade<symbol=ETHUSDT, size=12.05092000, side=buy, price=162.16>
[25.10.2019 11:17:10, worker, INFO] Candle <binance>: Ticker<symbol=STXBTC, open=0.00003780, close=0.00003780, low=0.00003780, high=0.00003780, buy=0, sell=0>
```
