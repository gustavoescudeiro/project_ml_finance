import pandas as pd
import numpy as np

def get_momentum_signal(df = None, window = 180, percentile = 0.25):

    df_prices = df.copy()
    df_momentum = df_prices.shift(22) / df_prices.shift(window) - 1

    # Ajustando ao risco
    df_risk = df_prices.pct_change().rolling(window).std()
    df_momentum_risk_adjusted = df_momentum / df_risk

    # Calculando percentil
    upper_percentile = (df_momentum_risk_adjusted.quantile(q=percentile, axis=1))
    lower_percentile = (df_momentum_risk_adjusted.quantile(q=1 - percentile, axis=1))

    # Criando df vazio e populando com sinais
    df_signal = pd.DataFrame(columns=df_momentum_risk_adjusted.columns, index=df_momentum_risk_adjusted.index)
    for column in df_momentum_risk_adjusted.columns:
        mask_upper = df_momentum_risk_adjusted[column] > upper_percentile
        df_signal.loc[mask_upper, column] = 1
        mask_lower = df_momentum_risk_adjusted[column] < lower_percentile
        df_signal.loc[mask_lower, column] = -1

    return df_signal