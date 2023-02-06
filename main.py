import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import numpy as np


def plot_panda(panda, index):
    df = pd.DataFrame(panda)

    print(df)

    fig, ax = plt.subplots()

    ax.plot(df[index])

    ax.yaxis.set_major_formatter('${x:,.2f}')

    plt.show()


# S&P Ticker list


url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
res = requests.get(url)
soup = BeautifulSoup(res.content, 'html.parser')
table = soup.find_all('table')[0]
sp500_tickers = []
for row in table.find_all('tr')[1:]:
    ticker = row.find_all('td')[0].text
    sp500_tickers.append(ticker.strip())

tickers = sp500_tickers

financials_list = {}

for i in tickers:
    financials_list[i] = yf.Ticker(i).get_financials()
    print(i)

revenue_figures = {0: [], 1: [], 2: [], 3: []}

for i in tickers:
    yf_ticker = yf.Ticker(i)

    financials = yf_ticker.get_financials()

    if len(financials.columns) == 4:
        for i in range(3):
            financials.columns[i] = 2022 - i

    if len(financials.columns) == 3:
        for i in range(3):
            financials.columns[i] = 2021 - i

    for i, date in enumerate(financials.columns):
        revenue_figures[i].append(financials[date]['TotalRevenue'] / 1000000)

    print(len(revenue_figures[1]))

    '''

    msft = yf.Ticker("MSFT")

    financials = msft.get_financials()

    print(financials.columns)

    plot_arr = []
    dates = []

    for date in financials.columns:
        print(date)
        print(financials[date]['TotalRevenue'])
        dates.append(date)
        plot_arr.append(financials[date]['TotalRevenue']/1000000)


    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(dates, plot_arr, width=250)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, pos: "${:,.0f}".format(x)))

    # set the x-axis tick frequency to 30
    plt.xticks(np.arange(min(dates).to_datetime64(), max(dates).to_datetime64()+np.timedelta64(365,'D'), np.timedelta64(365,'D')))
    plt.xticks(dates, [d.strftime("%Y") for d in dates])

    plt.title("Revenue")
    plt.xlabel("Year")
    plt.ylabel("Revenue (in units)")
    plt.show()
    '''



