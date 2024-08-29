import yfinance as yf
import pandas as pd

#https://github.com/ranaroussi/yfinance/wiki/Ticker
btcjpyticker = yf.Ticker("BTC-JPY")
hist = btcjpyticker.history(period="5y",interval="1d")

#hist.to_csv("btcjpy_data_from_yfinance-5y-1d.csv")

histfromcsv = pd.read_csv("btcjpy_data_from_yfinance-5y-1d.csv",index_col=0)

print(hist.dtypes)
print(histfromcsv.dtypes)