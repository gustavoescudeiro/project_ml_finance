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
