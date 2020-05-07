import pandas as pd
from bs4 import BeautifulSoup
import ssl
from urllib.request import Request, urlopen


__all__ = ['yhparse_many', 'yhparse_one']


def yhparse_one(ticker, verbose=False):
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
    afterhourprice = None
    for span in soup.findAll('span',
                                                        # Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)
                             attrs={'class': closepricespanclass  # 'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)'
                                    }):
        closeprice = float(span.text.strip().replace(',', ''))
        closepricecnt += 1
    for span in soup.findAll('span', attrs={'class': afterhoursspanclass}):
        afterhourprice = float(span.text.strip().replace(',', ''))
        afterhourspricecnt += 1

    if not (closepricecnt == 1 and afterhourspricecnt <= 1):
        # something wrong.
        if verbose:
            print("Something wrong with this ticker {0}, return nothing".format(ticker), flush=True)
        return None
    nowtime = pd.to_datetime('today')
    nowdate = nowtime.date()
    d = pd.DataFrame({'ticker': [ticker], 'date': [nowdate], 'datetime': [nowtime],
                      'closeprice': [closeprice],
                      'afterhourprice': [afterhourprice]})
    return d


def yhparse_many(tickers=None, verbose=False):
    """
    Yahoo parse tickers after hours price
    :param tickers: list of tickers, or single str
    :param verbose: default False, True to print progress.
    :return: pandas DataFrame
    """
    if tickers is None:
        tickers = ['SPY', 'USO', 'GOOG', 'AAPL']
    if not isinstance(tickers, (list,)):
        tickers = [tickers]
    dl = [yhparse_one(ticker, verbose=verbose) for ticker in tickers]
    return pd.concat(dl, ignore_index=True)


if __name__ == '__main__':
    # d = yhparse_one("SPY")
    # print(d)

    d2 = yhparse_many(['SPY', 'USO', 'GOOG', 'AAPL'], verbose=True)
    print(d2)
