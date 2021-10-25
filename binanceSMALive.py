import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from config import *

client = Client(API_KEY,API_SECRET)

symbol = input('Type Coin to Watch: ')

twm = ThreadedWebsocketManager(API_KEY, API_SECRET)
# start is required to initialise its internal loop
twm.start()

#initialize a reference dataframe
prices = pd.DataFrame(columns=[symbol])
#prices.set_index('Time', inplace=True)

#response = pd.DataFrame([0],columns=[f'symbol'])
def handle_socket_message(message):
    global prices
    prices = pd.DataFrame([{'Time':\
                            dt.datetime.fromtimestamp(int(f'{message["E"]}')/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),\
                            f'{symbol}':float(f"{message['k']['c']}")}])
    prices.index = prices['Time']
    del prices['Time']
    chartboard()

prices = prices.append(prices)
klines = client.get_historical_klines(symbol,\
                                      Client.KLINE_INTERVAL_1MINUTE,\
                                          "7 days ago UTC")
close = [float(i[4]) for i in klines]
timestamp = [int(i[0]) for i in klines]
#timestamp = [i.strftime('%Y-%m-%d %H:%M:%S.%f') for i in data.index.to_list()]

for i in range(len(timestamp)):
    timestamp[i] = dt.datetime.fromtimestamp(timestamp[i]/1000).strftime('%Y-%m-%d %H:%M:%S.%f')

#bot = pd.DataFrame(data.to_list(),columns=[symbol],index=timestamp)
bot = pd.DataFrame(close,columns=[symbol],index=timestamp)

def chartboard():
    global bot
    bot = bot.append(prices)
    bot['SMA'] = bot[symbol].rolling(round(len(bot)*0.1), min_periods=0).mean()
    bot['signal'] = 0.0
    bot['signal'] = np.where(bot[symbol] > bot['SMA'], 1.0, 0.0)  # use a conditional
    bot['positions'] = bot['signal'].diff()
    return bot, print(bot.tail(1))


twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

# plot
#fig = plt.figure(figsize=(30,15))
#ax1 = fig.add_subplot(111)
#bot[[symbol,'SMA']].plot(ax=ax1, lw=4.)
#ax1.set_title(f'{symbol} Bot', fontsize=50, fontweight='bold')
#ax1.grid(True,color='k',linestyle='-.',linewidth=2)
#ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
#plt.xticks(size=20)
#plt.yticks(size=20)import time
