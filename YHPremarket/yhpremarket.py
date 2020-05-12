import pandas as pd
from bs4 import BeautifulSoup
import ssl
from urllib.request import Request, urlopen
import time
import datetime as dt
import re


__all__ = ['yhparse_many', 'yhparse_one']


def yhparse_one(ticker, verbose=False, sleep=None):
    """
    Get Yahoo price for one ticker.
    :param ticker:
    :param verbose:
    :return:
    """
    # get idea from:
    # https://www.promptcloud.com/blog/how-to-scrape-yahoo-finance-data-using-python/
    if verbose:
        print(" *** Yahoo Parsing ticker {0}".format(ticker), flush=True)
    url = "https://finance.yahoo.com/quote/%s?p=%s" % (ticker, ticker)
    # For ignoring SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Making the website believe that you are accessing it using a Mozilla browser
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    if sleep is not None:
        time.sleep(sleep)
    webpage = urlopen(req).read()
    # Creating a BeautifulSoup object of the HTML page for easy extraction of data.

    soup = BeautifulSoup(webpage, 'html.parser')
    # html = soup.prettify('utf-8')
    # company_json = {}

    closepricespanclass = 'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)'
    afterhoursspanclass = 'C(black) Fz(14px) Fw(500)'
    closepricecnt = 0
    afterhourspricecnt = 0
    closeprice = None
    closetime = None
    afterhourprice = None
    pretime = None

    # this is to find the regular price.
    for span in soup.findAll('span',
                                                        # Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)
                             attrs={'class': closepricespanclass  # 'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)'
                                    }):
        closeprice = float(span.text.strip().replace(',', ''))
        closepricecnt += 1
        try:
            closetime = span.next_sibling.next_element.next_element.next_element.next_element.next
        except:
            closetime = None
        if closetime is not None and closetime != '':
            closetime = closetime.replace("At close:  ", '').replace(" EDT", '').replace(" EST", '')
            closetime = gsub_one('(.* )?([0-9]+:[0-9]+[APM]+)', '\\2', closetime)
            aa = dt.datetime.strptime(closetime, '%H:%M%p')
            atoday = dt.datetime.today()
            atoday.replace(hour=aa.hour, minute=aa.minute, second=0, microsecond=0)
            closetime = atoday

    # this is to find the premarket or afterhours price.
    is_premarket = False
    for span in soup.findAll('span', attrs={'class': afterhoursspanclass}):
        afterhourprice = float(span.text.strip().replace(',', ''))

        afterhourspricecnt += 1
        try:
            ispre = span.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_element.next_element
        except:
            ispre = None
        if ispre == 'Pre-Market:':
            is_premarket = True
        try:
            pretime = span.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_element.next_element.next_element.next_element.next_element.next_element.next_element
        except:
            pretime = None
        if pretime is not None and pretime != '':
            pretime = pretime.replace(" EDT", '').replace(" EST", '')
            aa = dt.datetime.strptime(pretime, '%H:%M%p')
            atoday = dt.datetime.today()
            atoday.replace(hour=aa.hour, minute=aa.minute, second=0, microsecond=0)
            pretime = atoday

    if not (closepricecnt == 1 and afterhourspricecnt <= 1):
        # something wrong.
        if verbose:
            print("Something wrong with this ticker {0}, return nothing".format(ticker), flush=True)
        return None
    if closepricecnt == 1 and afterhourspricecnt == 0:
        datatype = 'marketopen'
    elif closepricecnt == 1 and afterhourspricecnt == 1:
        if is_premarket:
            datatype = 'premarket'
        else:
            datatype = 'aftermarket'
    else:
        datatype = 'unknown'
    nowtime = pd.to_datetime('today')
    nowdate = nowtime.date()
    if is_premarket:
        # use the sraper's datetime stamp.
        nowtime = pretime
    d = pd.DataFrame({'ticker': [ticker], 'date': [nowdate], 'datetime': [nowtime],
                      'closeprice': [closeprice],
                      'realtimeprice': [afterhourprice],
                      'datatype': [datatype]})
    return d


def yhparse_many(tickers=None, verbose=False, sleep=0.5):
    """
    Yahoo parse tickers after hours price
    :param tickers: list of tickers, or single str
    :param verbose: default False, True to print progress.
    :param sleep: how much time (seconds) to sleep to avoid being banned
    :return: pandas DataFrame
    """
    if tickers is None:
        tickers = ['SPY', 'USO', 'GOOG', 'AAPL']
    if not isinstance(tickers, (list,)):
        tickers = [tickers]
    dl = [yhparse_one(ticker, verbose=verbose, sleep=sleep) for ticker in tickers]
    return pd.concat(dl, ignore_index=True)


def gsub_one(pattern, replacement, s, count=0, ignorecase=False):
    if ignorecase:
        p = re.compile(pattern, re.IGNORECASE)
    else:
        p = re.compile(pattern)

    return p.sub(replacement, s, count=count)


if __name__ == '__main__':
    # d = yhparse_one("SPY")
    # print(d)

    d2 = yhparse_many(['SPY', 'USO', 'GOOG', 'AAPL'], verbose=True)
    print(d2)
