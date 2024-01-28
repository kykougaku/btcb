import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import talib as ta
import optuna
import xgboost as xgb
from xgboost import XGBClassifier
from xgboost import plot_importance
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold

csv_use_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
shift = 5

def twotype_label_func(x):
    if x > 0.02: return 1
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
    df["EMA100"] = ta.EMA(df["Close"], timeperiod=100)
    df["EMA200"] = ta.EMA(df["Close"], timeperiod=200)
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
        df["EMA100-{0}ratio".format(i)] = df["EMA100"].shift(i)/df["Close"]
        df["EMA200-{0}ratio".format(i)] = df["EMA200"].shift(i)/df["Close"]
        df["Volume-{0}".format(i)] = df["Volume"].shift(i)
        df["RSI-{0}".format(i)] = df["RSI"].shift(i)
        df["MFI-{0}".format(i)] = df["MFI"].shift(i)

    df.dropna(axis=0,inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def objective(trial,df_X,df_y):
    params ={
        'max_depth':trial.suggest_int("max_depth",1,10),
        'min_child_weight':trial.suggest_int('min_child_weight',1,5),
        'gamma':trial.suggest_float('gamma',0,1),
        'subsample':trial.suggest_float('subsample',0,1),
        'colsample_bytree':trial.suggest_float('colsample_bytree',0,1),
        'reg_alpha':trial.suggest_float('reg_alpha',1e-5,100,log=True),
        'reg_lambda':trial.suggest_float('reg_lambda',1e-5,100,log=True),        
        'learning_rate':trial.suggest_float('learning_rate',0,1)}

    model = XGBClassifier(**params)
    
    scores = cross_val_score(model, df_X, df_y, cv=5, scoring='accuracy')
    score_mean = scores.mean()
    
    return -1 * score_mean



def main():
    df = read_data()
    df = labeling(df)
    df = data_modify(df)
    print(df["target"].value_counts())

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
        mlcols.append("EMA100-{0}ratio".format(i))
        mlcols.append("EMA200-{0}ratio".format(i))
        mlcols.append("Volume-{0}".format(i))
        mlcols.append("RSI-{0}".format(i))
        mlcols.append("MFI-{0}".format(i))

    X = df[mlcols]
    Y = df["target"]
    print("train data")
    print(X.head())

    study = optuna.create_study()
    study.optimize(lambda trial: objective(trial,X,Y), n_trials=100)
    print("best params")
    print(study.best_params)

    best_params_training_data = xgb.cv(study.best_params, xgb.DMatrix(X, label=Y), num_boost_round=1000, nfold=5, metrics='auc', seed=0)
    plt.plot(best_params_training_data)
    plt.legend(best_params_training_data.columns)
    plt.savefig("best_params_training_data.png")
    plt.close()

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, shuffle=False)
    model = XGBClassifier(**study.best_params)
    model.fit(X_train, Y_train)
    Y_pred = model.predict(X_test)
    print("accuracy_score")
    print(accuracy_score(Y_test, Y_pred))
    plt.scatter(Y_test, Y_pred)
    plt.xlabel("Actual")
    plt.ylabel("Predicted")
    plt.savefig("prediction.png")
    plt.close()

    fig = plt.figure(figsize=(30,30),dpi=50)
    plot_importance(model)
    plt.savefig("feature_importance.png")
    plt.close()


if __name__ == "__main__":
    main()