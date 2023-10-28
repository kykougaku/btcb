import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import talib as ta
import numpy as np
"""
btcjpyticker = yf.Ticker("BTC-JPY")
hist = btcjpyticker.history(period="2y",interval="1h")
"""
hist = pd.read_csv("btcjpy_data_from_yfinance-2y-1h.csv")
hist["Datetime"] = pd.to_datetime(hist["Datetime"])
hist.set_index("Datetime",inplace=True)

print(hist.head())
spread = 0.9999
yen_assets = 50000.0
btc_assets_yen = 50000.0

s = 13
l = 29
sig = 14


hist["EMA"+str(s)] = hist["Close"].ewm(span=s).mean()
hist["EMA"+str(l)] = hist["Close"].ewm(span=l).mean()
hist["SMA25"] = hist["Close"].rolling(25).mean()
hist["MACD"] = hist["EMA"+str(s)] - hist["EMA"+str(l)]
hist["Signal"] = hist["MACD"].ewm(span=sig).mean()

hist["before_MACD"] = hist["MACD"].shift()
hist["before_Signal"] = hist["Signal"].shift()

hist["upper_sigma4"], _, hist["lower_sigma4"] = ta.BBANDS(hist["Close"], timeperiod=25, nbdevup=4, nbdevdn=4, matype=ta.MA_Type.SMA)

hist.drop(index=hist.index[[0,1]],inplace=True)

mode = 1
g_point =[]
s_point =[]
yens = []
btcs = []

macd_grads = []
signal_grads = []
profits = []

yen = yen_assets
btc = btc_assets_yen/ hist["Close"].iloc[0]
for idx,(macd,signal,before_macd,before_signal,close,upsigma4,losigma4) in enumerate(zip(hist["MACD"].values,hist["Signal"].values,hist["before_MACD"].values,hist["before_Signal"].values,hist["Close"].values,hist["upper_sigma4"].values,hist["lower_sigma4"].values)):
    if(close<losigma4 or upsigma4<close):
        mode = 1
    elif(losigma4<close and close<upsigma4 and mode==1):
        mode = 2

    if(before_macd<before_signal and macd>signal and mode==2): 
        g_point.append(True)
        s_point.append(False)
        yen,btc = 0,btc+(spread*yen/close)
        mode = 3

        macd_grads.append(macd-before_macd)
        signal_grads.append(signal-before_signal)
        tempo = btc*close
    elif(before_macd>before_signal and macd<signal and mode == 3):
        g_point.append(False)
        s_point.append(True)
        yen,btc = yen+(spread*btc*close),0
        mode = 2

        profits.append(yen-tempo)
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
print("golden_cross"+str(hist['g_point'].sum()))
print(hist.loc[:,["MACD","before_MACD","Signal","before_Signal","Close","yen","btc","total"]])

fig = plt.figure()

up = fig.add_subplot(3,1,1)
down = fig.add_subplot(3,1,2)
down2 = fig.add_subplot(3,1,3)

up.plot(hist.index,hist["Close"],color="black")
up.plot(hist.index,hist["SMA25"],color="orange")
up.plot(hist.index,hist["lower_sigma4"],color="red")
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

plt.savefig("fig"+str(s)+"-"+str(l)+"-"+str(sig)+".png",dpi=300)
plt.show()
grad_datas = pd.DataFrame(list(zip(macd_grads,signal_grads,profits)),columns=["MACD_grad","Signal_grad","profit"])
fig2 = plt.figure()
plt.scatter(grad_datas["MACD_grad"],grad_datas["Signal_grad"],c=grad_datas["profit"],cmap="jet")
plt.colorbar()
plt.show()

fig3 = plt.figure()
plt.scatter(grad_datas["MACD_grad"]*((grad_datas["MACD_grad"]-grad_datas["Signal_grad"])**2.0),grad_datas["profit"])
plt.show()