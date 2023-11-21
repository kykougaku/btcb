import pandas as pd
import time
import talib as ta
hist = pd.read_csv("btcjpy_data_from_yfinance-2y-1d.csv")
hist["Date"] = pd.to_datetime(hist["Date"])
hist.set_index("Date",inplace=True)

columns1 =["s", "l", "signal","gold","silver","assets"]
result = pd.DataFrame(columns=columns1)

yen_assets = 50000.0
btc_assets_yen = 50000.0
spread = 0.999
start = time.time()
for l in range(2,50):
    for s in range(1,l):
        for signal_span in range(2,40):

            hist["EMA"+str(s)] = hist["Close"].ewm(span=s).mean()
            hist["EMA"+str(l)] = hist["Close"].ewm(span=l).mean()
            hist["SMA25"] = hist["Close"].rolling(25).mean()
            hist["MACD"] = hist["EMA"+str(s)] - hist["EMA"+str(l)]
            hist["Signal"] = hist["MACD"].ewm(span=signal_span).mean()

            hist["before_MACD"] = hist["MACD"].shift()
            hist["before_Signal"] = hist["Signal"].shift()

            hist["upper_sigma5"], _, hist["lower_sigma5"] = ta.BBANDS(hist["Close"], timeperiod=25, nbdevup=5, nbdevdn=5, matype=ta.MA_Type.SMA)

            mode = 1

            countg = 0
            counts = 0

            yen = yen_assets
            btc = btc_assets_yen/ hist["Close"].iloc[0]
            premode = 2
            for idx,(macd,signal,before_macd,before_signal,close,upsigma4,losigma4) in enumerate(zip(hist["MACD"].values,hist["Signal"].values,hist["before_MACD"].values,hist["before_Signal"].values,hist["Close"].values,hist["upper_sigma4"].values,hist["lower_sigma4"].values)):
                if(close<losigma4 or upsigma4<close):
                    if mode != 1: premode = mode
                    mode = 1
                elif(losigma4<close and close<upsigma4 and mode==1):
                    mode = premode

                if(before_macd<before_signal and macd>signal and mode==2):
                    countg += 1
                    yen,btc = 0,btc+(spread*yen/close)
                    mode = 3
                elif(before_macd>before_signal and macd<signal and mode == 3):
                    counts += 1
                    yen,btc = yen+(spread*btc*close),0
                    mode = 2

            total = yen + btc*hist["Close"].iloc[-1]
            adddata ={'s':s,'l':l,'signal':signal_span,'gold':countg,'silver':counts,'assets':total} 
            result = pd.concat([result, pd.DataFrame(adddata,index=[1])],ignore_index=True)
            print("EMA"+str(s)+"-"+str(l)+"-"+str(signal_span)+": ",countg,counts,total)
        result.to_csv("result_2y_1d.csv")

print("time: ",time.time()-start)