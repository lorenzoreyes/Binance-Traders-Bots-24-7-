import pandas as pd 
import numpy as np 
import yfinance as yahoo



def SimpleMovingAverage(bot,symbol,prices):
    """Simple Moving Average for num_days given"""
    bot = bot.append(prices)
    bot['SMA'] = bot[symbol].rolling(round(len(bot)*0.15), min_periods=0).mean()
    bot['signal'] = 0.0
    bot['signal'] = np.where(bot[symbol] > bot['SMA'], 1.0, 0.0)  # use a conditional
    bot['positions'] = bot['signal'].diff()
    print(bot.tail(1))
    
def Momentum(bot,symbol,prices):
    """Provide financial 'symbol' to look data 
       Choose number of days for the metric"""
    bot = bot.append(prices)
    bot['Momentum'] = bot[symbol] / bot[symbol].rolling(round(len(bot)*0.1),min_periods=1).mean()
    bot['signal'] = 0.0
    bot['signal'] = np.where(bot['Momentum'] < bot[f'{symbol}'], 1.0,0.0)
    bot['positions'] = bot['signal'].diff()
    print(bot.tail(1))
    
def BollingerBands(bot,symbol,prices):
    """Provide financial 'symbol' to look data 
       Choose number of days for the metric
       number of factors for stdev to apply"""
    stdev_factor = 2
    bot = bot.append(prices)
    bot['MiddleBand'] = bot[f'{symbol}'].rolling(round(len(bot)*0.1),min_periods=1).mean()
    bot['UpperBand'] = (bot['MiddleBand'] + int(stdev_factor) * bot[symbol].rolling(round(len(bot)*0.1),min_periods=1).std())
    bot['LowerBand'] = (bot['MiddleBand'] - int(stdev_factor) * bot[symbol].rolling(round(len(bot)*0.1),min_periods=1).std())
    print(bot.tail(1))
  
def StandardDeviation(bot,symbol,prices):
    """Provide financial 'symbol' to look data 
       Choose number of days for the metric"""
    bot = bot.append(prices)
    bot['StDev'] = bot[symbol].rolling(round(len(bot)*0.1),min_periods=1).std()
    print(bot.tail(1))
  
def AbsolutePriceOscillator(bot, symbol, prices):
   """Differences between short-term & long-term
      moving averages to current price,  
      Choose short & long period days"""
   bot = bot.append(prices)
   bot['shortAPO-5%'] = bot[symbol] - bot[symbol].rolling(round(len(bot)*0.05),min_periods=1).mean()
   bot['longAPO-25%'] = bot[symbol] - bot[symbol].rolling(round(len(bot)*0.3),min_periods=1).mean()
   print(bot.tail(1))
      
def RelativeStrenghtIndex(bot,symbol,prices):
   """RSI = 100 - (100 / (1 + RS))"""
   bot = bot.append(prices)
   bot['difference'] = bot[symbol].diff()
   bot['loss'] = bot.difference[bot.difference<=0]
   bot['gain'] = bot.difference[bot.difference>=0]
   bot = bot.fillna(0)
   average_gain = pd.Series(bot.gain.rolling(round(len(bot)*0.3),min_periods=1).mean())
   average_loss = pd.Series(bot.loss.rolling(round(len(bot)*0.3),min_periods=1).mean())
   rs = average_gain / -average_loss
   bot[f'{symbol} RSI'] = 100 - (100 /  (1 + rs))
   print(bot.tail(1))

def MovingAverageConvergenceDivergence(bot, symbol, prices):
   """Return one line oscillator,
      betweeen short & long averages,
      provide periods"""
   bot = bot.append(prices)
   bot[f'MACD {symbol}'] = bot[symbol].rolling(round(len(bot)*0.05),min_periods=1).mean() - bot[symbol].rolling(round(len(bot)*0.3),min_periods=1).mean()
   print(bot.tail(1))