import requests
import json
import datetime
import time
import os
import tqdm
import pickle
import pandas as pd

endPoint = 'https://api.coin.z.com/public'
path     = '/v1/ticker?symbol=BTC'

def get_gmo_data(path: str, endPoint: str = 'https://api.coin.z.com/public') -> dict:
    response = requests.get(endPoint + path)
    return response.json()

def get_ticker_data(ticker: str = 'BTC') -> dict:
    path = '/v1/ticker?symbol=' + ticker
    return get_gmo_data(path)

def get_status_data() -> dict:
    path = '/v1/status'
    return get_gmo_data(path)

def get_orderbooks_data(ticker: str = 'BTC') -> dict:
    path = '/v1/orderbooks?symbol=' + ticker
    return get_gmo_data(path)

def get_trades_data(ticker: str = 'BTC') -> dict:
    path = '/v1/trades?symbol=' + ticker
    return get_gmo_data(path)

def get_klines_data(ticker: str = 'BTC', interval: str = '1min', date: str = '20210417') -> dict:
    path = '/v1/klines?symbol=' + ticker + '&interval=' + interval + '&date=' + date
    return get_gmo_data(path)

def get_yyyymmdd() -> list:
    dt = datetime.datetime.today()
    yyyymmddlist = []
    while dt > datetime.datetime(2021, 4, 17):
        yyyymmddlist.append(format(dt, '%Y%m%d'))
        dt = dt - datetime.timedelta(days=1)
    yyyymmddlist = yyyymmddlist[::-1]
    return yyyymmddlist

def save_gmo_ohlcv(filedir: str) -> None:
    yyyymmddlist = get_yyyymmdd()
    for yyyymmdd in tqdm.tqdm(yyyymmddlist):
        dict = {yyyymmdd: get_klines_data(date=yyyymmdd)}
        time.sleep(1)
        filename = os.path.join(filedir, str(yyyymmdd) + '.json')
        with open(filename, 'w') as f:
            json.dump(dict, f, indent=4)

def open_json(filename: str = 'btcjpy_data_from_gmo.json') -> None:
    with open(filename, 'r') as f:
        data = json.load(f)
        print(data)

def convert2pickle(filedir: str) -> None:
    filelist = os.listdir(filedir)
    filelist = sorted(filelist)
    savedata = {}
    for filename in tqdm.tqdm(filelist):
        with open(os.path.join(filedir, filename), 'r') as f:
            data = json.load(f)
            yyyymmdd = filename.split('.')[0]
            savedata[yyyymmdd] = data
    with open(os.path.join(filedir, 'gmo_data.pkl'), 'wb') as f:
        pickle.dump(savedata, f)

def convert2pandas(filedir: str) -> pd.DataFrame:
    with open(os.path.join(filedir, 'gmo_data.pkl'), 'rb') as f:
        data = pickle.load(f)
    datalist = []
    for yyyymmdd, data in data.items():
        datalist_yyyymmdd = data[yyyymmdd]["data"]
        datalist.extend(datalist_yyyymmdd)
    pdata = pd.DataFrame(datalist)
    return pdata


if __name__ == '__main__':
    pass

    #save_gmo_ohlcv(filedir='../data/gmo')

    #convert2pickle(filedir='../data/gmo')

    #pdata = convert2pandas(filedir='../data/gmo')
    #pdata.to_csv('../data/gmo/gmo_data.csv', index=False)