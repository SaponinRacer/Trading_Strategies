import numpy as np
import pandas as pd
import plotly.express as px

def Hackathon_Simulation(price_df, strat_list, strat_names, total_account, risk_per_trade, total_accepted_risk):
    
    from Strategy_Engine import strategy_engine
    
    if len(strat_list)<1:
        raise ValueError("strat_list must include at least one item")
    if len(strat_list)!=len(strat_names):
        raise ValueError("The length of strat_list does not coincide with the length of strat_names")
    
    strat_df = pd.DataFrame(index=price_df.index, columns=strat_names)
    
    for i in range(0, len(strat_list)):
        strat_history = strategy_engine(price_df, strat_list[i], total_account, risk_per_trade[i], total_accepted_risk[i],
                                        close_positions=True)
        strat_history_pl = strat_history[["Closed on", "Profit/Loss"]].groupby("Closed on").sum()
        for j in range(0, len(strat_history_pl)):
            strat_df.loc[strat_history_pl.index[j], strat_names[i]] = strat_history_pl["Profit/Loss"].iloc[j]
        print("Completed: ", strat_names[i])
        
    strat_pl = np.cumsum(strat_df.fillna(0))
    
    return strat_pl

if __name__ == '__main__':

    #For VSCode
    price_df = pd.read_csv(r"Trading_Strategies\Algotrading\AAPL_data.csv", index_col="Date")
    #For Jupyter Notebook
    #price_df = pd.read_csv("AAPL_data.csv", index_col="Date")
    price_df.index.name = None

    from Bollinger_Bands import boll_buy_lower_sell_upper
    from Golden_Cross_Death_Cross import golden_cross_death_cross

    strat_list = [boll_buy_lower_sell_upper(price_df), golden_cross_death_cross(price_df)]

    history = Hackathon_Simulation(price_df, strat_list, ["Bollinger Bands", "Golden Cross - Death Cross"], 100000, [0.01, 0.1], [0.1, 1])

    fig = px.line(history, labels={"variables":"Strategies", "value":"Profit/Loss"})
    fig.show()