import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

##########################################################################################################################################################################################################################

#Simple Moving Average

def SMA(df, period=15):
    
    """Intakes a price dataframe and returns SMA column
    SMA is the simple moving average that describes the direction of the trend, and computed using the
    mean over the certain period"""
    
    df["{} SMA".format(period)] = df["Close"].rolling(window=period).mean()
    
    return df

##########################################################################################################################################################################################################################

#Exponential Moving Average

def EMA(df, period=20, smoothing=2):
    
    """Intakes a price dataframe and returns EMA column
    EMA is the exponential moving average that describes the direction of the trend, and is requires previous EMA and the latest
    Close price to compute; the first EMA will be same as SMA"""
    
    multiplier = smoothing/(1+period)
    df["{} EMA".format(period)] = np.nan
    
    df["{} EMA".format(period)].iloc[period-1] = df["Close"].iloc[0:period].mean()
    for i in range(period, len(df)):
        df["{} EMA".format(period)].iloc[i] = (df["Close"].iloc[i]*multiplier
                                               + df["{} EMA".format(period)].iloc[i-1]*(1-multiplier))
    
    return df

##########################################################################################################################################################################################################################

#MACD

def MACD(df, small_ema=12, large_ema=26, signal_line=9, smoothing=2):
    
    """"""
    
    if large_ema<=small_ema:
        raise ValueError("large_ema has to be larger than small_ema")
    
    macd_df = pd.DataFrame(index=df.index, columns=["{} EMA".format(small_ema), "{} EMA".format(large_ema), "MACD",
                                                    "MACD Signal Line", "MACD Histogram"])
    
    small_ema_mult = smoothing/(1+small_ema)
    large_ema_mult = smoothing/(1+large_ema)
    signal_line_mult = smoothing/(1+signal_line)
    
    macd_df.iloc[small_ema-1, 0] = df["Close"].iloc[0:small_ema].mean()
    for i in range(small_ema, len(df)):
        macd_df.iloc[i, 0] = (df["Close"].iloc[i]*small_ema_mult
                              + macd_df["{} EMA".format(small_ema)].iloc[i-1]*(1-small_ema_mult))
    
    macd_df.iloc[large_ema-1, 1] = df["Close"].iloc[:large_ema].mean()
    for i in range(large_ema, len(df)):
        macd_df.iloc[i, 1] = (df["Close"].iloc[i]*large_ema_mult
                              + macd_df["{} EMA".format(large_ema)].iloc[i-1]*(1-large_ema_mult))
    
    macd_df["MACD"] = macd_df["{} EMA".format(small_ema)] - macd_df["{} EMA".format(large_ema)]
    
    macd_df.iloc[large_ema-2+signal_line, 3] = macd_df["MACD"].iloc[large_ema-1:large_ema-1+signal_line].mean()
    for i in range(large_ema-1+signal_line, len(macd_df)):
        macd_df.iloc[i, 3] = (macd_df["MACD"].iloc[i]*signal_line_mult
                              + macd_df["MACD Signal Line"].iloc[i-1]*(1-signal_line_mult))
    
    macd_df["MACD Histogram"] = macd_df["MACD"] - macd_df["MACD Signal Line"]
    
    df["MACD"] = macd_df["MACD"]
    df["MACD Signal Line"] = macd_df["MACD Signal Line"]
    df["MACD Histogram"] = macd_df["MACD Histogram"]
    
    return df

##########################################################################################################################################################################################################################

#Bollinger Bands

def Bollinger_Bands(df, period=50, n_deviations=2):
    
    """Intakes a price dataframe and returns SMA, Upper Band and Lower Band columns
    Bollinger Band is an indicator that creates SMA and keeps price action bounded by upper and lower bands that
    sit n_deviations away from the SMA line"""
    
    df["SMA"] = df["Close"].rolling(window=period).mean()
    df["Upper Band"] = df["SMA"] + (df["Close"].rolling(window=period).std()*n_deviations)
    df["Lower Band"] = df["SMA"] - (df["Close"].rolling(window=period).std()*n_deviations)
    
    return df

##########################################################################################################################################################################################################################

#RSI

def RSI(df, period=14):
    
    """Intakes a price dataframe and returns RSI column
    RSI is a momentum indicator that measures the magnitude of recent price changes to evaluate overbought or oversold
    conditions"""
    
    rsi_df = pd.DataFrame(index=df.index, columns=["U", "D", "U SMMA", "D SMMA", "RS", "RSI"])
    
    for i in range(1, len(df)):
        if df["Close"].iloc[i]>=df["Close"].iloc[i-1]:
            #U
            rsi_df.iloc[i, 0] = df["Close"].iloc[i] - df["Close"].iloc[i-1]
            #D
            rsi_df.iloc[i, 1] = 0
        else:
            #U
            rsi_df.iloc[i, 0] = 0
            #D
            rsi_df.iloc[i, 1] = df["Close"].iloc[i-1] - df["Close"].iloc[i]
    
    #U SMMA
    rsi_df.iloc[period, 2] = rsi_df["U"].iloc[1:period+1].mean()
    #D SMMA
    rsi_df.iloc[period, 3] = rsi_df["D"].iloc[1:period+1].mean()
    for i in range(period+1, len(df)):
        #U SMMA
        rsi_df.iloc[i, 2] = (rsi_df["U SMMA"].iloc[i-1]*(period-1) + rsi_df["U"].iloc[i])/period
        #D SMMA
        rsi_df.iloc[i, 3] = (rsi_df["D SMMA"].iloc[i-1]*(period-1) + rsi_df["D"].iloc[i])/period
    
    rsi_df["RS"] = rsi_df["U SMMA"]/rsi_df["D SMMA"]
    rsi_df["RSI"] = 100 - 100/(1+rsi_df["RS"])
    
    df["RSI"] = rsi_df["RSI"]
    
    return df

##########################################################################################################################################################################################################################

#ADX

def ADX(df, period=14):
    
    """Intakes a price dataframe and returns +DI, -DI and ADX columns
    ADX is an indicator that describes the relative strength of the trend"""
    
    adx_df = pd.DataFrame(index=df.index, columns=["+DM", "-DM", "TR", "ATR", "+DM SMMA", "-DM SMMA", "+DI", "-DI",
                                                   "Abs(+DI--DI)", "ADX"])
    
    for i in range(1, len(df)):
        up_move = df["High"].iloc[i] - df["High"].iloc[i-1]
        down_move = df["Low"].iloc[i-1] - df["Low"].iloc[i]
        if (up_move > down_move) and (up_move > 0):
            adx_df["+DM"].iloc[i] = up_move
        else:
            adx_df["+DM"].iloc[i] = 0
        if (down_move > up_move) and (down_move > 0):
            adx_df["-DM"].iloc[i] = down_move
        else:
            adx_df["-DM"].iloc[i] = 0
    
    for i in range(1, len(df)):
        adx_df["TR"].iloc[i] = (max(df["High"].iloc[i], df["Close"].iloc[i-1])
                                  - min(df["Low"].iloc[i], df["Close"].iloc[i-1]))
    
    adx_df["ATR"].iloc[period-1] = adx_df["TR"].iloc[0:period].mean()
    for i in range(period, len(adx_df)):
        adx_df["ATR"].iloc[i] = (adx_df["ATR"].iloc[i-1]*(period-1) + adx_df["TR"].iloc[i])/period
    
    adx_df["+DM SMMA"].iloc[period] = adx_df["+DM"].iloc[1:period+1].mean()
    adx_df["-DM SMMA"].iloc[period] = adx_df["-DM"].iloc[1:period+1].mean()
    for i in range(period+1, len(df)):
        adx_df["+DM SMMA"].iloc[i] = (adx_df["+DM SMMA"].iloc[i-1]*(period-1) + adx_df["+DM"].iloc[i])/period
        adx_df["-DM SMMA"].iloc[i] = (adx_df["-DM SMMA"].iloc[i-1]*(period-1) + adx_df["-DM"].iloc[i])/period
    adx_df["+DI"] = adx_df["+DM SMMA"]*(100/adx_df["ATR"])
    adx_df["-DI"] = adx_df["-DM SMMA"]*(100/adx_df["ATR"])
    
    adx_df["Abs(+DI--DI)"] = abs(adx_df["+DI"]-adx_df["-DI"])
    adx_df["ADX"].iloc[2*period] = adx_df["Abs(+DI--DI)"].iloc[period:2*period+1].mean()
    for i in range(2*period+1, len(adx_df)):
        adx_df["ADX"].iloc[i] = (adx_df["ADX"].iloc[i-1]*(period-1) + adx_df["Abs(+DI--DI)"].iloc[i])/period
    adx_df["ADX"] = adx_df["ADX"]*(100/(adx_df["+DI"]+adx_df["-DI"]))
    
    df["+DI"] = adx_df["+DI"]
    df["-DI"] = adx_df["-DI"]
    df["ADX"] = adx_df["ADX"]
    
    return df




if __name__ == '__main__':

    #For VSCode
    price_df = pd.read_csv(r"Trading_Strategies\Algotrading\AAPL_data.csv", index_col="Date")
    #For Jupyter Notebook
    #price_df = pd.read_csv("AAPL_data.csv", index_col="Date")
    price_df.index.name = None



    #Plotting Japanese Candlestick Chart

    fig = go.Figure(data=go.Candlestick(x = price_df.index, open = price_df["Open"], high = price_df["High"], low = price_df["Low"], close = price_df["Close"], name="Candlestick"))
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_layout(title="Candlestick Chart", yaxis_title="Stock Price", xaxis_title="Date")

    fig.show()
    
    
    #Plotting RSI

    price_df = RSI(price_df)
    oversold = 30
    overbought = 70

    fig = go.Figure(go.Scatter(x = price_df.index, y = overbought*np.ones(len(price_df)), line_color = "green", name = "Overbought Condition"), layout = {"height":303})
    fig.add_trace(go.Scatter(x = price_df.index, y = oversold*np.ones(len(price_df)), line_color = "red", name = "Oversold Condition"))
    fig.add_trace(go.Scatter(x = price_df.index, y = price_df["RSI"], line_color = "blue", name = "RSI"))

    fig.update_layout(title="RSI", yaxis_title="RSI Value", xaxis_title="Date")

    fig.show()


    #Plotting Candlestick Chart and MACD

    price_df = EMA(price_df)
    price_df = MACD(price_df)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, shared_yaxes=False, row_heights=[0.8, 0.2], subplot_titles=["Candlestick Chart", "MACD"])

    fig.add_trace(go.Candlestick(x = price_df.index, open = price_df["Open"], high = price_df["High"], low = price_df["Low"], close = price_df["Close"], name="Candlestick"), row=1, col=1)
    fig.add_trace(go.Scatter(x = price_df.index, y = price_df["20 EMA"], line_color = "blue", name = "20 EMA"), row=1, col=1)
    fig.update_layout(xaxis_rangeslider_visible=False)

    fig.add_trace(go.Scatter(x = price_df.index, y = price_df["MACD"], line_color = "blue", name = "MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x = price_df.index, y = price_df["MACD Signal Line"], line_color = "red", name = "MACD Signal Line"), row=2, col=1)
    fig.add_trace(go.Bar(x = price_df.index, y = price_df["MACD Histogram"], name = "MACD Histogram"), row=2, col=1)

    fig.show()