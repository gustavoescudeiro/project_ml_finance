import pandas as pd

def stocks_brazil():

    # Lendo df com cotacao das acoes
    df_prices = pd.read_parquet("brazil_50_stocks.parquet")

    # Filtrando somente campos com "Close" em seu nome
    lista_campos = df_prices.columns
    filtro_close = ["CLOSE" in x for x in lista_campos]
    lista_campos_close = lista_campos[filtro_close]
    df_prices = df_prices[lista_campos_close]

    # Ajustando nome das colunas
    df_prices.columns = [x.split("-")[0].strip() for x in df_prices.columns]

    return df_prices


def multiclass():

    # Lendo df
    df_prices = pd.read_parquet("dados_aula.parquet")
    df_prices = df_prices.reset_index(drop=False)
    df_prices.rename(columns={"DATE": "Date"}, inplace=True)
    df_prices["Date"] = pd.to_datetime(df_prices["Date"])
    df_prices.set_index(["Date"], inplace=True)
    df_prices.drop(["DOGEUSD"],axis = 1, inplace = True)


    return df_prices


def etfs_b3():

    # Lendo df
    df_prices = pd.read_pickle("etfs.pkl")
    df_prices = df_prices.reset_index(drop=False)
    df_prices.rename(columns={"date": "Date"}, inplace=True)
    df_prices["Date"] = pd.to_datetime(df_prices["Date"])
    df_prices.set_index(["Date"], inplace=True)



    return df_prices
