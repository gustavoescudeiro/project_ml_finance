import pandas as pd
import numpy as np
from datetime import datetime
from yahooquery import Ticker


def get_equity_data(equity_list, start_date=None, end_date=None, feature=['adjclose']):
    if end_date == None:
        end_date = str(datetime.today().date())
    else:
        end_date = end_date

    if start_date == None:
        start_date = datetime(1980, 1, 1).date()
    else:
        start_date = start_date

    dic_df = {}
    for i in equity_list:
        if i[0] == '^':
            equity = Ticker(i)
        else:
            equity = Ticker(i + ".SA")
        df = equity.history(start=pd.to_datetime(start_date), end=pd.to_datetime(end_date))
        if isinstance(df, pd.DataFrame):
            dic_df[i] = df
            print(f"Ação {i} baixada com sucesso")
        else:
            print(f"Ação {i} não encontrada")

    df_final = pd.concat(dic_df, axis=0)
    df_final = df_final.reset_index()
    df_final = df_final.rename(columns={'level_0': 'ticker'})
    df_final = df_final.pivot(index='date', columns='ticker')[feature]

    return df_final


def get_sgs_data(ticker_list):
    lista_df = []
    for codigo_bcb in ticker_list:
        url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json'.format(codigo_bcb)
        df = pd.read_json(url)
        df['variavel'] = codigo_bcb
        lista_df.append(df)

    df_bcb = pd.concat(lista_df, axis=0)
    df_bcb['data'] = pd.to_datetime(df_bcb['data']).dt.strftime('%d-%m-%Y %H:%M:%S')
    df_bcb['data'] = pd.to_datetime(df_bcb['data']).dt.strftime('%Y-%m-%d')
    df_bcb.rename(columns={df_bcb.columns[0]: 'date'}, inplace=True)
    df_bcb['date'] = pd.to_datetime(df_bcb['date'])
    df_bcb = df_bcb.reset_index(drop=True)
    df_bcb = df_bcb.pivot(index='date', columns='variavel')

    return df_bcb