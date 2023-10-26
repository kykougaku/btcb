import yfinance as yf
import pandas as pd
import time

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
hist = btcjpyticker.history(period="1y",interval="1h")


columns1 =["s", "l", "signal","gold","silver","assets"]
result = pd.DataFrame(columns=columns1)

yen_assets = 50000.0
btc_assets_yen = 50000.0
myassets = assets(yen_assets,btc_assets_yen,hist["Close"].iloc[0])
start = time.time()
for l in range(5,50):
    for s in range(1,l):
        for signal in range(5,20):
            countg = 0
            counts = 0
            myassets.set_btc(btc_assets_yen,hist["Close"].iloc[0])
            myassets.set_yen(yen_assets)
            hist["EMA"+str(s)] = hist["Close"].ewm(span=s).mean()
            hist["EMA"+str(l)] = hist["Close"].ewm(span=l).mean()
            hist["SMA25"] = hist["Close"].rolling(25).mean()

            hist["MACD"] = hist["EMA"+str(s)] - hist["EMA"+str(l)]
            hist["Signal"] = hist["MACD"].ewm(span=signal).mean()


            for i in range(len(hist.index)-1):
                if(hist.loc[:,'MACD'].iloc[i]<hist.loc[:,'Signal'].iloc[i] and hist.loc[:,'MACD'].iloc[i+1]>hist.loc[:,'Signal'].iloc[i+1]):
                    countg += 1
                    myassets.buy_btc_all(hist.loc[:,'Close'].iloc[i+1])
                elif(hist.loc[:,'MACD'].iloc[i]>hist.loc[:,'Signal'].iloc[i] and hist.loc[:,'MACD'].iloc[i+1]<hist.loc[:,'Signal'].iloc[i+1]):
                    counts += 1
                    myassets.sell_btc_all(hist.loc[:,'Close'].iloc[i+1])

            adddata ={'s':s,'l':l,'signal':signal,'gold':countg,'silver':counts,'assets':myassets.get_total(hist.loc[:,'Close'].iloc[-1])} 
            result = pd.concat([result, pd.DataFrame(adddata,index=[1])],ignore_index=True)
            print("EMA"+str(s)+"-"+str(l)+"-"+str(signal)+": ",countg,counts,myassets.get_total(hist.loc[:,'Close'].iat[-1]))

print("time: ",time.time()-start)
result_s = result.sort_values('assets',ascending=False)
print(result_s)
result_s.to_csv("result.csv")