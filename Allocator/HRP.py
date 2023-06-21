import riskfolio as rp
import pandas as pd
import numpy as np


def get_weights_hrp(*args, df_signal=None, df_prices=None, window=60, **kwargs):

    try:

        if len(df_prices) < window:
            df_weights = pd.DataFrame(0, index=np.arange(1, 2), columns=df_prices.columns)
            df_weights["Date"] = df_prices.tail(1).index
            df_weights.set_index(["Date"], inplace=True)

            return df_weights

        # Filtrando janela
        df_prices = df_prices.iloc[-window:]
        df_prices.fillna(0, inplace = True)

        # Definindo dataframe com precos:
        r = df_prices.pct_change()
        r = r.fillna(0)

        # Calculando sinal de momentum a partir do dataframe com precos

        df_signal = df_signal.tail(1)

        # Verificando posicoes long
        df_signal_long = df_signal.loc[:, (df_signal == 1).any()]
        colunas_long = df_signal_long.columns
        # Verificando posicoes short
        df_signal_short = df_signal.loc[:, (df_signal == -1).any()]
        colunas_short = df_signal_short.columns

        # Computando pesos long
        r_long = r[colunas_long]
        r_long = r_long.loc[:, (r_long != 0).any(axis=0)] # desconsiderando ativo quando nao tiver retorno no periodo

        if len(df_signal_short) > 0:
            r_short = r[colunas_short]
            r_short = r_short.loc[:, (r_short != 0).any(axis=0)]  # desconsiderando ativo quando nao tiver retorno no periodo
        # Definindo parametros
        model = 'HRP'  # Could be HRP or HERC
        codependence = 'pearson'  # Correlation matrix used to group assets in clusters
        rm = 'MV'  # Risk measure used, this time will be variance
        rf = 0  # Risk free rate
        linkage = 'single'  # Linkage method used to build clusters
        max_k = 10  # Max number of clusters used in two difference gap statistic, only for HERC model
        leaf_order = True

        # Long
        port = rp.HCPortfolio(returns=r_long.dropna())
        # Consider optimal order of leafs in dendrogram
        df_weights_long = port.optimization(model=model,
                                            codependence=codependence,
                                            rm=rm,
                                            rf=rf,
                                            linkage=linkage,
                                            max_k=max_k,
                                            leaf_order=leaf_order)
        df_weights_long = df_weights_long.T.reset_index(drop=True)

        if len(df_signal_short.columns) > 0:
            port = rp.HCPortfolio(returns=r_short.dropna())
            df_weights_short = port.optimization(model=model,
                                                 codependence=codependence,
                                                 rm=rm,
                                                 rf=rf,
                                                 linkage=linkage,
                                                 max_k=max_k,
                                                 leaf_order=leaf_order)
            df_weights_short = df_weights_short.T.reset_index(drop=True)

        if len(df_signal_short.columns) > 0:
            df_weights = pd.concat([df_weights_long, df_weights_short], axis=1)
            df_weights = df_weights / 2
        else:
            df_weights = df_weights_long

        df_weights = df_weights * df_signal.reset_index(drop = True)
        df_weights = df_weights.fillna(0)
        df_weights["Date"] = df_prices.tail(1).index
        df_weights.set_index(["Date"], inplace=True)


    except:
        df_weights = pd.DataFrame(0, index=np.arange(1, 2), columns=df_prices.columns)
        df_weights["Date"] = df_prices.tail(1).index
        df_weights.set_index(["Date"], inplace = True)
        df_weights = df_weights * df_signal

        return df_weights


    return df_weights


