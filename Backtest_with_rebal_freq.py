from Data.reading_data import stocks_brazil, multiclass
from Signal.momentum import get_momentum_signal
from Signal.buy_and_hold import get_buy_and_hold_signal
from Allocator.one_over_n import get_weights_one_over_n
from Allocator.HRP import get_weights_hrp
import pandas as pd
import numpy as np
import datetime

def rebalance(current_total_aum = None, df_new_weights = None, df_prices_d0 = None, df_current_qt = None):


    df_new_notional = df_new_weights * current_total_aum
    df_new_qt = df_new_notional / df_prices_d0
    # Adicionando colunas com 0 caso estejam com novo peso definido (entrando pela primeira vez)
    list_new_assets = list(set(df_new_weights) - set(df_current_qt))
    if len(list_new_assets) > 0:
        for asset in list_new_assets:
            df_current_qt[asset] = 0
    df_new_qt.fillna(0,inplace = True)
    df_current_qt.fillna(0,inplace = True)
    df_qt_dif = df_new_qt - df_current_qt



    return df_qt_dif

# Definindo dataframe com precos:
df_prices = stocks_brazil()
# df_prices = multiclass()





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
df_return = df_prices.pct_change()


initial_date = rebal_index[0]
initial_value = 0 # valor financeiro
initial_notional = 100000
new_value = 0
dict_qt = {}
dict_notional = {}
list_signal = []
dict_nav = {}
dict_signal = {}

first_date_already_happened = False
date_index = df_prices.index.min()
list_total_dates = list(df_prices.index)

date_index = pd.to_datetime("2015-01-02")
window = 60

while date_index <= df_prices.index.max():

    df_temp = df_prices[df_prices.index <= date_index]  # df temporario com precos para usarmos para computar os sinais
    df_temp = df_temp.iloc[-window:]
    df_temp = df_temp.dropna(axis =1)
    # df_signal = get_momentum_signal(df=df_temp, window=window, percentile = 0.1)  # computando sinal
    df_signal = get_buy_and_hold_signal(df=df_temp)  # computando sinal
    # df_weights = get_weights_one_over_n(df_signal.tail(1)).tail(1)
    df_weights = get_weights_hrp(df_prices = df_temp, df_signal=df_signal, window=window)


    # computando backtest quando nao eh data de rebalanceamento
    if first_date_already_happened == True and date_index not in rebal_index:
        print(f"aplicando retornos em {date_index}")
        current_index = list_total_dates.index(date_index)
        previous_date = list_total_dates[current_index - 1]
        # acessando o notional do dia anterior
        df_notional_t1 = dict_notional[previous_date]
        df_notional = df_notional_t1.reset_index(drop=True) * (1 + df_temp.pct_change().tail(1).reset_index(drop=True))
        df_notional["Date"] = date_index
        df_notional.set_index(["Date"], inplace = True)
        dict_notional[date_index] = df_notional
        # acessando a quantidade do dia anterior e replicando ate ter rebalanceamento
        df_qt_t1 = dict_qt[previous_date].reset_index(drop = True)
        df_qt_t1["Date"] = date_index
        df_qt_t1.set_index(["Date"], inplace=True)
        dict_qt[date_index] = df_qt_t1

    if first_date_already_happened == True and date_index in rebal_index:
        print(f"rebalanceando em {date_index}")
        current_index = list_total_dates.index(date_index)
        previous_date = list_total_dates[current_index - 1]
        # acessando a notional do dia anterior
        df_notional_t1 = dict_notional[previous_date]
        df_notional = df_notional_t1.reset_index(drop=True) * (1 + df_temp.pct_change().tail(1).reset_index(drop=True))
        df_notional["Date"] = date_index
        df_notional.set_index(["Date"], inplace = True)
        # dict_notional[date_index] = df_notional
        # last_total_aum = dict_nav[previous_date]
        current_total_aum = df_notional.sum(axis=1).iloc[0]
        # rebalanceando
        # acessando a quantidade do dia anterior e replicando ate ter rebalanceamento
        df_qt_t1 = dict_qt[previous_date].reset_index(drop=True)
        df_qt_t1["Date"] = date_index
        df_qt_t1.set_index(["Date"], inplace=True)
        df_qt_trade = rebalance(current_total_aum=current_total_aum, df_new_weights=df_weights,
                                df_prices_d0=df_temp.tail(1), df_current_qt = df_qt_t1)
        dict_qt[date_index] = df_qt_t1 + df_qt_trade
        dict_notional[date_index] = (df_qt_t1 + df_qt_trade) * df_temp.tail(1)
        print(f"qt trade: {df_qt_trade.sum(axis=1)}")


    # checando se ha pesos computados, para iniciarmos o backtest
    if df_weights.T.isnull().all().iloc[0] == False and first_date_already_happened == False and df_weights.sum(axis=1).iloc[0] != 0:
        df_notional = df_weights * initial_notional
        df_qt = df_notional / df_temp.tail(1)
        first_date_already_happened = True
        print(f"iniciou em {date_index}")
        dict_qt[date_index] = df_qt
        dict_notional[date_index] = df_notional

    if first_date_already_happened == True:
        # initial_value += df_notional.sum(axis=1).iloc[0]
        dict_nav[date_index] = df_notional.sum(axis=1).iloc[0]

    # identifcando proxima data
    current_index = list_total_dates.index(date_index)
    try:
        next_date = list_total_dates[current_index+1]
    except:
        next_date = date_index + datetime.timedelta(days=1) # forcando soma de 1 dia
    date_index = next_date

    dict_signal[date_index] = df_signal.tail(1)
    print(date_index)


df_notional = pd.concat(dict_notional.values())
df_qt = pd.concat(dict_qt.values())
df_signal = pd.concat(dict_signal.values())
df_nav = pd.DataFrame(dict_nav.items())



df_notional["total_pos"] = df_notional[df_notional > 0].sum(axis=1)
df_notional["total_neg"] = df_notional[df_notional < 0].sum(axis=1)

'''df_weights_adjusted = df_notional.copy()
df_weights_adjusted = df_weights_adjusted[df_weights_adjusted["total_pos"]!=0]

# Funcao para chegar no peso em %
for column in df_weights_adjusted.columns:
    if df_notional["total_pos"].sum() != 0:
        mask_pos = df_weights_adjusted[column] > 0
        df_weights_adjusted.loc[mask_pos, column] = df_weights_adjusted[column]/df_weights_adjusted["total_pos"]
    if df_notional["total_neg"].sum() != 0:
        mask_neg = df_weights_adjusted[column] < 0
        df_weights_adjusted.loc[mask_neg, column] = df_weights_adjusted[column] / df_weights_adjusted["total_neg"]

df_weights_adjusted.drop(["total_pos", "total_neg"], axis=1, inplace = True)
df_notional.drop(["total_pos", "total_neg"], axis=1, inplace = True)'''

# df_signal = df_notional.abs()/df_notional

# df_weights_adjusted = df_weights_adjusted * df_signal

# df_return = df_maybe_correct_cum_ret = (df_weights_adjusted * ((1 + df_return[df_return.index >= df_weights_adjusted.index.min()]).cumprod() - 1))
# df_return["cumulative_total_return"] = df_return.sum(axis = 1)

print("a")


with pd.ExcelWriter(f"analise_estrategia_{freq}_hrp.xlsx") as writer:
    # use to_excel function and specify the sheet_name and index
    # to store the dataframe in specified sheet
    df_return.to_excel(writer, sheet_name="portfolio_returns", index=True)
    df_weights_adjusted.to_excel(writer, sheet_name="portfolio_weigths", index=True)






