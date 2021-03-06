# -*- coding: utf-8 -*-
"""investcop-streamlit-original.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1teOk6A0XNe4nyYeJ4sbvx2IjXpOLC0G5

# InvestCop
## Main DataFrame to generate Analysis Data from Yahoo Finance
## Streamlit Edt
## Date: 04/11/21

## References
"""

import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import seaborn as sns
import numpy as np
import ta
from ta.volatility import BollingerBands
from ta.trend import MACD, SMAIndicator
from ta.momentum import RSIIndicator
import streamlit as st
import datetime

## Choose stock

types=['bdr','cambio','cripto','fii','index','bov','commodities','etf','futures']

#stock="USDBRL=X"    # ETH-USD BTTL3.SA USDBRL=X  ^N225
period='2y'

def insert(df, row):
    insert_loc = df.index.max()

    if pd.isna(insert_loc):
        df.loc[0] = row
    else:
        df.loc[insert_loc + 1] = row

## Side Menu Streamlit

##########
# sidebar #
###########
type = st.sidebar.selectbox('Select type', types)
file='./symbols/'+type+'.csv'
symbolslist=open(file,'r').readlines()
stocks=[symbol.strip('\n') for symbol in symbolslist]
stock=st.sidebar.selectbox('Select type', stocks)
today = datetime.date.today()
before = today - datetime.timedelta(days=700)
start_date = st.sidebar.date_input('Start date', before)
end_date = st.sidebar.date_input('End date', today)
if start_date < end_date:
    st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.sidebar.error('Error: End date must fall after start date.')

"""## InvestCop 
   ### Streamlit EDT """    
## Import data from Yahoo Finance
tickersymbol=stock
ticker=yf.Ticker(stock)

ydata = ticker.history(period=period)

ticker_info=ticker.info

#ticker_name=ticker_info['shortName']
tickername=ticker_info['shortName']

#ydata.head()

data=ydata[['Close']].copy()

## Data Quality check

#data.isna().sum()

#data.info()

#data.describe()

## Feature Engineering

#data.size

data['Delta']=data.Close/data.Close.shift(1) - 1

data['MA20']=SMAIndicator(data.Close,14).sma_indicator()

data['Boll+']=BollingerBands(data.Close).bollinger_hband()
data['Boll-']=BollingerBands(data.Close).bollinger_lband()

data['RFI20']=RSIIndicator(data.Close,14).rsi()
data['RFI100']=RSIIndicator(data.Close,100).rsi()

data.tail()

# Wave Analysis
rfi_start=data.query('RFI20 <30 and Delta <0').index
rfi_end=data.query('RFI20>70 and Delta >0').index
# another approach
data['daybefore']=data.RFI20.shift()
rfi_start=data.query('RFI20>=30 and daybefore<30').index
rfi_end=data.query('RFI20>=70 and daybefore<70').index
waves=[]




if len(rfi_start)==0 or len(rfi_end)==0:
    st.error('No RSI')
lastmin=rfi_start[0]
lastmax=rfi_end[rfi_end>lastmin][0]
rfi=data.RFI20
for min in rfi_start:
    if min < lastmax:
      if lastmin > min:
        lastmin=min
     # print('lastmin=',lastmin)
    else:
      #print('new-entry:wave=',lastmin,lastmax)
      waves.append((lastmin,lastmax))
      if len(rfi_end[rfi_end>min])>0:
        lastmax=rfi_end[rfi_end>min][0]
        lastmin=min
        #print('next max =',lastmax)
      else:
        break
waves=list(dict.fromkeys(waves))

#waves[0][0]
# True max and mins
#waves
truewaves=[]
i=0
for i in range(0,len(waves)):
  wave=waves[i]
  if i< len(waves)-1:
    next=waves[i+1][0]
  else:
    next=data.index[-1]
  dmin=data.loc[wave[0]:wave[1]].Close.argmin()
  min=data.loc[wave[0]:wave[1]].iloc[dmin].name

  dmax=data.loc[wave[1]:next].Close.argmax()
  max=data.loc[wave[1]:next].iloc[dmax].name
  truewaves.append((min,max))

# Generate Summary
summary=pd.DataFrame(columns=['Type', 'Symbol', 'Description','Close','LastWaveStart','LastwaveEnd','LastWavePeriod','LastWaveValueGain','CurrentWaveStart','CurrentPeriod',
                              'CurrentValueGain','TRelative','GainRelative','Congruence','P','DeltaN','YieldEst','GainPerDayCurrent','GainPerDayEstimated', 'Boll-2MA','MA2Boll+'])

if len(truewaves)<1:
    st.error('No Waves')

LastWaveStart=truewaves[-1][0]
LastwaveEnd=truewaves[-1][1]

LastRFIEnd=rfi_end[-1]
LastRFIStart=rfi_start[-1]

LastWavePeriod=LastwaveEnd - LastWaveStart

LastWaveValueGain= data.loc[LastWaveStart:LastwaveEnd].Delta.sum()*100

CurrentWaveRSIRestart=data.query('RFI20<30 and daybefore>30').index[-1] 
dmin=data.loc[CurrentWaveRSIRestart:].Close.argmin()
CurrentWaveStart=data.loc[CurrentWaveRSIRestart:].iloc[dmin].name        

today = data.iloc[-1].name
CurrentPeriod= today - CurrentWaveStart

CurrentValueGain=data.loc[CurrentWaveStart:].Delta.sum()*100 # -->

TRelative=100*CurrentPeriod.days/LastWavePeriod.days #-->

GainRelative=100*CurrentValueGain/LastWaveValueGain # -->

Congruence=abs(TRelative-GainRelative) # -->

P= 100* (CurrentValueGain/LastWaveValueGain) / (abs(1-Congruence)) # -->

DeltaN=LastWavePeriod.days-CurrentPeriod.days # -->

YieldEst= LastWaveValueGain - CurrentValueGain   #-->

GainPerDayCurrent= 100* (CurrentValueGain/CurrentPeriod.days)

GainPerDayEstimated= 100* (LastWaveValueGain - CurrentValueGain)/(LastWavePeriod.days - CurrentPeriod.days)

Close=data.iloc[-1].Close

BollNeg2MA = (Close > data.iloc[-1]['Boll-']) and (Close <data.iloc[-1]['MA20'] )

MA2BollPos = (Close > data.iloc[-1]['MA20'] ) and (Close <data.iloc[-1]['Boll+'] )

line= [type, tickersymbol, tickername,  Close, LastWaveStart,LastwaveEnd,LastWavePeriod,
    LastWaveValueGain,CurrentWaveStart,CurrentPeriod, CurrentValueGain,TRelative,
    GainRelative,Congruence,P,DeltaN,YieldEst,GainPerDayCurrent,GainPerDayEstimated,
    BollNeg2MA,MA2BollPos]
#summary.loc[0] = line
insert(summary,line)

# Create analysis image
st.write('Summary')
#st.dataframe(summary.transpose())

#Plot 3 - All-in-One + Waves
fig, ax1 = plt.subplots()
data.Close.plot(figsize=(20,10),title=tickername,marker='o',style='-',ax=ax1)
data.MA20.plot(color='grey',label='MA20',ax=ax1)
data['Boll+'].plot(color='red',style='--',label='Bol+',ax=ax1)
data['Boll-'].plot(color='green',style='--',label='Bol-',ax=ax1)
#Polynomial 6 degree
x=np.array(range(data.shape[0]))
coefs=np.polyfit(x,data.Close,deg=6)
poly=np.poly1d(coefs)
y=poly(x)
plt.plot(data.index,y,color='purple',label='Poly-6')
ax1.set_ylim(auto=True)
ax1.set_ylabel('Close', color='blue')
ax1.legend(loc='upper left')
for truewave in truewaves:
    plt.plot([truewave[0]],data.loc[truewave[0]].Close,marker='+',color='red', markersize=30)
    plt.plot([truewave[1]],data.loc[truewave[1]].Close,marker='+',color='red', markersize=30)
plt.plot(CurrentWaveStart,data.loc[CurrentWaveStart].Close,marker='*',color='orange', markersize=30)

# Axis 2
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
data['RFI20'].plot(figsize=(20,10),color='black',ax=ax2)
data['RFI100'].plot(color='pink',ax=ax2)
ax2.axhline(y=30,color='y',linestyle ='--')
ax2.axhline(y=70,color='y',linestyle ='--')
for wave in waves:
    plt.plot([wave[0]],data.loc[wave[0]].RFI20,marker='o',color='red', markersize=20)
    plt.plot([wave[1]],data.loc[wave[1]].RFI20,marker='o',color='red', markersize=20)

ax2.set_ylabel('IFR', color='red')  # we already handled the x-label with ax1
ax2.set_yticks(list(range(0,110,10)))
ax2.legend()
fig.tight_layout() 
st.pyplot(fig)
#plt.close()


## Plot
###################
# Set up main app #
###################

st.write('Stock Price ')
#fig1=plt.Figure(1)
f,ax= plt.subplots(figsize=(20,10))
data.Close.plot(figsize=(20,10),title=tickername,marker='o',style='-')
data.MA20.plot(color='grey',label='MA20')
data['Boll+'].plot(color='green',style='--',label='Bol+')
data['Boll-'].plot(color='red',style='--',label='Bol-')
plt.legend(loc='upper left')
#plt.plot();
st.pyplot(f)
progress_bar = st.progress(0)

st.write('Stock RSI ')
#fig2=plt.Figure(2)
f2,ax= plt.subplots(figsize=(20,5))
data['RFI20'].plot(figsize=(20,5),title=tickername + ' - Indicators',color='black')
data['RFI100'].plot(color='pink')
plt.axhline(y=30,color='y',linestyle ='--')
plt.axhline(y=70,color='y',linestyle ='--')
plt.ylim(0,100)
plt.yticks(list(range(0,110,10)))
plt.legend(loc='upper left')
st.pyplot(f2)

st.write('Recent data ')
st.dataframe(data.tail(10))

# All-in-One
st.write('All-in-One ')
