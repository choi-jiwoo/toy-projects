from datetime import datetime
import os
from candlestick_chart import Candle, Chart
import pandas as pd
from pyrich.database import PostgreSQL
from pyrich.transaction import Transaction
from pyrich.forex import get_usd_to_krw
from pyrich.error import CurrencyError
from pyrich import stock
from pyrich import parse
from pyrich import summary
from pyrich.terminal.summary import Financial
from pyrich.terminal.summary import timestamp
from pyrich.terminal.summary import header
from pyrich.terminal.summary import component
from pyrich.terminal.summary import change


ANSI_STYLE_CODE_LEN = 12

def run() -> None:
    # Load arguments
    parser = parse.set_args()
    args = parser.parse_args()
    options = vars(args)

    usd_to_krw = get_usd_to_krw()

    if options['summary']:
        financial = Financial()
        financial.asset.record_current_asset(financial.cur_asset_value)
        total_asset = component('total asset')
        total_cash = component('total cash')
        stock_value = component('stock value')
        portfolio_gain = change(financial.gain, financial.yield_)
        total_invested = component('total invested')

        timestamp_section = timestamp('%Y %B %d %A, %X')
        financial_section = header('financial summary', style='uppercase')
        portfolio_section = header('portfolio components', style='uppercase')

        stock_list_str = []
        stock_list = financial.stock_list

        for item in stock_list.values():
            name = item['symbol']
            current_stock_value = item['current_value']
            invested = item['invested_amount']
            display_currency = item['currency']
            if display_currency == 'USD':
                current_stock_value = current_stock_value * usd_to_krw
                invested = invested * usd_to_krw
            stock_gain = current_stock_value - invested
            stock_yield = summary.current_yield(stock_gain, invested)
            ratio = current_stock_value / financial.current_value
            gain = change(stock_gain, stock_yield)
            symbol = component(name)
            stock_list_str.append(
                f'({ratio:>6,.2%}) {symbol} {current_stock_value:,.2f} 원 {gain}'
            )

        asset_section = header('asset components', style='uppercase')
        stock_ratio_label = component('stock')
        stock_ratio = financial.current_value / financial.cur_asset_value
        cash_ratio_label = component('cash', indent_left=5)
        cash_ratio = financial.total_cash / financial.cur_asset_value

        part_1 = (f'{timestamp_section}\n'
                  f'{financial_section}\n'
                  f'{total_asset} {financial.cur_asset_value:,.2f} 원\n'
                  f'{total_cash} {financial.total_cash:,.2f} 원\n'
                  f'{stock_value} {financial.current_value:,.2f} 원 {portfolio_gain}\n'
                  f'{total_invested} {financial.invested:,.2f} 원\n')
        print(part_1)

        part_2 = f'{portfolio_section}'
        print(part_2)
        for stock_str in stock_list_str:
            print(f'{stock_str}')
                             
        part_3 = (f'\n{asset_section}\n'
                  f'{stock_ratio_label} {stock_ratio:,.2%}\n'
                  f'{cash_ratio_label} {cash_ratio:,.2%}')
        print(part_3)
        return

    # Open a portfolio dashboards
    if options['web']:
        os.system('streamlit run dashboard.py')
        return

    # Set up database connection
    db = PostgreSQL()

    # Copy record from csv file
    if options['csv']:
        table_name = options['csv']
        db.copy_from_csv(table_name)
        return

    # Disaply database table
    if options['show']:
        table_name = options['show']
        table = db.show_table(table_name, msg=False)
        display_table = table.drop(['id'], axis=1)
        display_table_desc = display_table[::-1]
        print(display_table_desc.head())
        return

    # Handling delete option
    if options['deletelast']:
        table_name = options['deletelast']
        db.delete_rows(table_name)
        return

    if options['deleteall']:
        table_name = options['deleteall']
        db.delete_rows(table_name, all_rows=True)
        return

    # Update current cash
    if options['cash']:
        cash_record = options['cash']
        currency_id = {
            'KRW': 1,
            'USD': 2,
        }
        amount = cash_record[0]
        currency = cash_record[1]
        try:
            _id = currency_id[currency]
            cols_to_update = ['amount']
            db.update('cash', cols_to_update, [amount], _id)
        except KeyError:
            raise CurrencyError('Currency should be either USD or KRW.')
        else:
            return

    # Search price
    if options['price']:
        price_record = options['price']
        price_record = [item.upper() for item in price_record]
        price_info = stock.get_current_price(*price_record)
        stock_ = price_record[0]
        current_price = price_info['c']
        day_change = price_info['d']
        pct_change = price_info['dp']
        symbol = component(stock_)
        quote = change(day_change, pct_change)
        price_text = (f'{symbol} {current_price} {quote}')
        search_header = header('search result', style='title')
        print(f'{search_header}: {stock_}\n{price_text}')

        # Display ohlc chart
        historical_price = stock.get_historical_price(*price_record)
        historical_price.reset_index('Date', inplace=True)
        try:
            historical_price['Date'] = historical_price['Date'].apply(
                lambda x: datetime.strptime(x, '%Y-%m-%d').timestamp()
            )
        except TypeError:
            historical_price['Date'] = historical_price['Date'].apply(
                lambda x: x.timestamp()
            )
        price_data_by_row = historical_price.values
        cols = ['timestamp', 'close', 'open', 'high', 'low', 'volume']
        price_data = pd.DataFrame(price_data_by_row, columns=cols)
        candles = [
            Candle(
                timestamp=price_data['timestamp'][i],
                close=price_data['close'][i],
                open=price_data['open'][i],
                high=price_data['high'][i],
                low=price_data['low'][i],
                volume=price_data['volume'][i],
            )
            for i
            in range(len(price_data))
        ]
        width = os.get_terminal_size()[0]
        chart = Chart(candles, title=f'{stock_}', width=width, height=16)
        chart.set_volume_pane_enabled(False)
        chart.set_label('average', '')
        chart.set_label('volume', '')
        chart.set_label('variation', '')
        chart.draw()
        return

    # Record transaction
    if not options['dividend']:
        headers = ['date', 'country', 'type', 'symbol', 'quantity', 'price']
        transaction = Transaction(options['transaction'], headers=headers)
        transaction_record = transaction.record
        total_price_paid = transaction_record['quantity'] * transaction_record['price']
        transaction_record['total_price_paid'] = total_price_paid
        transaction_record['total_price_paid_in_krw'] = transaction_record['total_price_paid']
        if transaction_record['country'] == 'USA':
            transaction_record['total_price_paid_in_krw'] *= usd_to_krw
        db.insert('transaction', transaction_record)
    else:
        headers = ['date', 'symbol', 'dividend', 'currency']
        dividends = Transaction(options['dividend'], headers=headers)
        dividends_record = dividends.record
        db.insert('dividend', dividends_record)
