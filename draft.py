import pandas as pd
import numpy as np

# Lendo df com cotacao das acoes
df_prices = pd.read_parquet("brazil_50_stocks.parquet")

# Filtrando somente campos com "Close" em seu nome
lista_campos = df_prices.columns
filtro_close = ["CLOSE" in x for x in lista_campos]
lista_campos_close = lista_campos[filtro_close]
df_prices = df_prices[lista_campos_close]

# Ajustando nome das colunas
df_prices.columns = [x.split("-")[0].strip() for x in df_prices.columns]

# Gerando score de momentum
window = 180
df_momentum = df_prices.shift(22)/df_prices.shift(window) - 1

# Ajustando ao risco
df_risk = df_prices.pct_change().rolling(window).std()
df_momentum_risk_adjusted = df_momentum/df_risk

# Calculando percentil
percentile = 0.25
upper_percentile = (df_momentum_risk_adjusted.quantile(q = percentile, axis = 1))
lower_percentile = (df_momentum_risk_adjusted.quantile(q = 1 - percentile, axis = 1))

# Criando df vazio e populando com sinais
df_signal = pd.DataFrame(columns = df_momentum_risk_adjusted.columns, index = df_momentum_risk_adjusted.index)
for column in df_momentum_risk_adjusted.columns:
    mask_upper = df_momentum_risk_adjusted[column] > upper_percentile
    df_signal.loc[mask_upper, column] = 1
    mask_lower = df_momentum_risk_adjusted[column] < lower_percentile
    df_signal.loc[mask_lower, column] = -1

# Definindo pesos
df_weights = df_signal.copy()
positive_count = df_weights[df_weights>0].count(axis=1)
negative_count = df_weights[df_weights<0].count(axis=1)

df_weights = pd.DataFrame(columns = df_signal.columns, index = df_signal.index)
for column in df_signal.columns:
    mask_positive = df_signal[column] == 1
    df_weights.loc[mask_positive, column] = 1/positive_count
    mask_negative = df_signal[column] == -1
    df_weights.loc[mask_negative, column] = -1/negative_count

# Sanity Check
df_check = df_weights.sum(axis = 1)

# Backtest simplificado
df_return = df_weights.shift(1) * df_prices.pct_change() # retorno de t0 * peso de t-1
df_return["total_return"] = df_return.sum(axis = 1)
df_return["cumulative_return"] = (1 + df_return["total_return"]).cumprod() - 1

df_return.to_excel("strategy.xlsx")


