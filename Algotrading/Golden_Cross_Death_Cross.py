from os import close
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

price_df = pd.read_csv(r"C:\Users\Rem\Documents\Documents\GitHub Resources\Trading_Strategies\AAPL_data.csv", index_col="Date")
price_df.index.name = None

def plot_golden_cross_death_cross(df):
    
    large_sma = 200
    small_sma = 50
    
    df["200 SMA"] = df["Close"].rolling(window=large_sma).mean()
    df["50 SMA"] = df["Close"].rolling(window=small_sma).mean()
    
    fig = go.Figure(data=go.Candlestick(x = df.index, open = df["Open"], high = df["High"], low = df["Low"],
                                        close = df["Close"], name="Candlestick"))
    fig.add_trace(go.Scatter(x = df.index, y = df["200 SMA"], line_color = "blue", name = "200 SMA"))
    fig.add_trace(go.Scatter(x = df.index, y = df["50 SMA"], line_color = "orange", name = "50 SMA"))
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig.show()


def golden_cross_death_cross(df):
    
    large_sma = 200
    small_sma = 50
    trading_signals = np.array([None])
    
    df["200 SMA"] = df["Close"].rolling(window=large_sma).mean()
    df["50 SMA"] = df["Close"].rolling(window=small_sma).mean()
    
    for i in range(1, len(df)):
        #Golden Cross
        if (df["200 SMA"].iloc[i-1]>df["50 SMA"].iloc[i-1]) and (df["200 SMA"].iloc[i]<df["50 SMA"].iloc[i]):
            trading_signals = np.append(trading_signals, "Buy")
        #Death Cross
        elif (df["200 SMA"].iloc[i-1]<df["50 SMA"].iloc[i-1]) and (df["200 SMA"].iloc[i]>df["50 SMA"].iloc[i]):
            trading_signals = np.append(trading_signals, "Sell")
        else:
            trading_signals = np.append(trading_signals, None)
    
    return trading_signals


if __name__ == '__main__':

    from Strategy_Engine import strategy_engine

    #plot_golden_cross_death_cross(price_df)
    
    strat = golden_cross_death_cross(price_df)
    history = strategy_engine(price_df, strat, 100000, 0.1, 0.1, close_positions=True)
    print(history)
    fig = px.line(np.cumsum(history["Profit/Loss"]))
    fig.show()
