import pandas as pd, numpy as np
from itertools import product
import yfinance as yahoo

def backtest(stock):
    data = yahoo.download(stock,period="1y",interval="60m")["Adj Close"].fillna(method="ffill")
    data = pd.DataFrame(data.values,columns=[stock],index=data.index)
    data['SMA-5%'] = data[stock].rolling(round(len(data)*0.05),min_periods=1).mean()
    data['Signal'] = np.where(data[stock] > data['SMA-5%'],1,0)
    data['Positions'] = data['Signal'].diff()
    # chequeo entradas y salidas
    ordenes = data[stock] * data['Positions']
    precio_entrada = ordenes[ordenes>=1.0]
    precio_salida = ordenes[ordenes<=-1.0] * -1.0
    if precio_salida.index[0] < precio_entrada.index[0]:
        precio_salida = precio_salida.drop(precio_salida.index[0])
    elif precio_entrada.index[-1] > precio_salida.index[-1]:
        precio_entrada = precio_entrada.drop(precio_entrada.index[-1]) 
    book = pd.DataFrame(precio_entrada, columns=['entrada'])
    book['salida'] = precio_salida.values 
    book['resultado'] = book['salida'] - book['entrada']
    return [data,book]

data = backtest(input('stock to backtest?\t'))[0]
stock = str(data.columns[0])
sma1 = range(1,2,1)# round(len(data)*0.05), 200)  
#sma1 = range(round(len(data)*0.05), round(len(data)*0.15),round(len(data)*0.01)) 
sma2 = range(round(len(data)*0.15), round(len(data)*0.5),round(len(data)*0.02)) 

results = pd.DataFrame()
for SMA1, SMA2 in product(sma1, sma2):  
    data = pd.DataFrame(data[stock])
    data.dropna(inplace=True)
    data['Returns'] = data[stock].pct_change().fillna(value=0) # np.log(data[stock] / data[stock].shift(1))
    data['SMA1'] = data[stock].rolling(SMA1,min_periods=1).mean()
    data['SMA2'] = data[stock].rolling(SMA2,min_periods=1).mean()
    data.dropna(inplace=True)
    data['Position'] = np.where(data['SMA1'] > data['SMA2'], 1, -1)
    data['Strategy'] = data['Position'].shift(1) * data['Returns']
    data.dropna(inplace=True)
    perf = np.exp(data[['Returns', 'Strategy']].sum())
    results = results.append(pd.DataFrame(
                {'SMA1': SMA1, 'SMA2': SMA2,
                 'MARKET': perf['Returns'],
                 'STRATEGY': perf['Strategy'],
                 'OUT': perf['Strategy'] - perf['Returns']},
                 index=[0]), ignore_index=True) 

print(results.sort_values('OUT', ascending=False).head(7))
