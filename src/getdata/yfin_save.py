import yfinance as yf
import pandas as pd

def save_yfinance_data(ticker: str = "BTC-JPY", period: str = "5y", interval: str = "1d", filename: str = "btcjpy_data_from_yfinance-5y-1d.csv")-> None:
    #https://github.com/ranaroussi/yfinance/wiki/Ticker
    ticker = yf.Ticker(ticker)
    hist = ticker.history(period=period, interval=interval)
    #hist.to_csv(filename)

if __name__ == '__main__':
    save_yfinance_data()