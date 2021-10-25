import pandas as pd
import numpy as np
import yfinance as yahoo
import datetime as dt
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.family'] = 'serif'
plt.style.use('fivethirtyeight')


# Quick screener of crypto performance

spectre = ['AAVE-USD', 'ADA-USD', 'BNB-USD', 'BTC-USD', 'BAT-USD', 'DOGE-USD',
           'EGLD-USD', 'ETC-USD', 'ETH-USD', 'HBAR-USD', 'IOST-USD', 
           'LINK-USD', 'LTC-USD', 'MATIC-USD', 'OMG-USD', 'SOL1-USD']
         

data = yahoo.download(spectre,period="60d",interval="2m")["Adj Close"].fillna(method="ffill")

df = pd.DataFrame(data.tail(1).T.values,columns=['Last'],index=data.columns)

df['SMA_5%'] = data.rolling(int(len(data)*0.05),min_periods=1).mean().tail(1).T
data.rolling(int(len(data)*0.05),min_periods=1).mean().tail(1).T
pct = data.pct_change().fillna(value=0.0)
gains = pct[pct>=0].fillna(value=0.0)
loss = -pct[pct<0].fillna(value=0.0)

gains = gains.rolling(int(len(gains)*0.05),min_periods=1).mean()
loss = loss.rolling(int(len(gains)*0.05),min_periods=1).mean()

rs = gains / loss
rs = rs.replace([np.inf, -np.inf], np.nan)
rs.dropna(inplace=True)
rsi = 100 - (100 / (1 + rs))

df['RSI'] = rsi.tail(1).T
df['Action'] = np.where(df.Last > df['SMA_5%'],'Buy','Sell')
df['Difference%'] = (df['Last'] - df['SMA_5%']) / df['Last']

dt = data.copy()
columnas = []
for i in range(len(dt.columns)):
    columnas.append(str(round(dt.iloc[:,i].pct_change().sum(),2)) + '% ' + str(dt.columns[i]))

dt.columns = columnas
dt.reindex(sorted(dt.columns,reverse=True), axis=1)
dt = dt.reindex(sorted(dt.columns,reverse=True), axis=1)

fig = plt.figure(figsize=(30,15))
ax1 = fig.add_subplot(111)
dt.pct_change().cumsum().plot(ax=ax1, lw=2)
ax1.set_title('Binance TOP30', fontsize=50, fontweight='bold')
ax1.grid(True,color='k',linestyle='-.',linewidth=2)
ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize=30)
plt.xticks(size=40)
plt.yticks(size=40)
plt.savefig('binance.png',bbox_inches='tight')