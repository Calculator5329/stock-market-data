import yfinance as yf

myTicker = "meta"

ticker = yf.Ticker(myTicker)

financials = ticker.get_financials(as_dict=True)

print(ticker.get_shares()['BasicShares'][2021])
