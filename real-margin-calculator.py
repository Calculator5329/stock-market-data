import math

import requests
import yfinance as yf
import datetime as dt
import numpy as np
from bs4 import BeautifulSoup


def decimal_round(val, places=2):
    return round(val * 10 ** places) / 10 ** places


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
    try:
        formatted_margins.append(decimal_round(100 * ((ttm_fcf - ttm_sbc) / ttm_rev)))
    except ZeroDivisionError:
        pass

    return [years, formatted_margins]


url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
res = requests.get(url)
soup = BeautifulSoup(res.content, 'html.parser')
table = soup.find_all('table')[0]
sp500_tickers = []
for row in table.find_all('tr')[1:]:
    ticker = row.find_all('td')[0].text
    sp500_tickers.append(ticker.strip())

tickers = sp500_tickers

#tickList = ["PINS", "CRSR", "CRCT", "AMZN", "META", "DBX", "WIX", "GOOGL", ""
#            "BABA", "VZ", "TTCF", "ROKU", "TDOC", "NFLX", "MSFT"]

tickList = tickers
allMargins = {}

for i in tickList:

    # myTicker = validate_str_input("Enter a ticker to check margin: ")
    myTicker = i

    print("")
    print(myTicker)
    print("")

    # Create a master list so we don't have to run the function twice
    adjusted_margins = adjusted_margin(myTicker)

    years, marginList = adjusted_margins[0], adjusted_margins[1]

    for index, year in enumerate(years):
        if year == "TTM" and len(marginList) > index:
            print(f"TTM: {marginList[index]}%")
        elif len(marginList) > index:
            print(f"Year: {year} Margin: {marginList[index]}%")

    allMargins[i] = marginList

# allMargins = {'PINS': [-123.46, -18.29, 12.74, 4.5], 'CRSR': [2.21, 9.06, -0.42, 0.09], 'CRCT': [-2.48, 22.62, -13.69, -4.8], 'AMZN': [5.27, 4.33, -5.85, -8.77], 'META': [23.16, 19.89, 25.4, 12.63], 'DBX': [7.8, 11.97, 19.18, 18.35], 'WIX': [2.39, -1.83, -15.23, -23.0], 'GOOGL': [12.47, 16.35, 20.04, 15.71], 'BABA': [16.94, 20.3, 19.31, 7.67, 11.75], 'VZ': [12.82, 16.72, -21.21, 7.6, 6.9], 'TTCF': [-5.28, -24.13, -34.36, -55.54], 'ROKU': [-13.83, -3.84, 0.02, -14.05], 'TDOC': [-8.63, -50.74, -8.49, -7.04], 'NFLX': [-17.59, 6.06, -1.8, 3.3, 0.95], 'MSFT': [26.71, 27.93, 29.75, 29.07, 22.56]}


print(allMargins)

marginSums = [[], [], [], []]

for key in allMargins.keys():
    print(f"{key} {allMargins[key]}")
    for j in range(3):
        marginSums[j].append(allMargins[key][j])

    if len(allMargins[key]) > 3:
        marginSums[3].append(allMargins[key][3])

for i in range(4):
    if i == 3:
        print(f"TTM Mean: {decimal_round(np.mean(marginSums[i]))}")
    else:
        print(f"{2019 + i} Mean: {decimal_round(np.mean(marginSums[i]))}")

for i in range(4):
    if i == 3:
        print(f"TTM Median: {decimal_round(np.median(marginSums[i]))}")
    else:
        print(f"{2019 + i} Median: {decimal_round(np.median(marginSums[i]))}")