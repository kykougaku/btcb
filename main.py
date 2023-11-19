import pandas as pd
import matplotlib.pyplot as plt
import talib as ta

hist = pd.read_csv("btcjpy_data_from_yfinance-2y-1h.csv")
hist["Datetime"] = pd.to_datetime(hist["Datetime"])
hist.set_index("Datetime",inplace=True)

print(hist.head())
spread = 0.999
yen_assets = 50000.0
btc_assets_yen = 50000.0

s = 13
l = 29
sig = 14
sma = 25
ema = 50


hist["EMA"+str(s)] = hist["Close"].ewm(span=s).mean()
hist["EMA"+str(l)] = hist["Close"].ewm(span=l).mean()
hist["SMA"+str(sma)] = hist["Close"].rolling(sma).mean()
hist["EMA"+str(ema)] = hist["Close"].ewm(span=ema).mean()
hist["MACD"] = hist["EMA"+str(s)] - hist["EMA"+str(l)]
hist["Signal"] = hist["MACD"].ewm(span=sig).mean()

hist["before_MACD"] = hist["MACD"].shift()
hist["before_Signal"] = hist["Signal"].shift()
hist["before_SMA"+str(sma)] = hist["SMA"+str(sma)].shift()
hist["before_EMA"+str(ema)] = hist["EMA"+str(ema)].shift()

hist["upper_sigma4"], _, hist["lower_sigma4"] = ta.BBANDS(hist["Close"], timeperiod=25, nbdevup=5, nbdevdn=5, matype=ta.MA_Type.SMA)

hist.drop(index=hist.index[[0,1]],inplace=True)

mode = 1
g_point =[]
s_point =[]
yens = []
btcs = []

smas = []
emas = [] 
closes = []
macd_grads = []
signal_grads = []
sma_grads = []
ema_grads = []
profits = []
buy_index = []
sell_index = []
modes = []

yen = yen_assets
btc = btc_assets_yen/ hist["Close"].iloc[0]
premode = 2
for idx,(macd,signal,before_macd,before_signal,close,upsigma4,losigma4,smass,emass,before_smass,before_emass) in enumerate(zip(hist["MACD"].values,hist["Signal"].values,hist["before_MACD"].values,hist["before_Signal"].values,hist["Close"].values,hist["upper_sigma4"].values,hist["lower_sigma4"].values,hist["SMA"+str(sma)].values,hist["EMA"+str(ema)].values,hist["before_SMA"+str(sma)].values,hist["before_EMA"+str(ema)].values)):
    if(close<losigma4 or upsigma4<close):
        if mode != 1: premode = mode
        mode = 1
    elif(losigma4<close and close<upsigma4 and mode==1):
        mode = premode

    if(before_macd<before_signal and macd>signal and mode==2): 
        g_point.append(True)
        s_point.append(False)
        yen,btc = 0,btc+(spread*yen/close)
        mode = 3

        macd_grads.append(macd-before_macd)
        signal_grads.append(signal-before_signal)
        smas.append(smass)
        emas.append(emass)
        sma_grads.append(smass-before_smass)
        ema_grads.append(emass-before_emass)
        closes.append(close)
        buy_index.append(hist.index[idx])

        tempo = btc*close
    elif(before_macd>before_signal and macd<signal and mode == 3):
        g_point.append(False)
        s_point.append(True)
        yen,btc = yen+(spread*btc*close),0
        mode = 2

        profits.append(yen-tempo)
        sell_index.append(hist.index[idx])
    else:
        g_point.append(False)
        s_point.append(False)
    yens.append(yen)
    btcs.append(btc)
    modes.append(mode)

hist["g_point"] = g_point
hist["s_point"] = s_point
hist["mode"] = modes

hist["yen"] = yens
hist["btc"] = btcs
hist["total"] = hist["yen"] + hist["btc"]*hist["Close"]
print("golden_cross"+str(hist['g_point'].sum()))
print(hist.loc[:,["MACD","before_MACD","Signal","before_Signal","Close","yen","btc","total"]])

hist.to_csv("hist"+str(s)+"-"+str(l)+"-"+str(sig)+".csv")

fig = plt.figure()

up = fig.add_subplot(3,1,1)
down = fig.add_subplot(3,1,2)
down2 = fig.add_subplot(3,1,3)

up.plot(hist.index,hist["Close"],color="black")
up.plot(hist.index,hist["SMA"+str(sma)],color="orange")
up.plot(hist.index,hist["EMA"+str(ema)],color="green")
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

up.legend(["Close","SMA"+str(sma),"EMA"+str(ema),"lower_sigma4"])
down.legend(["MACD","Signal"])

down.text(hist.index[0],5000,"s="+str(s)+"\nl="+str(l)+'\nsignal='+str(sig),fontsize=10)

plt.savefig("fig"+str(s)+"-"+str(l)+"-"+str(sig)+".png",dpi=800)
plt.show()

grad_datas = pd.DataFrame(list(zip(macd_grads,signal_grads,profits,smas,emas,closes,sma_grads,ema_grads,buy_index,sell_index)),columns=["MACD_grad","Signal_grad","profit","SMA"+str(sma),"EMA"+str(ema),"Close","SMA_grad","EMA_grad","buy_index","sell_index"])
print(grad_datas.head())
grad_datas.to_csv("grad_datas"+str(s)+"-"+str(l)+"-"+str(sig)+".csv")

fig2 = plt.figure()
plt.scatter(grad_datas["SMA_grad"],grad_datas["profit"])
plt.show()