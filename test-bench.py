import yfinance as yf

myTicker = "meta"

ticker = yf.Ticker(myTicker)

print(ticker.quarterly_cashflow)

data = yf.download(myTicker, interval='3mo', period='max')

print(data)
