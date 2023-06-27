from Performance.performance import *

df_ibov = pd.read_pickle("ibov.pkl")
df_cdi = pd.read_pickle("cdi.pkl")

cdi_returns = (1 + df_cdi/100)**(1/252) - 1
cdi_returns.columns = ['cdi_return']
ibov = df_ibov.pct_change()

df_resultado_hrp = pd.read_pickle("long_only_hrp.pkl")
#df_resultado_hrp = df_resultado_hrp[[0,1]]
df_resultado_hrp["total_aum"] = df_resultado_hrp.sum(axis=1)
# df_resultado_hrp.rename(columns={0:"Date", 1:"total_aum"}, inplace = True)
# df_resultado_hrp["Date"] = pd.to_datetime(df_resultado_hrp["Date"])
# df_resultado_hrp.set_index(["Date"], inplace = True)

df_resultado_equal = pd.read_pickle("long_only_equal_weighted.pkl")
# df_resultado_equal = df_resultado_equal[[0,1]]
df_resultado_equal["total_aum"] = df_resultado_equal.sum(axis=1)
# df_resultado_equal.rename(columns={0:"Date", 1:"total_aum"}, inplace = True)
#df_resultado_equal["Date"] = pd.to_datetime(df_resultado_equal["Date"])
# df_resultado_equal.set_index(["Date"], inplace = True)

df_resultado_herc = pd.read_pickle("long_only_herc.pkl")
# df_resultado_equal = df_resultado_equal[[0,1]]
df_resultado_herc["total_aum"] = df_resultado_herc.sum(axis=1)
# df_resultado_equal.rename(columns={0:"Date", 1:"total_aum"}, inplace = True)
#df_resultado_equal["Date"] = pd.to_datetime(df_resultado_equal["Date"])
# df_resultado_equal.set_index(["Date"], inplace = True)

resumo_hrp = summary_perfomance(df_resultado_hrp[['total_aum']], cdi_returns)
resumo_equal = summary_perfomance(df_resultado_equal[['total_aum']], cdi_returns)
resumo_herc = summary_perfomance(df_resultado_herc[['total_aum']], cdi_returns)


print("A")




