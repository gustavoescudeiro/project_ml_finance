from Data.reading_data import stocks_brazil
from Signal.momentum import get_momentum_signal
from Allocator.one_over_n import get_weights_one_over_n

# Definindo dataframe com precos:
df_prices = stocks_brazil()

# Calculando sinal de momentum a partir do dataframe com precos
df_signal = get_momentum_signal(df = df_prices, window = 180, percentile = 0.25)

# Calculando pesos a partir dos sinais (1/n)
df_weights = get_weights_one_over_n(df_signal)

# Check de sanidade
df_check = df_weights.sum(axis = 1)

# Backtest simplificado
df_return = df_weights.shift(1) * df_prices.pct_change() # retorno de t0 * peso de t-1
df_return["total_return"] = df_return.sum(axis = 1)
df_return["cumulative_return"] = (1 + df_return["total_return"]).cumprod() - 1


