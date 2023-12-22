import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
import talib as ta
from sklearn.model_selection import cross_val_score
import lightgbm as lgb

csv_use_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
shift = 5

def twotype_label_func(x):
    if x < -0.05: return 1
    else: return 0

def read_data():
    df = pd.read_csv("btcjpy_data_from_yfinance-5y-1d.csv",usecols=csv_use_cols)
    return df

def labeling(df):
    df["diff_ratio"] = df["Close"].diff()/df["Close"] 
    df["target"] = np.vectorize(twotype_label_func)(df["diff_ratio"])
    df["target"] = df["target"].shift(-1)
    return df

def data_modify(df):
    df["EMA5"] = ta.EMA(df["Close"], timeperiod=5)
    df["EMA10"] = ta.EMA(df["Close"], timeperiod=10)
    df["EMA25"] = ta.EMA(df["Close"], timeperiod=25)
    df["EMA50"] = ta.EMA(df["Close"], timeperiod=50)
    df["EMA75"] = ta.EMA(df["Close"], timeperiod=75)
    df["RSI"] = ta.RSI(df["Close"], timeperiod=14)
    df["MFI"] = ta.MFI(df["High"], df["Low"], df["Close"], df["Volume"], timeperiod=14)

    for i in range(0, shift+1):
        df["Open-{0}ratio".format(i)] = df["Open"].shift(i)/df["Close"]
        df["High-{0}ratio".format(i)] = df["High"].shift(i)/df["Close"]
        df["Low-{0}ratio".format(i)] = df["Low"].shift(i)/df["Close"]
        df["Close-{0}ratio".format(i)] = df["Close"].shift(i)/df["Close"]
        df["EMA5-{0}ratio".format(i)] = df["EMA5"].shift(i)/df["Close"]
        df["EMA10-{0}ratio".format(i)] = df["EMA10"].shift(i)/df["Close"]
        df["EMA25-{0}ratio".format(i)] = df["EMA25"].shift(i)/df["Close"]
        df["EMA50-{0}ratio".format(i)] = df["EMA50"].shift(i)/df["Close"]
        df["EMA75-{0}ratio".format(i)] = df["EMA75"].shift(i)/df["Close"]
        df["Volume-{0}".format(i)] = df["Volume"].shift(i)
        df["RSI-{0}".format(i)] = df["RSI"].shift(i)
        df["MFI-{0}".format(i)] = df["MFI"].shift(i)

    df.dropna(axis=0,inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def get_score(X, Y,scoring):
    my_pipeline = Pipeline(steps=[("model", lgb.LGBMClassifier(n_estimators=5000, learning_rate=0.005,n_jobs=4,random_state=0))])
    return cross_val_score(my_pipeline, X, Y, cv=4, scoring=scoring).mean()

def main():
    df = read_data()
    df = labeling(df)
    df = data_modify(df)

    print(df.head())

    mlcols = []
    for i in range(0, shift+1):
        mlcols.append("Open-{0}ratio".format(i))
        mlcols.append("High-{0}ratio".format(i))
        mlcols.append("Low-{0}ratio".format(i))
        mlcols.append("Close-{0}ratio".format(i))
        mlcols.append("EMA5-{0}ratio".format(i))
        mlcols.append("EMA10-{0}ratio".format(i))
        mlcols.append("EMA25-{0}ratio".format(i))
        mlcols.append("EMA50-{0}ratio".format(i))
        mlcols.append("EMA75-{0}ratio".format(i))
        mlcols.append("Volume-{0}".format(i))
        mlcols.append("RSI-{0}".format(i))
        mlcols.append("MFI-{0}".format(i))

    X = df[mlcols]
    Y = df["target"]
    print(get_score(X=X,Y=Y,scoring='precision'))

if __name__ == "__main__":
    main()