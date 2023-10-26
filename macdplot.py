import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


btcjpyticker = yf.Ticker("BTC-JPY")
hist = btcjpyticker.history(period="1y",interval="1h")
"""
print(hist)
print(hist.columns)
print(hist.index)
print(type(hist))
"""
s = 46
l = 48
sig = 19
hist["EMA"+str(s)] = hist["Close"].ewm(span=s).mean()
hist["EMA"+str(l)] = hist["Close"].ewm(span=l).mean()
hist["SMA25"] = hist["Close"].rolling(25).mean()

hist["MACD"] = hist["EMA"+str(s)] - hist["EMA"+str(l)]
hist["Signal"] = hist["MACD"].ewm(span=sig).mean()


hist["g_point"] = False
hist["s_point"] = False
for i in range(len(hist.index)-1):
    hist["g_point"].iat[i+1] = False
    if(hist.loc[:,'MACD'].iloc[i]<hist.loc[:,'Signal'].iloc[i] and hist.loc[:,'MACD'].iloc[i+1]>hist.loc[:,'Signal'].iloc[i+1]): 
        hist["g_point"].iat[i+1] = True
    elif(hist.loc[:,'MACD'].iloc[i]>hist.loc[:,'Signal'].iloc[i] and hist.loc[:,'MACD'].iloc[i+1]<hist.loc[:,'Signal'].iloc[i+1]):
        hist["s_point"].iat[i+1] = True


fig = plt.figure()

up = fig.add_subplot(2,1,1)
down = fig.add_subplot(2,1,2)

up.plot(hist.index,hist["Close"],color="black")
up.plot(hist.index,hist["SMA25"],color="orange")
down.plot(hist.index,hist["MACD"],color="blue")
down.plot(hist.index,hist["Signal"],color="red")

for i in range(len(hist.index)):
    if(hist.loc[:,'g_point'].iloc[i]):
        up.scatter(hist.index[i],hist.loc[:,'Close'].iloc[i],facecolor="none",edgecolors="blue",)
        down.scatter(hist.index[i],hist.loc[:,'MACD'].iloc[i],facecolor="none",edgecolors="blue")
    elif(hist.loc[:,'s_point'].iloc[i]):
        up.scatter(hist.index[i],hist.loc[:,'Close'].iloc[i],facecolor="none",edgecolors="red",)
        down.scatter(hist.index[i],hist.loc[:,'MACD'].iloc[i],facecolor="none",edgecolors="red")

up.legend(["Close","SMA25"])
down.legend(["MACD","Signal"])

down.text(hist.index[0],5000,"s="+str(s)+"\nl="+str(l)+'\nsignal='+str(sig),fontsize=10)

plt.savefig("fig.png",dpi=300)
plt.show()
