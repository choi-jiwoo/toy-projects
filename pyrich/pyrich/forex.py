import pandas as pd


def get_usd_to_krw():
    url = 'https://finance.naver.com/marketindex/exchangeDetail.naver?marketindexCd=FX_USDKRW'
    naver_finance_currency_data = pd.read_html(url)
    currency_table = naver_finance_currency_data[0]
    current_usd_to_krw = currency_table.iloc[0, 0]
    return current_usd_to_krw
