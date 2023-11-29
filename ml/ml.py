import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import talib as ta

import sklearn

df = pd.read_csv("btcjpy_data_from_yfinance-2y-1d.csv")
df["diff"] = df["Close"] - df["Open"]
df["diff_ratio"] = df["diff"] / df["Open"]

plt.hist(df["diff_ratio"], bins=100)
plt.show()