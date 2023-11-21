import yfinance as yf
import pandas as pd

btcjpyticker = yf.Ticker("BTC-JPY")
hist = btcjpyticker.history(period="2y",interval="1d")

#hist.to_csv("btcjpy_data_from_yfinance-2y-1d.csv")

histfromcsv = pd.read_csv("btcjpy_data_from_yfinance-2y-1d.csv",index_col=0)

print(hist.dtypes)
print(histfromcsv.dtypes)