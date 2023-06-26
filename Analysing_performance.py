from Performance.performance import *

df_ibov = pd.read_pickle("ibov.pkl")
df_cdi = pd.read_pickle("cdi.pkl")

cdi_returns = (1 + df_cdi/100)**(1/252) - 1
cdi_returns.columns = ['cdi_return']
ibov = df_ibov.pct_change()

df_resultado_hrp = pd.read_excel("etfs_hrp.xlsx")
df_resultado_hrp = df_resultado_hrp[[0,1]]
df_resultado_hrp.rename(columns={0:"Date", 1:"total_aum"}, inplace = True)
df_resultado_hrp["Date"] = pd.to_datetime(df_resultado_hrp["Date"])
df_resultado_hrp.set_index(["Date"], inplace = True)

df_resultado_equal = pd.read_excel("etfs.xlsx")
df_resultado_equal = df_resultado_equal[[0,1]]
df_resultado_equal.rename(columns={0:"Date", 1:"total_aum"}, inplace = True)
df_resultado_equal["Date"] = pd.to_datetime(df_resultado_equal["Date"])
df_resultado_equal.set_index(["Date"], inplace = True)

resumo_hrp = summary_perfomance(df_resultado_hrp[['total_aum']], cdi_returns)
resumo_equal = summary_perfomance(df_resultado_equal[['total_aum']], cdi_returns)

underwater_plot(pd.DataFrame(np.cumprod(1 + df_resultado_hrp["total_aum"].pct_change().dropna()) * 100))

underwater_plot(pd.DataFrame(np.cumprod(1 + df_resultado_equal["total_aum"].pct_change().dropna()) * 100))



print('a')