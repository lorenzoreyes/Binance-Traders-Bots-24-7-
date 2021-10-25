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
    bot['EMA_5'] = bot[f'{symbol}'].ewm(span=round(len(bot)*0.05),adjust=False).mean()
    bot['EMA_20'] = bot[f'{symbol}'].ewm(span=round(len(bot)*0.2),adjust=False).mean()
    bot['MACD'] = bot.EMA_5 - bot.EMA_20
    bot['Reference'] = bot.MACD.ewm(span=round(len(bot)*0.1),adjust=False).mean()
    bot['Signal'] = np.where(bot.MACD > bot.Reference, 1.0, 0.0)
    bot['positions'] = bot.Signal.diff()    
    return bot, print(bot.tail(1))


twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

Buy, Sell = [], []

for i in range(2,len(bot)):
    if bot.MACD.iloc[i] > bot.Signal.iloc[i] and bot.MACD.iloc[i-1] < bot.Signal.iloc[i-1]:
        Buy.append(i+2) # as we started from i = 2, we add 2 now to adjust data point
    elif bot.MACD.iloc[i] < bot.Signal.iloc[i] and bot.MACD.iloc[i-1] > bot.Signal.iloc[i-1]:
        Sell.append(i+2)

fig = plt.figure(figsize=(20,8))
ax1 = fig.add_subplot(111)
plt.scatter(bot.iloc[Buy].index, bot.iloc[Buy][f'{symbol}'], marker="^", color="green", lw=7.)
plt.scatter(bot.iloc[Sell].index, bot.iloc[Sell][f'{symbol}'], marker="v", color="red", lw=7.)
bot[f'{symbol}'].plot(ax=ax1,color="k", lw=2.)
ax1.set_title(f'{symbol} & MACD', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=20)
plt.yticks(size=20)
plt.show()

fig = plt.figure(figsize=(15,10))
ax1 = fig.add_subplot(111)
bot[[symbol,'EMA_5','EMA_20']].plot(ax=ax1, lw=4.)

ax1.set_title(f'{symbol} MACD', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=20)
plt.yticks(size=20)