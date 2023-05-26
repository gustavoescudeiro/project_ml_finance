import pandas as pd
import numpy as np

def get_weights_one_over_n(df = None):

    df_signal = df.copy()
    df_weights = df_signal.copy()
    positive_count = df_weights[df_weights > 0].count(axis=1)
    negative_count = df_weights[df_weights < 0].count(axis=1)

    df_weights = pd.DataFrame(columns=df_signal.columns, index=df_signal.index)
    for column in df_signal.columns:
        mask_positive = df_signal[column] == 1
        df_weights.loc[mask_positive, column] = 1 / positive_count
        mask_negative = df_signal[column] == -1
        df_weights.loc[mask_negative, column] = -1 / negative_count

    return df_weights