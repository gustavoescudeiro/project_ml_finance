import pandas as pd
import numpy as np
from datetime import datetime
import empyrical as ep
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import skew
from scipy.stats import kurtosis
import plotly.figure_factory as ff


def customLegend(fig, nameSwap):
    for i, dat in enumerate(fig.data):
        for elem in dat:
            if elem == 'name':
                fig.data[i].name = nameSwap[fig.data[i].name]
    return (fig)


# Underwater plot
def underwater_plot(cum_rets):
    df_cum_rets = cum_rets
    df_cum_rets.columns = ['return']
    running_max = np.maximum.accumulate(df_cum_rets)
    underwater = -100 * ((running_max - df_cum_rets) / running_max)
    fig = px.area(underwater, x=underwater.index, y=underwater.columns, title='Underwater Plot')

    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    fig['data'][0]['line']['color'] = "orange"

    fig = customLegend(fig=fig, nameSwap={'return': 'Drawmdown'})

    fig.update_layout(
        # title="Plot Title",
        xaxis_title="date",
        yaxis_title="%",
        legend_title="")

    fig.show()


def rolling_sharpe_ratio(cum_rets, risk_free, window=126, period='daily', annualization=None):
    returns = cum_rets.pct_change()
    df = returns.merge(risk_free, left_on=returns.index, right_on=risk_free.index, how='left')
    df.set_index(['key_0'], inplace=True)
    df = df.dropna()
    df['rolling_sharpe_ratio'] = df.rolling(window).apply(lambda x: ep.sharpe_ratio(x.iloc[0:, 0:1].values,
                                                                                    risk_free=x.iloc[0:, 1:2].values,
                                                                                    period=period,
                                                                                    annualization=annualization)[0]())
    df['mean'] = df['rolling_sharpe_ratio'].mean()

    return (df[['rolling_sharpe_ratio', 'mean']].dropna())


def cum_returns(returns):
    df_returns = (1 + returns).cumprod() - 1
    last_return = df_returns.iloc[len(df_returns.index) - 1]
    return (last_return[df_returns.columns[0]])


def func_sharpe_ratio(returns, risk_free=0, annualization=None, period='daily'):
    df = returns.merge(risk_free, left_on=returns.index, right_on=risk_free.index, how='left')
    df.set_index(['key_0'], inplace=True)
    df = df.dropna()

    s_r = ep.sharpe_ratio(df.iloc[0:, 0:1].values, risk_free=df.iloc[0:, 1:2].values, period=period,
                          annualization=annualization)[0]

    return (s_r)


def annual_returns(returns):
    df_returns = (1 + returns).cumprod() - 1
    last_return = df_returns.iloc[len(df_returns.index) - 1]
    annual_return = (1 + last_return) ** (252 / len(df_returns.index))
    return (annual_return[0] - 1)


def annual_vol(returns):
    vol = returns.dropna().std() * 252 ** (0.5)

    return (vol[0])


def kurtosis_func(returns):
    return (kurtosis(returns.dropna())[0])


def skew_func(returns):
    return (skew(returns.dropna())[0])


def tail_ratio_func(returns):
    return (ep.tail_ratio(returns))


def summary_perfomance(returns, risk_free, frequency = None):


    dic_cum_returns = {}
    dic_sharpe_ratio = {}
    dic_annual_returns = {}
    dic_annual_vol = {}
    dic_kurtosis = {}
    dic_skew = {}
    dic_tail_ratio = {}
    if frequency is not None:
        first_day_year = returns.loc[returns.groupby(returns.index.to_period(frequency)).apply(lambda x: x.index.min())].index


        for i in first_day_year:
            df_filtrado = returns.pct_change().copy()
            df_filtrado = df_filtrado[df_filtrado.index >= i]
            dic_cum_returns[i] = cum_returns(df_filtrado)
            dic_annual_returns[i] = annual_returns(df_filtrado)
            dic_annual_vol[i] = annual_vol(df_filtrado)
            dic_sharpe_ratio[i] = func_sharpe_ratio(df_filtrado, risk_free)
            dic_kurtosis[i] = kurtosis_func(df_filtrado)
            dic_skew[i] = skew_func(df_filtrado)
            dic_tail_ratio[i] = tail_ratio_func(df_filtrado)
    else:
        first_day_year = returns.groupby(returns.index.to_period("Y")).apply(lambda x: x.index.min()).max()
        df_filtrado = returns.pct_change().copy()
        dic_cum_returns[first_day_year] = cum_returns(df_filtrado)
        dic_annual_returns[first_day_year] = annual_returns(df_filtrado)
        dic_annual_vol[first_day_year] = annual_vol(df_filtrado)
        dic_sharpe_ratio[first_day_year] = func_sharpe_ratio(df_filtrado, risk_free)
        dic_kurtosis[first_day_year] = kurtosis_func(df_filtrado)
        dic_skew[first_day_year] = skew_func(df_filtrado)
        dic_tail_ratio[first_day_year] = tail_ratio_func(df_filtrado)


    df_cum_returns = pd.DataFrame(list(dic_cum_returns.items()), columns=['date', 'value'])
    df_cum_returns['statistic'] = 'Cummulative return'
    # df_cum_returns['value'] = df_cum_returns['value'].apply(lambda x: round(x, 2))
    df_cum_returns['value'] = df_cum_returns['value'] * 100
    df_cum_returns['value'] = df_cum_returns['value'].apply(lambda x: "{0:.2f}%".format(x))

    df_annual_returns = pd.DataFrame(list(dic_annual_returns.items()), columns=['date', 'value'])
    df_annual_returns['statistic'] = 'Annual return'
    # df_annual_returns['value'] = df_annual_returns['value'].apply(lambda x: round(x, 2))
    df_annual_returns['value'] = df_annual_returns['value'] * 100
    df_annual_returns['value'] = df_annual_returns['value'].apply(lambda x: "{0:.2f}%".format(x))

    df_annual_vol = pd.DataFrame(list(dic_annual_vol.items()), columns=['date', 'value'])
    df_annual_vol['statistic'] = 'Annual Volatility'
    # df_annual_vol['value'] = df_annual_vol['value'].apply(lambda x: round(x, 2))
    df_annual_vol['value'] = df_annual_vol['value'] * 100
    df_annual_vol['value'] = df_annual_vol['value'].apply(lambda x: "{0:.2f}%".format(x))

    df_sharpe_ratio = pd.DataFrame(list(dic_sharpe_ratio.items()), columns=['date', 'value'])
    df_sharpe_ratio['statistic'] = 'Annual Sharpe Ratio'
    df_sharpe_ratio['value'] = df_sharpe_ratio['value'].apply(lambda x: round(x, 2))

    df_kurtosis = pd.DataFrame(list(dic_kurtosis.items()), columns=['date', 'value'])
    df_kurtosis['statistic'] = 'Kurtosis'
    df_kurtosis['value'] = df_kurtosis['value'].apply(lambda x: round(x, 2))

    df_skew = pd.DataFrame(list(dic_skew.items()), columns=['date', 'value'])
    df_skew['statistic'] = 'Skewness'
    df_skew['value'] = df_skew['value'].apply(lambda x: round(x, 2))

    df_tail_ratio = pd.DataFrame(list(dic_tail_ratio.items()), columns=['date', 'value'])
    df_tail_ratio['statistic'] = 'Tail ratio'
    df_tail_ratio['value'] = df_tail_ratio['value'].apply(lambda x: round(x, 2))

    df_stats = pd.concat([df_cum_returns,
                          df_annual_returns,
                          df_annual_vol,
                          df_sharpe_ratio,
                          df_kurtosis,
                          df_skew,
                          df_tail_ratio], axis=0)
    summary = df_stats.pivot(index='statistic', columns='date', values=['value'])
    summary.columns.rename('values', level=0)
    summary.columns = summary.columns.to_flat_index()

    summary.columns = [str(date)[21:28] for date in summary.columns.to_list()]

    return (summary)


def rolling_sharpe_plot(returns):
    fig = px.line(returns, x=returns.index, y=returns.columns, title='Rolling Sharpe Ratio 6M')

    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    fig['data'][1]['line']['color'] = "red"
    fig['data'][1]['line']['dash'] = "dash"
    # fig.add_trace(go.Scatter(x=df_r_s.index, y=df_r_s['mean'], name='mean',
    # line=dict(color='firebrick', width=4,
    # dash='dash')))

    # fig.add_trace(go.Scatter(x=df_r_s.index, y=df_r_s['rolling_sharpe_ratio'], name='rolling_sharpe_ratio',
    # line=dict(color='purple', width=4)))

    fig.update_layout(
        # title="Plot Title",
        xaxis_title="date",
        yaxis_title="Sharpe Ratio",
        legend_title="")

    fig.show()


def cum_returns_plot(returns, list_benchmarks):
    returns = returns.reset_index(drop=False)
    for i in list_benchmarks:
        i = i.reset_index(drop=False)

    for i in list_benchmarks:
        returns = returns.merge(i, left_on=['date'], right_on=['date'], how='left')

    returns.set_index(['date'], inplace=True)
    returns = (1 + returns).cumprod() - 1

    returns = returns * 100

    fig = px.line(returns, x=returns.index, y=returns.columns, title='Cummulative returns')

    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    # fig['data'][1]['line']['color']="red"
    # fig['data'][1]['line']['dash']="dash"
    # fig.add_trace(go.Scatter(x=df_r_s.index, y=df_r_s['mean'], name='mean',
    # line=dict(color='firebrick', width=4,
    # dash='dash')))

    # fig.add_trace(go.Scatter(x=df_r_s.index, y=df_r_s['rolling_sharpe_ratio'], name='rolling_sharpe_ratio',
    # line=dict(color='purple', width=4)))

    fig.update_layout(
        # title="Plot Title",
        xaxis_title="date",
        yaxis_title="%",
        legend_title="")

    fig.show()


def rolling_vol(returns, window=126):
    df_rolling_vol = returns.rolling(window=window).std() * 252 ** (0.5)
    df_rolling_vol.columns = ['volatility']
    df_rolling_vol = df_rolling_vol * 100

    fig = px.line(df_rolling_vol, x=df_rolling_vol.index, y=df_rolling_vol.columns,
                  title="Rolling Volatility - {window} day window".format(window=window))

    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    # fig['data'][1]['line']['color']="red"
    # fig['data'][1]['line']['dash']="dash"
    # fig.add_trace(go.Scatter(x=df_r_s.index, y=df_r_s['mean'], name='mean',
    # line=dict(color='firebrick', width=4,
    # dash='dash')))

    # fig.add_trace(go.Scatter(x=df_r_s.index, y=df_r_s['rolling_sharpe_ratio'], name='rolling_sharpe_ratio',
    # line=dict(color='purple', width=4)))

    fig.update_layout(
        # title="Plot Title",
        xaxis_title="date",
        yaxis_title="%",
        legend_title="")

    fig.show()


def weights_heatmap(df_weights = None, year = None):

    df_weights = df_weights[df_weights.index.year == year]
    index_to_reorder = pd.DataFrame(df_weights.mean()).sort_values(0, ascending = False).dropna().index
    wgt_grouped = df_weights.groupby(by=[df_weights.index.month]).mean()
    wgt_grouped = wgt_grouped.T
    wgt_grouped.dropna(axis = 0, how = 'all', inplace = True)
    wgt_grouped = wgt_grouped.reindex(index_to_reorder)
    wgt_grouped.fillna(0, inplace = True)
    wgt_grouped = wgt_grouped * 100
    wgt_grouped = wgt_grouped = np.round(wgt_grouped, decimals=2)


    fig = ff.create_annotated_heatmap(wgt_grouped.values, x=wgt_grouped.columns.to_list(), y=wgt_grouped.index.to_list(), colorscale='Viridis_r')
    #fig = ff.create_annotated_heatmap(wgt_grouped.values)
    fig['layout']['yaxis']['autorange'] = "reversed"

    fig.update_layout(
        showlegend = False,
        width = 1000, height = 1100,
        autosize = False,
        title=f"Monthly mean weights (%) - {year}")

    fig['layout']['xaxis']['side'] = 'bottom'
    fig['layout']['xaxis']['title'] = 'Month'
    fig['layout']['yaxis']['title'] = 'Ticker'

    fig.show()
