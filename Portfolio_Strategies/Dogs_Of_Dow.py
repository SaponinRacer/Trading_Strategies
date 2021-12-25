import pandas as pd
import datetime
import yfinance as yf

start_date=datetime.date(2021, 1, 1)
end_date=datetime.date.today()

dow_tickers=["AXP", "AMGN", "AAPL", "BA", "CAT", "CSCO", "CVX", "GS", "HD", "HON", "IBM", "INTC", "JNJ", "KO", "JPM", "MCD", 
             "MMM", "MRK", "MSFT", "NKE", "PG", "TRV", "UNH", "CRM", "VZ", "V", "WBA", "WMT", "DIS", "DOW"]

tickers_entry=" ".join(dow_tickers)
y_tickers=yf.Tickers(tickers_entry)


dividends_df=pd.DataFrame(index=y_tickers.tickers.keys(), columns=["Dividend Yield"])
for ticker in y_tickers.tickers:
    dividends_df["Dividend Yield"][ticker]=y_tickers.tickers[ticker].info["dividendYield"]

dividends_df=dividends_df*100

print("Strategy for this year:")
print(dividends_df["Dividend Yield"].sort_values(ascending=False).head(10))
