import numpy as np
import pandas as pd

def strategy_engine(price_df, strategy, total_account, risk_per_trade, total_accepted_risk, close_positions=False):

    """Intakes a dataframe with Close price of an asset; strategy array that must be the same length as the price dataframe and should contain entries Buy, Sell or None; total account value with which the strategy will be traded; risk per trade that the trader is ready to take; and total accepted risk for all currently open positions.
    Returns the dataframe with the history of transactions and prints the total account value by end of the simuation, plus the frozen funds that will be unavailable for further transactions due to currently open trades."""
    
    if len(price_df)!=len(strategy):
        raise TypeError("price_df and strategy must have the coinciding number of entries")
    if total_account<=0:
        raise ValueError("total_account should be a positive real number")
    if (risk_per_trade<=0) and (1<risk_per_trade):
        raise ValueError("risk_per_trade should be a real value in (0,1]")
    if (total_accepted_risk<=0) and (1<total_accepted_risk):
        raise ValueError("total_accepted_risk should be a real value in (0,1]")
    
    current_open_sells = 0
    current_open_buys = 0
    frozen_funds = 0
    trading_history = pd.DataFrame(columns=["Action", "Entry Price", "Closing Price", "Opened on", "Closed on",
                                            "Number of Shares", "Total Investment", "Profit/Loss"])
    
    for i in range(0, len(strategy)):
        #Check the total balance
        if total_account<=0:
            print("You are bunkrupt")
            print("Your final balance is:", total_account)
            return trading_history
        
        #Actions performed on the Buy signal
        if strategy[i]=="Buy":
            #Check for positions to close
            if current_open_sells>0:
                incoming_balance = 0
                for j in np.linspace(current_open_sells, 1, current_open_sells):
                    j = int(j)
                    trading_history.loc[:, "Closed on"].iloc[-j] = price_df.index[i]
                    trading_history.loc[:, "Closing Price"].iloc[-j] = price_df["Close"].iloc[i]
                    trading_history.loc[:, "Profit/Loss"].iloc[-j] = (trading_history["Total Investment"].iloc[-j]
                                                               - trading_history["Closing Price"].iloc[-j]*trading_history["Number of Shares"].iloc[-j])
                    incoming_balance = incoming_balance+trading_history["Profit/Loss"].iloc[-j]
                total_account = total_account+incoming_balance
                current_open_sells = 0
                frozen_funds = 0
            #Implement buy transaction
            total_investment=price_df["Close"].iloc[i]*np.floor(total_account*risk_per_trade/price_df["Close"].iloc[i])
            if ((frozen_funds+total_investment)/total_account)<=total_accepted_risk and (total_investment>0):
                current_df = pd.DataFrame(data=[["Buy", price_df["Close"].iloc[i], None, price_df.index[i], None,
                                                np.floor(total_account*risk_per_trade/price_df["Close"].iloc[i]),
                                               total_investment, None]],
                                         columns=["Action", "Entry Price", "Closing Price", "Opened on", "Closed on",
                                                  "Number of Shares", "Total Investment", "Profit/Loss"])
                trading_history = trading_history.append(current_df, ignore_index=True)
                frozen_funds = frozen_funds+total_investment
                current_open_buys = current_open_buys+1
            else:
                continue
        
        #Actions performed on Sell signal
        if strategy[i]=="Sell":
            #Check for positions to close
            if current_open_buys>0:
                incoming_balance = 0
                for j in np.linspace(current_open_buys, 1, current_open_buys):
                    j = int(j)
                    trading_history.loc[:, "Closed on"].iloc[-j] = price_df.index[i]
                    trading_history.loc[:, "Closing Price"].iloc[-j] = price_df["Close"].iloc[i]
                    trading_history.loc[:, "Profit/Loss"].iloc[-j] = (trading_history["Closing Price"].iloc[-j]*trading_history["Number of Shares"].iloc[-j]
                                                               - trading_history["Total Investment"].iloc[-j])
                    incoming_balance = incoming_balance+trading_history["Profit/Loss"].iloc[-j]
                total_account = total_account+incoming_balance
                current_open_buys = 0
                frozen_funds = 0
            #Implement sell transaction
            total_investment=price_df["Close"].iloc[i]*np.floor(total_account*risk_per_trade/price_df["Close"].iloc[i])
            if (((frozen_funds+total_investment)/total_account)<=total_accepted_risk) and (total_investment>0):
                current_df = pd.DataFrame(data=[["Sell", price_df["Close"].iloc[i], None, price_df.index[i], None,
                                                np.floor(total_account*risk_per_trade/price_df["Close"].iloc[i]),
                                               total_investment, None]],
                                         columns=["Action", "Entry Price", "Closing Price", "Opened on", "Closed on",
                                                  "Number of Shares", "Total Investment", "Profit/Loss"])
                trading_history = trading_history.append(current_df, ignore_index=True)
                frozen_funds = frozen_funds+total_investment
                current_open_sells = current_open_sells+1
            else:
                continue
    
    if close_positions==True:
        for k in trading_history[trading_history["Closing Price"].isna()].index:
            trading_history.loc[:, "Closing Price"].iloc[k] = price_df["Close"].iloc[-1]
            trading_history.loc[:, "Closed on"].iloc[k] = price_df.index[-1]
            if trading_history["Action"].iloc[k]=="Buy":
                trading_history.loc[:, "Profit/Loss"].iloc[k] = (trading_history["Closing Price"].iloc[k]*trading_history["Number of Shares"].iloc[k]
                                                         -trading_history["Total Investment"].iloc[k])
            else:
                trading_history.loc[:, "Profit/Loss"].iloc[k] = (trading_history["Total Investment"].iloc[k]
                                                         -trading_history["Closing Price"].iloc[k]*trading_history["Number of Shares"].iloc[k])
            total_account = total_account+trading_history["Profit/Loss"].iloc[k]
        frozen_funds = 0
        
    print("Frozen funds:", frozen_funds) 
    print("Total account value:", total_account)
    return trading_history