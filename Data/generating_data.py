from get_data import *


lista_etfs_b3 = [
        "AGRI11",
        "IMAB11",
        "GOLD11",
        "NASD11",
        "IVVB11",
        "XFIX11",
        "URET11",
        "IFRA11",

]



lista_etfs_b3 = [
        "IMAB11",
        "GOLD11",
        "IVVB11",
        "BOVA11"]


# baixando preços
df_only = get_equity_data(lista_etfs_b3, start_date = '2021-01-01', feature=["adjclose"])
df_only = df_only['adjclose']
df_only.to_pickle("etfs.pkl")

# baixando cdi
# df_cdi = get_sgs_data([4389])
# df_cdi.to_pickle('./cdi.pkl')

# baixando ibov
# df_ibov = get_equity_data(['^BVSP'], start_date = '2015-01-01')
# df_ibov = df_ibov['adjclose']
# df_ibov.to_pickle("./ibov.pkl")