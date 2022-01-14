from flask import Flask, request, abort
import re
from datetime import date, timedelta, datetime
from pandas_datareader import data as pdr #panda_datareader api
from fractions import Fraction
import yfinance as yfin  # yahoo finance API
yfin.multi
yfin.pdr_override()
app = Flask(__name__)

def get_stock(symbol):
    start_date = request.args.get("period1")
    end_date = request.args.get("period2")

    unix_start = datetime.utcfromtimestamp(int(start_date)) if start_date else (date.today() - timedelta(days=8))
    unix_end = datetime.utcfromtimestamp(int(end_date)) if end_date else None
    dfSymbol = pdr.get_data_yahoo(symbol,  start=unix_start, end=unix_end, actions=True)

    if dfSymbol.empty:
        abort(404)
    dfSymbol.index = dfSymbol.index.strftime("%Y-%m-%d")

    dfTicks = dfSymbol[['Open', 'High', 'Low','Close', 'Volume']]
    dictTicks = dfTicks.to_dict('index')

    dfDividends = dfSymbol[dfSymbol['Dividends'] > 0][["Dividends"]]
    dictDividends = dfDividends.to_dict('index')

    dfSplits = dfSymbol[dfSymbol['Stock Splits'] > 0][["Stock Splits"]]
    dictSplits = dfSplits.to_dict('index')
    dictSplits = get_divisions(dictSplits)

    return {"chart": dictTicks, "dividends": dictDividends, "splits": dictSplits}

def get_divisions(splits):
    newDict = {}
    for k, v in splits.items():
        if v != 0:
            fractions_num = Fraction(v["Stock Splits"]).limit_denominator()
            newDict[k] = {
                "Numerator": fractions_num.numerator,
                "Denominator": fractions_num.denominator 
            }
    return newDict

def get_dividends(dividends):
    newDict = {}
    for k, v in dividends.items():
        if v != 0:
            newDict[k] = v
    return newDict

@app.route("/get-chart")
def get_symbol():
    symbol = request.args.get("symbol")
    if not symbol:
        abort(404)
    return get_stock(symbol)