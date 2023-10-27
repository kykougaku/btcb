import yfinance as yf
import pandas as pd
import time

btcjpyticker = yf.Ticker("BTC-JPY")
hist = btcjpyticker.history(period="2y",interval="1h")


columns1 =["s", "l", "signal","gold","silver","assets"]
result = pd.DataFrame(columns=columns1)

yen_assets = 50000.0
btc_assets_yen = 50000.0
start = time.time()
for l in range(2,50):
    for s in range(1,l):
        for signal_span in range(2,25):

            hist["EMA"+str(s)] = hist["Close"].ewm(span=s).mean()
            hist["EMA"+str(l)] = hist["Close"].ewm(span=l).mean()
            hist["SMA25"] = hist["Close"].rolling(25).mean()
            hist["MACD"] = hist["EMA"+str(s)] - hist["EMA"+str(l)]
            hist["Signal"] = hist["MACD"].ewm(span=signal_span).mean()

            hist["before_MACD"] = hist["MACD"].shift()
            hist["before_Signal"] = hist["Signal"].shift()

            countg = 0
            counts = 0
            yen = yen_assets
            btc = btc_assets_yen/ hist["Close"].iloc[0]
            for idx,(macd,signal,before_macd,before_signal,close) in enumerate(zip(hist["MACD"].values,hist["Signal"].values,hist["before_MACD"].values,hist["before_Signal"].values,hist["Close"].values)):
                if(before_macd<before_signal and macd>signal):
                    countg += 1
                    yen,btc = 0,btc+(yen/close)
                elif(before_macd>before_signal and macd<signal):
                    counts += 1
                    yen,btc = yen+(btc*close),0

            total = yen + btc*hist["Close"].iloc[-1]
            adddata ={'s':s,'l':l,'signal':signal_span,'gold':countg,'silver':counts,'assets':total} 
            result = pd.concat([result, pd.DataFrame(adddata,index=[1])],ignore_index=True)
            print("EMA"+str(s)+"-"+str(l)+"-"+str(signal_span)+": ",countg,counts,total)
        result.to_csv("result_2y_1h.csv")

print("time: ",time.time()-start)