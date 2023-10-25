import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


btcjpyticker = yf.Ticker("BTC-JPY")
hist = btcjpyticker.history(period="1mo",interval="1h")
"""
print(hist)
print(hist.columns)
print(hist.index)
print(type(hist))
"""
hist["EMA5"] = hist["Close"].ewm(span=5).mean()
hist["EMA25"] = hist["Close"].ewm(span=25).mean()
hist["SMA25"] = hist["Close"].rolling(25).mean()

hist["MACD"] = hist["EMA5"] - hist["EMA25"]
hist["Signal"] = hist["MACD"].ewm(span=9).mean()


hist["g_point"] = False
hist["s_point"] = False
for i in range(len(hist.index)-1):
    hist["g_point"].iat[i+1] = False
    if(hist.MACD[i]<hist.Signal[i] and hist.MACD[i+1]>hist.Signal[i+1]):
        hist["g_point"].iat[i+1] = True
    elif(hist.MACD[i]>hist.Signal[i] and hist.MACD[i+1]<hist.Signal[i+1]):
        hist["s_point"].iat[i+1] = True


fig = plt.figure()

up = fig.add_subplot(2,1,1)
down = fig.add_subplot(2,1,2)

up.plot(hist.index,hist["Close"],color="black")
up.plot(hist.index,hist["EMA5"],color="green")
up.plot(hist.index,hist["SMA25"],color="orange")
down.plot(hist.index,hist["MACD"],color="blue")
down.plot(hist.index,hist["Signal"],color="red")

for i in range(len(hist.index)):
    if(hist.g_point[i]):
        up.scatter(hist.index[i],hist["Close"][i],facecolor="none",edgecolors="blue",)
        down.scatter(hist.index[i],hist["MACD"][i],facecolor="none",edgecolors="blue")
    elif(hist.s_point[i]):
        up.scatter(hist.index[i],hist["Close"][i],facecolor="none",edgecolors="red",)
        down.scatter(hist.index[i],hist["MACD"][i],facecolor="none",edgecolors="red")

up.legend(["Close","EMA5"])
down.legend(["MACD","Signal"])

plt.savefig("fig.png",dpi=3000)
plt.show()
