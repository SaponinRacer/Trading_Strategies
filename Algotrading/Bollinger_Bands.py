import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

price_df = pd.read_csv(r"Trading_Strategies\Algotrading\AAPL_data.csv", index_col="Date")
price_df.index.name = None

def plot_bollinger_bands(df, sma, n_deviations):

    df["SMA"] = df["Close"].rolling(window=sma).mean()
    df["Upper Band"] = df["SMA"] + (df["Close"].rolling(window=sma).std()*n_deviations)
    df["Lower Band"] = df["SMA"] - (df["Close"].rolling(window=sma).std()*n_deviations)

    fig = go.Figure(data=go.Candlestick(x = df.index, open = df["Open"], high = df["High"], low = df["Low"], close = df["Close"], name="Candlestick"))
    fig.add_trace(go.Scatter(x = df.index, y = df["SMA"], line_color = "blue", name = "SMA"))
    fig.add_trace(go.Scatter(x = df.index, y = df["Upper Band"], line_color = "red", line = {"dash": "dash"}, name = "Upper Band", opacity = 0.5))
    fig.add_trace(go.Scatter(x = df.index, y = df["Lower Band"], line_color = "green", line = {"dash": "dash"}, name = "Lower Band", opacity = 0.5))
    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig.show()


def boll_buy_lower_sell_upper(df, sma_number=50, n_deviations=2):
    
    trading_signals = np.array([])
    df["SMA"] = df["Close"].rolling(window=sma_number).mean()
    df["Upper Band"] = df["SMA"] + (df["Close"].rolling(window=sma_number).std()*n_deviations)
    df["Lower Band"] = df["SMA"] - (df["Close"].rolling(window=sma_number).std()*n_deviations)
    
    for i in range(0, len(df)):
        if df["Close"].iloc[i]<=df["Lower Band"].iloc[i]:
            trading_signals = np.append(trading_signals, "Buy")
        elif df["Close"].iloc[i]>=df["Upper Band"].iloc[i]:
            trading_signals = np.append(trading_signals, "Sell")
        else:
            trading_signals = np.append(trading_signals, None)
    
    return trading_signals


if __name__ == '__main__':

    from Strategy_Engine import strategy_engine

    #plot_bollinger_bands(price_df, 50, 2)
    
    strat = boll_buy_lower_sell_upper(price_df, 50, 2)
    history = strategy_engine(price_df, strat, 100000, 0.01, 0.1, close_positions=True)
    print(history)
    fig = px.line(np.cumsum(history["Profit/Loss"]))
    fig.show()
