import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

btcjpyticker = yf.Ticker("BTC-JPY")

hist = btcjpyticker.history(period="1mo",interval="1h")

print(hist)
print(hist.columns)
print(hist.index)
print(type(hist))
plt.plot(hist.Close)
plt.show()
