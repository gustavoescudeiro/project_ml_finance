def get_buy_and_hold_signal(df = None, window = 60, percentile = 0.25):

    df_prices = df.copy()
    df_bh = df_prices.tail(1)

    # Criando df vazio e populando com sinais
    for column in df_bh.columns:
        df_bh[column] = 1


    return df_bh