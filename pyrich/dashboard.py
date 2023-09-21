import numpy as np
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from pyrich.stock import get_historical_price
from pyrich.style import style_table
from pyrich.style import style_neg_value
from pyrich.style import style_change
from pyrich.style import style_trade_type
from pyrich.table import sort_table
from pyrich.asset import Asset
from pyrich.portfolio import Portfolio
from pyrich.dividend import Dividend
from pyrich.cash import Cash
from pyrich.visualization import draw_line
from pyrich.visualization import draw_stock_chart
from pyrich.visualization import draw_pie
from pyrich.summary import portfolio_data
from pyrich.summary import current_portfolio
from pyrich.summary import total_realized_gain
from pyrich.summary import cash_data
from pyrich.summary import current_asset_data
from pyrich.summary import current_yield


st.set_page_config(
    page_title='Portfolio Manager',
    page_icon='🚀',
)
pd.set_option('styler.format.precision', 2)
pd.set_option('styler.format.thousands', ',')

# Loading main page
display_in_krw_currency = True
portfolio = Portfolio('transaction', display_in_krw_currency)

# Loding portfolio data
portfolio_data_ = portfolio_data(portfolio)
portfolio_table = portfolio_data_['portfolio_table']
portfolio_value = portfolio_data_['portfolio_value']

investment_by_country = portfolio.get_investment_by_country(portfolio_table)

cash = Cash('cash')
cash_table = cash.record
total_cash = cash_data(cash)
total_cash_value = total_cash.item()

asset = Asset('current_asset')
current_asset = asset.record
cur_asset_value = current_asset_data(
    portfolio_value['current_value'],
    total_cash_value,
)

# Sidebar component
with st.sidebar:
    # https://icons.getbootstrap.com/
    selected = option_menu(
        menu_title='Main Menu',
        options=[
            'Dashboard',
            'Portfolio',
            'My Asset',
            'Investment History',
            'Transaction History',
            'Dividends History',
            ], 
        icons=[
            'grid-fill',
            'easel2-fill',
            'pie-chart-fill',
            'archive-fill',
            'archive-fill',
            'currency-exchange',
            ],
        menu_icon='list',
        default_index=0
    )

if selected == 'Dashboard':
    st.subheader('Financial Summary')
    gain = portfolio_value['portfolio_gain']
    invested = portfolio_value['invested_amount']
    _yield = current_yield(gain, invested)
    gain_color = style_change(_yield)

    col1, col2 = st.columns([1, 2])
    with col1:
        cur_asset = st.container()
        cur_asset_value = portfolio_value['current_value'] + total_cash_value
        # Update current asset in the database
        asset.record_current_asset(cur_asset_value)
        cur_asset_text = ("<span>Current Asset Value</span>"
                          "<br>"
                          "<span style='font-weight: bold; font-size: 28px;'>"
                          f"{cur_asset_value:,.2f}원</span>")
        cur_asset.markdown(cur_asset_text, unsafe_allow_html=True)

        cur_investment = st.container()
        currency_conversion_applied = {
            True: '',
            False: '\ncurrency conversion not applied',
        }
        cur_investment_text = ("<span>Current Stock Value</span>"
                               "<br>"
                               "<span style='font-weight: bold; font-size: 28px;'>"
                               f"{portfolio_value['current_value']:,.2f}원</span>"
                               "<br>"
                               "<span style='"+gain_color+" font-size: 18px;'>"
                               f"&nbsp;{portfolio_value['portfolio_gain']:,.2f}원"
                               f"&nbsp;({_yield:,.2f} %)"
                               "<br>"
                               f"<span style='font-size: 12px; color: gray; font-style: italic;'>"
                               f"{currency_conversion_applied[display_in_krw_currency]}</span>"
                               "</span>")
        cur_investment.markdown(cur_investment_text, unsafe_allow_html=True)

        cur_cash = st.container()
        cur_cash_text = ("<span>Current Cash</span>"
                         "<br>"
                         "<span style='font-weight: bold; font-size: 28px;'>"
                         f"{total_cash_value:,.2f}원</span>")
        cur_cash.markdown(cur_cash_text, unsafe_allow_html=True)
    with col2:
        config = {'displayModeBar': False}
        trace_current_asset = draw_line(
            current_asset,
            x='date',
            y='amount',
            margin=dict(t=10, l=0, r=40, b=0),
            width=490,
            height=300,
            )
        st.plotly_chart(trace_current_asset, config=config)
elif selected == 'Portfolio':
    st.header('Portfolio')

    portfolio_section = st.container()
    portfolio_section.subheader('Current portfolio')
    portfolio_w_cash = portfolio.get_portfolio_w_cash(
        portfolio_table,
        total_cash_value,
    ).to_frame(name='Values in KRW')
    portfolio_chart = draw_pie(
        portfolio_w_cash,
        values=portfolio_w_cash['Values in KRW'],
        names=portfolio_w_cash.index,
        margin=None,
    )
    portfolio_section.plotly_chart(portfolio_chart)

    current_portfolio = current_portfolio(portfolio_table, display_in_krw_currency)
    value_subset = ['day_change(%)', 'pct_gain(%)']
    current_portfolio = sort_table(
        current_portfolio,
        by='pct_gain(%)',
        ascending=False,
    )
    styled_current_portfolio = style_table(
        current_portfolio,
        style_change,
        value_subset,
    )
    portfolio_section.dataframe(styled_current_portfolio)

    investment_section = st.container()
    investment_section.subheader('Investment')
    investment_section.markdown('#### Investment by Stock')

    current_investment_summary = portfolio.get_current_investment_summary(portfolio_table)
    current_investment_summary = sort_table(
        current_investment_summary,
        by='total_gain',
        ascending=False,
    )
    styled_current_investment_summary = style_table(
        current_investment_summary,
        style_change,
        ['total_gain'],
    )
    investment_section.dataframe(styled_current_investment_summary)

    selected = investment_section.selectbox('Choose Stock', portfolio_table.index)
    selected_stock_data = portfolio_table.loc[selected]
    change_color = style_change(selected_stock_data['day_change(%)'])
    stock_info_text = ("<p style='margin-left: 1.5em;'>"
                       "<span style='font-weight: bold; font-size: 26px;'>"
                       f"{selected_stock_data.name}</span>"
                       f"&nbsp<span>{selected_stock_data['current_price']:,.2f}</span>"
                       f"&nbsp;<span style='{change_color}'>"
                       f"({selected_stock_data['day_change(%)']}%)</span></p>")
    investment_section.markdown(stock_info_text, unsafe_allow_html=True)
    historical_price = get_historical_price(selected, selected_stock_data['country'])
    avg_price_paid = selected_stock_data['average_price_paid']
    stock_chart = draw_stock_chart(
        close=historical_price['Close'],
        average_price=avg_price_paid,
    )
    investment_section.plotly_chart(stock_chart)

    investment_section.markdown('#### Investment by Country')
    investment_chart = draw_pie(
        investment_by_country,
        values=investment_by_country['current_value'],
        names=investment_by_country.index,
        margin=None,
    )
    investment_section.plotly_chart(investment_chart)
    investment_by_country = sort_table(
        investment_by_country,
        by='total_gain',
        ascending=False,
    )
    styled_investment_by_country = style_table(
        investment_by_country,
        style_change,
        ['total_gain'],
    )
    investment_section.dataframe(styled_investment_by_country)

    cash_section = st.container()
    cash_section.subheader('Cash')
    cash_table = cash_table.set_index('currency')
    cash_table.drop(columns='id', inplace=True)
    cash_chart = draw_pie(
        cash_table,
        values=cash_table['amount'],
        names=cash_table.index,
        margin=None,
    )
    cash_section.plotly_chart(cash_chart)
    cash_section.dataframe(cash_table)
elif selected == 'My Asset':
    st.header('My Asset')
    st.subheader('Asset Ratio')

    # stock
    total_stock_value = pd.Series(
        portfolio_value['current_value'],
        index=['total_stock_value'],
        dtype=float,
    )

    # total asset
    asset_table = pd.concat([total_cash, total_stock_value])
    total_asset = asset_table.agg({'total_asset': np.sum})
    total_asset_table = pd.concat(
        [asset_table, total_asset]
    ).to_frame(name='Values in KRW')
    total_asset_table.index = [idx.upper() for idx in total_asset_table.index]

    asset_chart = draw_pie(
        asset_table,
        values=asset_table.array,
        names=asset_table.index,
        margin=None
    )
    st.plotly_chart(asset_chart)
    st.table(total_asset_table)
elif selected == 'Investment History':
    st.header('Investment History')
    realized_gain = portfolio.get_realized_gain()
    realized_gain = sort_table(realized_gain, by='realized_gain', ascending=False)

    st.subheader('Total Realized Gain')
    total_realized_gain_ = total_realized_gain(realized_gain)
    styled_total_realized_gain = style_table(
        total_realized_gain_,
        style_change,
        ['realized_gain'],
    )
    st.table(styled_total_realized_gain)

    st.subheader('Realized Gain by Stock')
    styled_realized_gain = style_table(
        realized_gain,
        style_change,
        ['realized_gain'],
    )
    st.table(styled_realized_gain)

    st.subheader('Realized Gain by Country')
    col_order = ['buy', 'sell', 'realized_gain', 'currency']
    realized_gain_by_country = (realized_gain.groupby(['country', 'currency'])
                                             .agg(np.sum)
                                             .reset_index('currency'))
    realized_gain_by_country = realized_gain_by_country[col_order]
    realized_gain_by_country = sort_table(
        realized_gain_by_country,
        by='realized_gain',
        ascending=False,
    )
    styled_realized_gain_by_country = style_table(
        realized_gain_by_country,
        style_change,
        ['realized_gain'],
    )
    st.table(styled_realized_gain_by_country)
elif selected == 'Transaction History':
    st.header('Transaction History')

    st.subheader('Total Transaction Amount')
    total_traded_amount = portfolio.get_total_traded_amount()
    total_traded_amount.index = [idx.upper() for idx in total_traded_amount.index]
    styled_total_traded_amount = style_table(
        total_traded_amount,
        style_neg_value,
        ['Values in KRW'],
    )
    st.table(styled_total_traded_amount)

    st.subheader('Transaction History')
    transaction_history = portfolio.record
    transaction_history.drop('id', axis=1, inplace=True)
    styled_transaction_history = style_table(
        transaction_history,
        style_trade_type,
        ['type'],
    )
    export_to_csv = transaction_history.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        'export to csv',
        export_to_csv,
        'transaction_history.csv',
        'text/csv',
    )
    st.dataframe(styled_transaction_history)

    st.subheader('Transaction History by Market')
    st.markdown('#### South Korea')
    kor_market = transaction_history[transaction_history['country']=='KOR']
    styled_kor_market = style_table(kor_market, style_trade_type, ['type'])
    st.dataframe(styled_kor_market)
    st.markdown('#### United States')
    us_market = transaction_history[transaction_history['country']=='USA']
    styled_us_market = style_table(us_market, style_trade_type, ['type'])
    st.dataframe(styled_us_market)
    st.markdown('#### Cryptocurrency')
    crypto = transaction_history[transaction_history['country']=='CRYPTO']
    styled_crypto = style_table(crypto, style_trade_type, ['type'])
    st.dataframe(styled_crypto)
elif selected == 'Dividends History':
    st.header('Dividends History')
    dividend = Dividend('dividend')
    dividend_history = dividend.record
    dividend_history.drop('id', axis=1, inplace=True)

    st.subheader('Total Dividends Received')
    total_dividends = dividend.get_total_dividends()
    total_dividends = {'Values in KRW': [total_dividends]}
    total_dividends_table = pd.DataFrame(total_dividends, index=['total_dividends'])
    total_dividends_table.index = [idx.upper() for idx in total_dividends_table.index]
    st.table(total_dividends_table)

    st.subheader('Total Dividends Received by Stock')
    dividends_by_stock = dividend.get_dividends_received_by_stock()
    st.table(dividends_by_stock)

    st.subheader('Dividends History')
    export_to_csv = dividend_history.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        'export to csv',
        export_to_csv,
        'dividend_history.csv',
        'text/csv',
    )
    st.dataframe(dividend_history)
