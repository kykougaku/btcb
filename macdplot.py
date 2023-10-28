import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


class assets:
    yen = 0.0
    btc = 0.0
    def __init__(self, yen, btc_yen, rate):
        self.yen = yen
        self.btc = btc_yen/rate
    def set_yen(self, yen):
        self.yen = yen
    def set_btc(self, btc_yen, rate):
        self.btc = btc_yen/rate
    def get_yen(self):
        return self.yen
    def get_btc(self):
        return self.btc
    def buy_btc_all(self, rate):
        self.btc += self.yen/rate
        self.yen = 0
    def sell_btc_all(self, rate):
        self.yen += self.btc*rate
        self.btc = 0
    def get_total(self, rate):
        return self.yen + self.btc*rate


btcjpyticker = yf.Ticker("BTC-JPY")
hist = btcjpyticker.history(period="2y",interval="1h")
"""
print(hist)
print(hist.columns)
print(hist.index)
print(type(hist))
"""
s = 16
l = 23
sig = 15

yen_assets = 50000.0
btc_assets_yen = 50000.0
myassets = assets(yen_assets,btc_assets_yen,hist.loc[:,'Close'].iloc[0])

hist["EMA"+str(s)] = hist["Close"].ewm(span=s).mean()
hist["EMA"+str(l)] = hist["Close"].ewm(span=l).mean()
hist["SMA25"] = hist["Close"].rolling(25).mean()
hist["MACD"] = hist["EMA"+str(s)] - hist["EMA"+str(l)]
hist["Signal"] = hist["MACD"].ewm(span=sig).mean()

hist["g_point"] = False
hist["s_point"] = False
hist["yen"] = yen_assets
hist["btc"] = btc_assets_yen
hist["total"] = yen_assets + btc_assets_yen

for i in range(len(hist.index)-1):
    hist.loc[:,'yen'].iat[i+1] = myassets.get_yen()
    hist.loc[:,'btc'].iat[i+1] = myassets.get_btc()
    hist.loc[:,'total'].iat[i+1] = myassets.get_total(hist.loc[:,'Close'].iloc[i+1])

    if(hist.loc[:,'MACD'].iloc[i]<hist.loc[:,'Signal'].iloc[i] and hist.loc[:,'MACD'].iloc[i+1]>hist.loc[:,'Signal'].iloc[i+1]): 
        hist["g_point"].iat[i+1] = True
        myassets.buy_btc_all(hist.loc[:,'Close'].iloc[i+1])
    elif(hist.loc[:,'MACD'].iloc[i]>hist.loc[:,'Signal'].iloc[i] and hist.loc[:,'MACD'].iloc[i+1]<hist.loc[:,'Signal'].iloc[i+1]):
        hist["s_point"].iat[i+1] = True
        myassets.sell_btc_all(hist.loc[:,'Close'].iloc[i+1])


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
print(hist.loc[:,'total'].iat[-1])
print(myassets.get_total(hist.loc[:,'Close'].iat[-1]))
print(hist)
plt.savefig("fig"+str(s)+"-"+str(l)+"-"+str(sig)+".png",dpi=300)
plt.show()
