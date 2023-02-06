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

# tickList = ["PINS", "CRSR", "CRCT", "AMZN", "META", "DBX", "WIX", "GOOGL", ""
#            "BABA", "VZ", "TTCF", "ROKU", "TDOC", "NFLX", "MSFT"]

tickList = tickers
allMargins = {}

myTicker = validate_str_input("Enter a ticker to check margin: ").upper()


print("")
print(f"Gathering margin data for {myTicker}")
print("")

# Create a master list so we don't have to run the function twice
adjusted_margins = adjusted_margin(myTicker)

years, marginList = adjusted_margins[0], adjusted_margins[1]

for index, year in enumerate(years):
    if year == "TTM" and len(marginList) > index:
        print(f"TTM: {marginList[index]}%")
    elif len(marginList) > index:
        print(f"Year: {year} Margin: {marginList[index]}%")



