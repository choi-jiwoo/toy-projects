from bs4 import BeautifulSoup as bs
from functools import lru_cache
import pandas as pd
import requests
from financialdatapy.stock import Stock
from pyrich.api import set_finnhub
from pyrich.error import SearchError


HEADERS = {
    'User-Agent': 'Mozilla',
    'X-Requested-With': 'XMLHttpRequest',
}

@lru_cache
def get_current_price(symbol: str, country: str) -> dict:
    if country == 'USA':
        price_data = get_from_us_market(symbol)
    elif country == 'KOR':
        kor_symbol = search_kor_company_symbol(symbol)
        price_data = get_from_kor_market(kor_symbol)
    elif country == 'CRYPTO':
        price_data = get_crypto_price(symbol)
    else:
        raise SearchError(f"'{symbol}' not found in '{country}' stock exchange.")
    return price_data

def get_from_us_market(symbol: str) -> dict:
    # https://finnhub.io/docs/api/quote
    finnhub = set_finnhub()
    quote = finnhub.quote(symbol)
    current_price_and_pct_change = ['c', 'd', 'dp']
    price_data = {
        k: quote[k]
        for k
        in current_price_and_pct_change
    }
    return price_data

def get_crypto_price(symbol: str) -> dict:
    url = 'https://crix-api-cdn.upbit.com/v1/crix/trades/ticks'
    params = {
        'code': f'CRIX.UPBIT.KRW-{symbol}',
        'count': 1,
    }
    res = requests.get(url, headers=HEADERS, params=params)
    try:
        res_data = res.json()
        first_res = res_data[0]
        current_price = first_res['tradePrice']
        close_price = first_res['prevClosingPrice']
        pct_change = (current_price - close_price) / close_price
        data = [current_price, pct_change]
        current_price_and_pct_change = ['c', 'd', 'dp']
        price_data = {
            k: v
            for k, v
            in zip(current_price_and_pct_change, data)
        }
        return price_data
    except Exception as e:
        print(e)

def search_kor_company_symbol(company_name: str) -> tuple:
    url = 'http://data.krx.co.kr/comm/util/SearchEngine/isuCore.cmd'
    params = {
        'isAutoCom': True,
        'solrIsuType': 'STK',
        'solrKeyword': company_name,
        'rows': '20',
        'start': '0',
    }
    res = requests.post(url, headers=HEADERS, params=params)
    try:
        res_data = res.json()
        first_search_res = res_data['result'][0]
        symbol = first_search_res['isu_srt_cd'][0]
        return symbol
    except Exception:
        res.raise_for_status()

def scrape_from_naver_finance(symbol: str) -> tuple[list, list]:
    url = f'https://finance.naver.com/item/main.nhn?code={symbol}'
    res = requests.get(url, headers=HEADERS)
    try:
        html = res.text
        soup = bs(html, 'html.parser')
        today = soup.select_one('#chart_area > div.rate_info > div')
        change_info = today.find_all('span', class_='blind')
        change_direction = today.find_all('span', class_='ico')
    except Exception:
        res.raise_for_status()

    direction = []
    for i in change_direction:
        item = i.get_text()
        direction.append(item)
    
    quote = []
    for tag in change_info:
        item = tag.get_text()
        item = item.replace(',', '')
        item = float(item)
        quote.append(item)

    return quote, direction

def get_from_kor_market(symbol: str) -> dict:
    quote, change_direction = scrape_from_naver_finance(symbol)
    change = change_direction[0]
    fall_state = '하락'
    if change == fall_state:
        for i in range(1, len(quote)): quote[i] *= -1
    current_price_and_pct_change = ['c', 'd', 'dp']  # c: current price, d: day change, dp: percent change
    price_data = {
        k: v
        for k, v
        in zip(current_price_and_pct_change, quote)
    }
    return price_data

@lru_cache
def get_historical_price(symbol: str, country: str) -> pd.DataFrame:
    comp = Stock(symbol, country)
    end_date = pd.Timestamp.today()
    one_year = pd.Timedelta(weeks=52)
    start_date = end_date - one_year
    date_format = '%Y-%m-%d'
    start_date = start_date.strftime(date_format)
    end_date = end_date.strftime(date_format)
    historical_price = comp.price(start_date, end_date)
    historical_price.set_index('Date', inplace=True)
    return historical_price
