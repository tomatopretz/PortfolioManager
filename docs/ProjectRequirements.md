# Portfolio Manager Training Project

[TOC]

## Overview

Your team is challenged with designing an application to manage a financial portfolio.

The portfolio may contain some or all of stocks, bonds, cash etc. 

Your task is to build the application.


## Technical Goals

You should aim to create a Portfolio Management REST API. This will be the main target for the training week where you learn about APIs.

This API should allow saving and retrieving records that describe the contents of a financial portofolio.

If/When you have made progress on the core requirements then requirements for further enhancements will be provided. This will included open-ended enhancements whereby you can make use of your particular skills and experience.

The Front end should facilitate your users to (in order of priority):

* Browse a portfolio
* View the performance of the portfolio (ideally in some graphical manner)
* Add items to the portfolio
* Remove items from the portfolio

In terms of detailed requirements, your instructor will act as customer, and will tell you what they want. You can arrange meetings with them as required.


## Notes

1. There will be no authentication and a single user is assumed, i.e. there is no requirement to manage users.

2. You should use the database technology you have been using in the training for any persistent storage.

3. Any documentation about how to use your REST API would be useful. 

## Technical Getting Started Checklist

1. Create your project structure.

2. Create a Git repository. Your instructors will guide you as to which Git platform to use.

3. Add, commit, push your skeleton project to your Git repository.

4. Ensure your team has access to the Git repository.

5. Decide on the absolute MINIMUM fields for a first working system e.g. the first version of your model object may just be an id, stockTicker and volume.

If you get stuck getting any of the above completed then contact your instructor for help.


## Suggestions for Success

1. START SMALL. Get a system working that stores a very simple object with minimal fields. You can then enhance to store more complex records.

## Appendix C: Useful links
Simple UI that reads live price data from yahoo finance and displays it in a web page: https://bitbucket.org/fcallaly/simple-price-ui

## Appendix D: Financial Data
You can get Financial data from Yahoo. 


### Python Projects

For those of you using Python, you can access the Yahoo API using code like this:

```
import time
from datetime import datetime
import pandas as pd

dt = datetime(2023, 1, 1)
start_date = int(round(dt.timestamp()))

dt = datetime(2023, 3, 31)
end_date = int(round(dt.timestamp()))

stock = 'GOOG'

df = pd.read_csv(f"https://query1.finance.yahoo.com/v7/finance/download/{stock}?period1={start_date}&period2={end_date}&interval=1d&events=history&includeAdjustedClose=true",
    parse_dates = ['Date'], index_col='Date')

```

You could also explore the Python Library specifically designed to work with Yahoo: https://pypi.org/project/yfinance/

### Sample REST API

We have created a sample API that you can interact with to get dummy financial data.

https://c4rm9elh30.execute-api.us-east-1.amazonaws.com/default/cachedPriceData?ticker=TSLA

It's caching price data from yahoo in the background so it doesn't do excess requests to yahoo. Only a few tickers are there by default. Tickers are: C, AMZN, TSLA, FB, AAPL

