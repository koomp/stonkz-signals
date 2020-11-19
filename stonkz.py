import threading
import numpy as np
import yfinance.multi as yf
import pandas as pd
from datetime import date
import json
import logging
import ichimoku

signals = {}
lock = threading.Lock()
log = logging.getLogger()
log_handler = logging.FileHandler('./log_{}'.format(date.today()))
# formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# log_handler.formatter(formatter)
log.addHandler(log_handler)

class StockProcess (threading.Thread):
    def __init__(self, threadId, name, short_period=12, long_period=26, signal_period=9):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.name = name
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period
    
    def run(self):
        print ("Evaluating {}".format(self.name))
        try:
            close_price = self.get_close_price()

            # evaluate MACD
            _, _, difference = macd_signal_line(close_price)
            # generate signal
            signal = macd_signal(difference[-1], difference[-2])
            if (signal):
                print("Macd {}".format(self.name))
                lock.acquire()
                signals[self.name] = ["MACD"]
                lock.release()
            # ichimoku
            if (ichimoku.buy_signal(self.data['High'].to_numpy(), self.data['Low'].to_numpy(), self.data['Close'].to_numpy())):
                print("Ichimoku buy {}".format(self.name))
                lock.acquire()
                if self.name not in signals:
                    signals[self.name] = []
                signals[self.name].append('Ichimoku buy')
                lock.release()
        except Exception as e:
            lock.release()
            log.error("Error in thread {} {}".format(self.name, e))

    def get_close_price(self):
        # TODO specify range
        self.data = yf._download_one(self.name, interval='1d', period="78d")
        return self.data['Close']

def ema(data, period, smoothing=2):
    multiplier = smoothing / (period + 1)
    # for time period take closing price
    _ema = [data[0]]
    for i in range(1, len(data)):
        # ema_today = (price today * multiplier) + (ema_yesterday * (1 - multiplier))
        ema_today = (data[i] * multiplier) + (_ema[i-1] * (1 - multiplier))
        _ema.append(ema_today)
    return np.array(_ema)

def macd(data,short_period=12, long_period=26):
    return ema(data,short_period) - ema(data,long_period)

# signal if today macd is positive and previous macd is negative
def macd_signal(actual, previous):
    return True if actual > 0 and previous < 0 else False

def macd_signal_line(data, signal_period=9):
    data = data.to_numpy()
    ema_line = macd(data)
    signal_line = ema(ema_line, 9)
    difference = ema_line - signal_line
    return ema_line, signal_line, difference

if __name__ == "__main__":
    with open('s&p500.json', 'r') as f:
        fjson = json.load(f)
        tickers = [ticker['Symbol'] for ticker in fjson]
    # tickers = ['IBM', 'MSFT']
    threads = []

    print(tickers)
    for tId, ticker in enumerate (tickers):
        thread = StockProcess(tId, ticker)
        thread.start()
        threads.append(thread)

    # Wait to process all stocks
    for t in threads:
        t.join()
    
    print("Evaluating finished, saving results")
    filename = 'report_{}.json'.format(date.today())
    with open(filename , 'w') as f:
        json.dump(signals, f)