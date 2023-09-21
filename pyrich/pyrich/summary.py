from copy import deepcopy
import pandas as pd
from typing import TypedDict
from pyrich.portfolio import Portfolio
from pyrich.cash import Cash
from pyrich.record import TransactionRecord


class PortfolioType(TypedDict):
    portfolio_table: pd.DataFrame
    portfolio_value: pd.DataFrame


def portfolio_data(portfolio: Portfolio) -> PortfolioType:
    portfolio_table = portfolio.current_portfolio()
    portfolio_value = portfolio.get_current_portfolio_value(portfolio_table)
    portfolio = {
        'portfolio_table': portfolio_table,
        'portfolio_value': portfolio_value,
    }
    return portfolio

def current_portfolio(portfolio_table: pd.DataFrame,
                      display_krw: bool) -> pd.DataFrame:
    drop_col = ['current_value', 'invested_amount', 'total_gain']
    portfolio = portfolio_table.drop(drop_col, axis=1)
    if display_krw:
        portfolio['currency'] = TransactionRecord.map_currency(portfolio['country'])
    return portfolio

def total_realized_gain(realized_gain_table: pd.DataFrame) -> pd.DataFrame:
    realized_gain_table = deepcopy(realized_gain_table)
    currency_grp = realized_gain_table.groupby('currency')
    sum_by_currency = currency_grp.sum()
    total_realized_gain_ = sum_by_currency['realized_gain'].to_frame()
    return total_realized_gain_

def cash_data(current_cash: Cash) -> pd.Series:
    total_cash = current_cash.get_total_cash_in_krw()
    return total_cash

def current_asset_data(current_stock_value: float, current_cash: float) -> float:
    cur_asset_value = current_stock_value + current_cash
    return cur_asset_value

def current_yield(gain: float, invested: float) -> float:
    return (gain / invested) * 100
