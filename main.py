import math
import pandas as pd
import requests
import yfinance as yf
import datetime as dt
import numpy as np
from bs4 import BeautifulSoup


def decimal_round(val, places=2):
    return round(val * 10 ** places) / 10 ** places


def get_market_cap(symbol):
    ticker = yf.Ticker(symbol)
    stock_info = ticker.fast_info
    return stock_info['market_cap']


def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    stock_info = ticker.fast_info
    return stock_info['last_price']


def validate_str_input(firstString, errorString="Error, please enter a string: "):
    validatedInput = ""
    tryLoop = True

    try:
        validatedInput = str(input(firstString))
    except ValueError:
        while tryLoop:
            tryLoop = False
            try:
                validatedInput = str(input(errorString))
            except ValueError:
                tryLoop = True
    return validatedInput


def adjusted_margin(inputTicker):
    ticker = yf.Ticker(inputTicker)
    dates = []
    fcf = []
    sbc = []
    revenues = []

    for date in ticker.cashflow:
        dates.append(date)

    dates.reverse()

    for date in dates:
        fcf.append(ticker.cashflow[date]['Free Cash Flow'])
        try:
            if not math.isnan(ticker.cashflow[date]['Stock Based Compensation']):
                sbc.append(ticker.cashflow[date]['Stock Based Compensation'])
            else:
                sbc.append(0)
        except KeyError:
            # this is for if the stock has no sbc
            sbc.append(0)
        try:
            revenues.append(ticker.financials[date]['Total Revenue'])
        except KeyError:
            pass
    # Prints latest FCF
    # print(fcf[-1])

    # Prints latest SBC
    # print(sbc[-1])

    # Prints latest Revenue
    # print(revenues[-1])

    margins = []

    for index, rev in enumerate(revenues):
        margins.append((fcf[index] - sbc[index]) / rev)

    years = []
    formatted_margins = []

    for index, margin in enumerate(margins):
        years.append(dates[index].strftime("%Y"))
        formatted_margins.append(decimal_round(100 * margin))

    ttm_fcf = 0
    ttm_sbc = 0
    ttm_rev = 0

    # this should be for in range 4
    for i in ticker.quarterly_financials:
        ttm_rev += ticker.quarterly_financials[i]['Total Revenue']

    # this should be for in range 4
    for i in ticker.quarterly_cashflow:
        ttm_fcf += ticker.quarterly_cashflow[i]['Free Cash Flow']
        try:
            if not math.isnan(ticker.quarterly_cashflow[i]['Stock Based Compensation']):
                sbc.append(ticker.quarterly_cashflow[i]['Stock Based Compensation'])
            else:
                sbc.append(0)
        except KeyError:
            # When there is no sbc
            ttm_sbc = 0

    years.append("TTM")
    revenues.append(ttm_rev)

    try:
        formatted_margins.append(decimal_round(100 * ((ttm_fcf - ttm_sbc) / ttm_rev)))
    except ZeroDivisionError:
        pass

    return [years, formatted_margins, revenues]


sp500 = True

if sp500:

    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    table = soup.find_all('table')[0]
    sp500_tickers = []
    for row in table.find_all('tr')[1:]:
        ticker = row.find_all('td')[0].text
        sp500_tickers.append(ticker.strip())

    tickers = sp500_tickers

# tickList = ["PINS", "CRSR", "CRCT", "AMZN", "META", "DBX", "WIX", "GOOGL", ""
#            "BABA", "VZ", "TTCF", "ROKU", "TDOC", "NFLX", "MSFT"]

print(tickers)

if sp500:
    tickList = tickers
else:
    tickList = []
    # tickList = ["MSFT", "AAPL", "AMZN", "GOOGL", "META"]
allMargins = {}
allRevenues = {}
revGrowthList = {}

for i in tickList:

    # myTicker = validate_str_input("Enter a ticker to check margin: ")
    myTicker = i

    print(f"Calculating data for: {myTicker}")
    print("")

    # Create a master list so we don't have to run the function twice
    adjusted_margins = adjusted_margin(myTicker)

    years, marginList, revenueList = adjusted_margins[0], adjusted_margins[1], adjusted_margins[2]

    for index, year in enumerate(years):
        if year == "TTM" and len(marginList) > index:
            # print(f"TTM: {marginList[index]}%")
            pass
        elif len(marginList) > index:
            # print(f"Year: {year} Margin: {marginList[index]}%")
            pass

    allMargins[i] = marginList
    allRevenues[i] = revenueList
    currentGrowthList = []
    for j in range(3):
        currentGrowthList.append((revenueList[j + 1] / revenueList[j] - 1) * 100)

    revGrowthList[i] = currentGrowthList

    print(f"Finished data collection for: {myTicker}")

market_caps = []
current_prices = []

for tick in tickList:
    market_caps.append(get_market_cap(tick))
    current_prices.append(get_current_price(tick))

print(allMargins)
print(allRevenues)
print(revGrowthList)

marginSums = [[], [], [], []]
revenueSums = [[], [], [], []]
revGrowthSums = [[], [], [], []]

for key in allRevenues.keys():
    for j in range(3):
        revenueSums[j].append(allRevenues[key][j])

    if len(allRevenues[key]) > 3:
        revenueSums[3].append(allRevenues[key][3])

for key in revGrowthList.keys():
    for j in range(2):
        revGrowthSums[j].append(revGrowthList[key][j])
    if len(revGrowthList[key]) > 2:
        revGrowthSums[2].append(revGrowthList[key][2])

for key in allMargins.keys():
    # print(f"{key} {allMargins[key]}")
    for j in range(3):
        marginSums[j].append(allMargins[key][j])

    if len(allMargins[key]) > 3:
        marginSums[3].append(allMargins[key][3])

p_fcfs = []
mcapTotal = 0
fcfTotal = 0
for index, tick in enumerate(tickList):
    current_fcf = decimal_round(marginSums[-1][index] * revenueSums[-1][index] / 100)
    current_mcap = decimal_round(market_caps[index])
    p_fcf = decimal_round(current_mcap / current_fcf)
    # current_price = decimal_round(current_prices[index])

    fcfTotal += current_fcf
    mcapTotal += current_mcap
    if p_fcf > 0:
        p_fcfs.append(p_fcf)

data = {"Metric" : [], "Value" : []}

data["Metric"].append("Average P/FCF of the profitable companies")
data["Value"].append(decimal_round(np.mean(p_fcfs)))

data["Metric"].append("Total P/FCF (Sum of all market caps / Sum of all FCF's)")
data["Value"].append(decimal_round(mcapTotal / fcfTotal))

# data["Metric"].append("Average P/FCF of the profitable companies")
# data["Value"].append(decimal_round(np.mean(p_fcfs)))

# print(p_fcfs)
# print(f"Average P/FCF of the profitable companies: {decimal_round(np.mean(p_fcfs))}")
# print(f"Total P/FCF (Sum of all market caps / Sum of all FCF's) {decimal_round(mcapTotal / fcfTotal)}")

for i in range(4):
    if i == 3:
        # print(f"TTM Margin Mean: {decimal_round(np.mean(marginSums[i]))}%")
        data["Metric"].append("TTM Margin Mean")
        data["Value"].append(decimal_round(np.mean(marginSums[i])))
    else:
        # print(f"{2019 + i} Margin Mean: {decimal_round(np.mean(marginSums[i]))}%")
        data["Metric"].append(f"{2019 + i} Margin Mean")
        data["Value"].append(decimal_round(np.mean(marginSums[i])))

for i in range(4):
    if i == 3:
        # print(f"TTM Margin Median: {decimal_round(np.median(marginSums[i]))}%")
        data["Metric"].append("TTM Margin Median")
        data["Value"].append(decimal_round(np.median(marginSums[i])))
    else:
        # print(f"{2019 + i} Margin Median: {decimal_round(np.median(marginSums[i]))}%")
        data["Metric"].append(f"{2019 + i} Margin Median")
        data["Value"].append(decimal_round(np.median(marginSums[i])))

for i in range(4):
    if i == 3:
        # print(f"TTM Revenue Mean: {decimal_round(np.mean(revenueSums[i]) / 1e9)}B")
        data["Metric"].append("TTM Revenue Mean")
        data["Value"].append(decimal_round(np.mean(revenueSums[i]) / 1e9))
    else:
        # print(f"{2019 + i} Revenue Mean: {decimal_round(np.mean(revenueSums[i]) / 1e9)}B")
        data["Metric"].append(f"{2019 + i} Revenue Mean")
        data["Value"].append(decimal_round(np.mean(revenueSums[i]) / 1e9))

for i in range(3):
    if i == 2:
        # print(f"TTM Revenue Growth (weighted): "
        #      f"{decimal_round(100 * (np.mean(revenueSums[i + 1]) / np.mean(revenueSums[i]) - 1))}%")
        data["Metric"].append("TTM Revenue Growth (weighted)")
        data["Value"].append(decimal_round(100 * (np.mean(revenueSums[i + 1]) / np.mean(revenueSums[i]) - 1)))
    else:
        # print(f"{2020 + i} Revenue Growth (weighted): "
        #      f"{decimal_round(100 * (np.mean(revenueSums[i + 1]) / np.mean(revenueSums[i]) - 1))}%")
        data["Metric"].append(f"{2020 + i} Revenue Growth (weighted)")
        data["Value"].append(decimal_round(100 * (np.mean(revenueSums[i + 1]) / np.mean(revenueSums[i]) - 1)))

for i in range(3):
    if i == 2:
        # print(f"TTM Revenue Growth (unweighted): {decimal_round(np.mean(revGrowthSums[2]))}%")
        data["Metric"].append("TTM Revenue Growth (unweighted)")
        data["Value"].append(decimal_round(np.mean(revGrowthSums[2])))
    else:
        # print(f"{2020 + i} Revenue Growth (unweighted): {decimal_round(np.mean(revGrowthSums[i]))}%")
        data["Metric"].append(f"{2020 + i} Revenue Growth (unweighted)")
        data["Value"].append(decimal_round(np.mean(revGrowthSums[i])))

df = pd.DataFrame(data)
filename = r'\export_dataframe5.csv'
df.to_csv(r'C:\Users\et2bo\Documents' + filename, index=False, header=True)

print("Succesfully exported to " + str(filename))
