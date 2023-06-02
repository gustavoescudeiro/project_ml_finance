from Data.reading_data import stocks_brazil
from Signal.momentum import get_momentum_signal
from Allocator.one_over_n import get_weights_one_over_n
import pandas as pd
import numpy as np

# Definindo dataframe com precos:
df_prices = stocks_brazil()



# Calculando sinal de momentum a partir do dataframe com precos
df_signal = get_momentum_signal(df = df_prices, window = 180, percentile = 0.25)

# Calculando pesos a partir dos sinais (1/n)
df_weights = get_weights_one_over_n(df_signal)


# Definindo frequencia do rebelanceamento d -> diaria, w -> semanal, m -> mensal, y -> anual
freq = "m"
dict_freq = {
            "d": ["d", "w", "m", "y"],
            "w": ["w", "m", "y"],
            "m": ["m", "y"],
            "y": ["y"]
             }

for period in dict_freq[freq]:
    if period == "d":
        df_prices[period] = df_prices.index.day
    if period == "w":
        df_prices[period] = df_prices.index.week
    if period == "m":
        df_prices[period] = df_prices.index.month
    if period == "y":
        df_prices[period] = df_prices.index.year

# Identificando datas de rebal
rebal_index = df_prices.groupby(dict_freq[freq]).tail(1).index
df_prices.drop(dict_freq[freq], axis= 1, inplace = True)
df_prices_period = df_prices[df_prices.index.isin(rebal_index)] # pesos em cada data de rebalanceamento

# Retorno no periodo de rebal
df_return_period = df_prices_period.pct_change()


initial_date = rebal_index[0]
value = 100000 # valor financeiro
initial_value = value
new_value = 0
dict_value = {}
list_signal = []

for index in df_prices_period.index[1:]:

    df_temp = df_prices[df_prices.index <= index] # df temporario com precos para usarmos para computar os sinais
    df_signal = get_momentum_signal(df = df_temp) # computando sinal
    df_weights = get_weights_one_over_n(df_signal.tail(1)) # computando pesos (usaremos aqui qualquer funcao, podendo ser risk parity, hierarchical risk parity, vol weighted
    df_notional = df_weights[df_weights.index == index] * initial_value # financeiro no tempo t
    df_qty = df_notional / df_prices[df_prices.index == index] # quantidade do papel que devemos ter em cada tempo t
    df_notional_end_of_period_delta = df_notional * (df_return_period[df_return_period.index == index])
    new_value = df_notional_end_of_period_delta.sum(axis=1)[0] # novo financeiro apos o fim do periodo antes de rebalancear
    initial_value += new_value # novo financeiro
    dict_value[index] = initial_value # salvando novo finaceiro da estrategia
    df_signal_t = df_signal[df_signal.index == index] # salvando o sinal para o tempo t
    list_signal.append(df_signal_t)
    print(index)




df_nav = pd.DataFrame(dict_value.items()) # salvando financeiros nos rebalanceamentos
df_nav.columns = ["Date", "nav"]
df_nav = df_nav.set_index(["Date"])
df_first_date = pd.DataFrame({initial_date:value}.items())
df_first_date.columns = ["Date", "nav"]
df_first_date = df_first_date.set_index(["Date"])
df_nav = pd.concat([df_first_date, df_nav])

df_new_qt = df_prices.merge(df_nav, left_index=True, right_index=True, how="left") # identificando as quantiades que deveremos ter apos cada rebalanceamento. Entre cada rebal as quantidades  permanecem constantes
for column in df_new_qt.columns[0:len(df_new_qt.columns)-1]:
    df_new_qt[column] = df_new_qt["nav"]/df_new_qt[column]

# Preenchendo quantidades com bfill
df_new_qt = df_new_qt.fillna(method="bfill")
df_prices["nav"] = 1

df_weights_adjusted = df_new_qt * df_prices
df_weights_adjusted.drop(["nav"], axis = 1, inplace = True)

# Multiplicando quantidades pela variacao de percentual de cada ativo
df_return_final = df_new_qt * df_prices.pct_change()

# Reconstruindo sinal baseado no periodo
df_signal_new = pd.concat(list_signal)
df_signal_new = df_signal_new.reindex(df_prices.index)
df_signal_new = df_signal_new.fillna(method="bfill")

# Ajustando pesos pelo sinal
df_weights_adjusted = df_weights_adjusted * df_signal_new
df_weights_adjusted["total_pos"] = df_weights_adjusted[df_weights_adjusted > 0].sum(axis=1)
df_weights_adjusted["total_neg"] = df_weights_adjusted[df_weights_adjusted < 0].sum(axis=1)

# Funcao para chegar no peso em %
for column in df_weights_adjusted.columns:
    mask_pos = df_weights_adjusted[column] > 0
    df_weights_adjusted.loc[mask_pos, column] = df_weights_adjusted[column]/df_weights_adjusted["total_pos"]
    mask_neg = df_weights_adjusted[column] < 0
    df_weights_adjusted.loc[mask_neg, column] = df_weights_adjusted[column] / df_weights_adjusted["total_neg"]

# pesos com sinais
df_weights_adjusted = df_weights_adjusted * df_signal_new


# Check de sanidade
df_check = df_weights_adjusted.sum(axis = 1)

# Backtest simplificado
df_return = df_weights_adjusted.shift(1) * df_prices.pct_change() # retorno de t0 * peso de t-1
df_return["total_return"] = df_return.sum(axis = 1)
df_return["cumulative_return"] = (1 + df_return["total_return"]).cumprod() - 1

df_return.to_excel(f"analise_estrategia_{freq}.xlsx")


