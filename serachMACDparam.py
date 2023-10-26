import yfinance as yf
import pandas as pd
import time


btcjpyticker = yf.Ticker("BTC-JPY")
hist = btcjpyticker.history(period="1mo",interval="1h")


columns1 =["s", "l", "signal","gold","silver"]
result = pd.DataFrame(columns=columns1)

start = time.time()
for l in range(5,50):
    for s in range(1,l-1):
        for signal in range(5,20):
            countg = 0
            counts = 0
            hist["EMA"+str(s)] = hist["Close"].ewm(span=s).mean()
            hist["EMA"+str(l)] = hist["Close"].ewm(span=l).mean()
            hist["SMA25"] = hist["Close"].rolling(25).mean()

            hist["MACD"] = hist["EMA"+str(s)] - hist["EMA"+str(l)]
            hist["Signal"] = hist["MACD"].ewm(span=signal).mean()


            for i in range(len(hist.index)-1):
                if(hist.loc[:,'MACD'].iloc[i]<hist.loc[:,'Signal'].iloc[i] and hist.loc[:,'MACD'].iloc[i+1]>hist.loc[:,'Signal'].iloc[i+1]):
                    countg += 1
                elif(hist.loc[:,'MACD'].iloc[i]>hist.loc[:,'Signal'].iloc[i] and hist.loc[:,'MACD'].iloc[i+1]<hist.loc[:,'Signal'].iloc[i+1]):
                    counts += 1
            adddata ={'s':s,'l':l,'signal':signal,'gold':countg,'silver':counts} 
            result = pd.concat([result, pd.DataFrame(adddata,index=[1])],ignore_index=True)
            print("EMA"+str(s)+"-"+str(l)+"-"+str(signal)+": ",countg,counts)

print("time: ",time.time()-start)
result_s = result.sort_values('gold')
print(result_s)
result_s.to_csv("result.csv")