import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import time

btcjpyticker = yf.Ticker("BTC-JPY")
hist = btcjpyticker.history(period="1mo",interval="1h")

yen_assets = 50000.0
btc_assets_yen = 50000.0

s = 45
l = 47
sig = 10

starttime = time.time()

hist["EMA"+str(s)] = hist["Close"].ewm(span=s).mean()
hist["EMA"+str(l)] = hist["Close"].ewm(span=l).mean()
hist["SMA25"] = hist["Close"].rolling(25).mean()
hist["MACD"] = hist["EMA"+str(s)] - hist["EMA"+str(l)]
hist["Signal"] = hist["MACD"].ewm(span=sig).mean()

hist["before_MACD"] = hist["MACD"].shift()
hist["before_Signal"] = hist["Signal"].shift()

hist.drop(index=hist.index[[0,1]],inplace=True)


g_point =[]
s_point =[]
yens = []
btcs = []
yen = yen_assets
btc = btc_assets_yen/ hist["Close"].iloc[0]
for idx,(macd,signal,before_macd,before_signal,close) in enumerate(zip(hist["MACD"].values,hist["Signal"].values,hist["before_MACD"].values,hist["before_Signal"].values,hist["Close"].values)):
    if(before_macd<before_signal and macd>signal): 
        g_point.append(True)
        s_point.append(False)
        yen,btc = 0,btc+(yen/close)
    elif(before_macd>before_signal and macd<signal):
        g_point.append(False)
        s_point.append(True)
        yen,btc = yen+(btc*close),0
    else:
        g_point.append(False)
        s_point.append(False)
    yens.append(yen)
    btcs.append(btc)
hist["g_point"] = g_point
hist["s_point"] = s_point

hist["yen"] = yens
hist["btc"] = btcs
hist["total"] = hist["yen"] + hist["btc"]*hist["Close"]
print(hist['g_point'].sum())
print(time.time()-starttime)
print(hist.loc[:,["MACD","before_MACD","Signal","before_Signal","Close","yen","btc","total"]])

fig = plt.figure()

up = fig.add_subplot(3,1,1)
down = fig.add_subplot(3,1,2)
down2 = fig.add_subplot(3,1,3)

up.plot(hist.index,hist["Close"],color="black")
up.plot(hist.index,hist["SMA25"],color="orange")
down.plot(hist.index,hist["MACD"],color="blue")
down.plot(hist.index,hist["Signal"],color="red")
down2.plot(hist.index,hist["total"],color="black")

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
hist.to_csv("hist.csv")
plt.show()