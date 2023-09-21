from collections import deque
from functools import lru_cache
import pandas as pd
import numpy as np
from pyrich.record import TransactionRecord
from pyrich import stock


class Portfolio(TransactionRecord):

    def __init__(self, table: str, display_krw: bool = True) -> None:
        super().__init__(table)
        self.display_krw = display_krw

    def _get_pivot_table(self, column: str,
                         remove_na: bool=False) -> pd.DataFrame:
        record_pivot_table = pd.pivot_table(
            self.record,
            values=column,
            index=['country', 'symbol'],
            columns='type',
            aggfunc=np.sum
        )
        if remove_na:
            record_pivot_table.fillna(0, inplace=True)
        return record_pivot_table

    @lru_cache
    def _get_current_stock(self) -> pd.DataFrame:
        stock_ = self._get_pivot_table('quantity', remove_na=True)
        stock_['quantity'] = stock_['buy'] - stock_['sell']
        return stock_

    @lru_cache
    def _get_trades(self) -> pd.DataFrame:
        trades = self._get_pivot_table('total_price_paid')
        if self.display_krw:
            total_price_paid_in_krw = 'total_price_paid_in_krw'
            us_transaction = self.record[self.record['country']=='USA']
            us_record_pivot_table = pd.pivot_table(
                us_transaction,
                values=total_price_paid_in_krw,
                index=['country','symbol'],
                columns='type',
                aggfunc=np.sum
            )
            trades.loc['USA'] = us_record_pivot_table
        return trades
    
    def _get_average_price_paid(self, symbol: str) -> float:
        symbol_transaction = self.record[self.record['symbol']==symbol]
        symbol_transaction = symbol_transaction[['type', 'quantity', 'price']]
        transactions = deque()
        for i in symbol_transaction.values:
            transaction_type = i[0]
            quantity = i[1]
            price = i[2]
            while quantity > 0:
                if transaction_type == 'buy':
                    transactions.append(price)
                else:
                    transactions.popleft()
                quantity -= 1
        transactions = np.array(transactions)
        try:
            average_price_paid = transactions.mean()
        except Exception:
            average_price_paid = 0
        finally:
            return average_price_paid

    def _get_portfolio_average_price(self, portfolio: pd.DataFrame) -> pd.Series:
        average_price_paid = {
            symbol: self._get_average_price_paid(symbol)
            for symbol
            in portfolio.index
        }
        average_price_paid = pd.Series(
            average_price_paid,
            name='average_price_paid'
        )
        return average_price_paid

    def _get_stock_quote(self, portfolio: pd.DataFrame) -> pd.DataFrame:
        portfolio_stock_price = []

        for symbol in portfolio.index:
            country = portfolio.loc[symbol, 'country']
            current_stock_data = stock.get_current_price(symbol, country)
            portfolio_stock_price.append(current_stock_data)

        day_change = pd.DataFrame(portfolio_stock_price)
        day_change['dp'] = day_change['dp'].apply(round, args=(2,))
        col_name = ['current_price', 'day_change', 'pct_change(%)']
        day_change.columns = col_name
        day_change.index = portfolio.index
        current_portfolio = portfolio.join(day_change)
        return current_portfolio

    def _get_gain(self, current_portfolio: pd.DataFrame) -> tuple:
        price_data = current_portfolio[['current_value', 'invested_amount']]
        total_gain = price_data.agg(lambda x: x[0]-x[1], axis=1)
        pct_gain = price_data.agg(lambda x: (x[0]-x[1])/x[1], axis=1)
        pct_gain *= 100
        pct_gain = round(pct_gain, 2)
        return total_gain, pct_gain

    def _get_current_stock_value(
        self,
        current_portfolio: pd.DataFrame
    ) -> pd.Series:
        investment = current_portfolio[['quantity', 'current_price']]
        current_stock_value = investment.agg(np.prod, axis=1)
        if self.display_krw:
            current_stock_value *= self.usd_to_krw
        return current_stock_value

    def current_portfolio(self) -> pd.DataFrame:
        quantity = self._get_current_stock()
        trades = self._get_trades()
        transaction_summary = trades.join(quantity['quantity'])
        
        quantity_gt_zero = transaction_summary['quantity'] > 0
        currently_owned_stock = transaction_summary[quantity_gt_zero]
        currently_owned_stock = currently_owned_stock.fillna(0)
        invested_amt = currently_owned_stock['buy'] - currently_owned_stock['sell']
        currently_owned_stock['invested_amount'] = invested_amt
        currently_owned_stock.drop(['buy', 'sell'], axis=1, inplace=True)
        
        portfolio = pd.DataFrame(currently_owned_stock)
        portfolio.reset_index('country', inplace=True)
        portfolio_average_price = self._get_portfolio_average_price(portfolio)
        portfolio = portfolio.join(portfolio_average_price)
        portfolio['currency'] = TransactionRecord.map_currency(
            portfolio['country'],
            self.display_krw,
        )

        current_portfolio = self._get_stock_quote(portfolio)
        current_stock_value = self._get_current_stock_value(current_portfolio)
        current_portfolio['current_value'] = current_stock_value
        total_gain, pct_gain = self._get_gain(current_portfolio)
        current_portfolio['total_gain'] = total_gain
        current_portfolio['pct_gain(%)'] = pct_gain

        col_order = [
            'country',
            'quantity',
            'pct_change(%)',
            'current_price',
            'average_price_paid',
            'pct_gain(%)',
            'current_value',
            'invested_amount',
            'total_gain',
            'currency',
        ]
        current_portfolio = current_portfolio[col_order]
        return current_portfolio
    
    def get_current_investment_summary(
        self,
        current_portfolio: pd.DataFrame
    ) -> pd.DataFrame:
        use_col = [
            'country',
            'invested_amount',
            'current_value',
            'total_gain',
            'currency',
        ]
        current_investment_summary = current_portfolio[use_col]
        return current_investment_summary

    def get_investment_by_country(
        self,
        current_portfolio: pd.DataFrame
    ) -> pd.DataFrame:
        use_col = ['country', 'invested_amount', 'current_value', 'total_gain']
        investment_table = current_portfolio[use_col]
        country_group = investment_table.groupby('country')
        investment_by_country = country_group.agg(np.sum)
        investment_by_country['currency'] = TransactionRecord.map_currency(
            investment_by_country.index,
            self.display_krw,
        )
        return investment_by_country

    def get_current_portfolio_value(
        self,
        current_portfolio: pd.DataFrame
    ) -> pd.Series:
        portfolio_copy = current_portfolio.copy(deep=True)
        currency_group = portfolio_copy.groupby('currency')
        if not self.display_krw:
            usd_group_stock = currency_group.groups['USD']
            cols_in_usd = [
                'current_price',
                'average_price_paid',
                'current_value',
                'invested_amount',
                'total_gain',
            ]
            portfolio_copy.loc[usd_group_stock, cols_in_usd] *= self.usd_to_krw
        portfolio_copy.loc[:, 'currency'] = 'KRW'
        portfolio_value = portfolio_copy.agg(
            {
                'current_value': np.sum,
                'invested_amount': np.sum,
            }
        )
        portfolio_value['portfolio_gain'] = portfolio_value.agg(
            lambda x: np.subtract(x[0], x[1])
        )
        return portfolio_value

    def get_realized_gain(self) -> pd.DataFrame:
        quantity = self._get_current_stock()
        past_owned = quantity[quantity['quantity'] == 0]
        past_owned = past_owned.reset_index('country').index
        trades = self._get_trades()
        trades = trades.reset_index('country').loc[past_owned]
        trades['realized_gain'] = trades['sell'] - trades['buy']
        trades['currency'] = TransactionRecord.map_currency(
            trades['country'],
            self.display_krw,
        )
        return trades

    def get_total_traded_amount(self) -> pd.DataFrame:
        trades = self._get_trades()
        trades_sum = trades.groupby('country').agg(np.sum)
        if not self.display_krw:
            trades_sum.loc['USA'] *= self.usd_to_krw
        trades_sum = trades_sum.sum()
        trades_sum['net'] = trades_sum['sell'] - trades_sum['buy']
        trades_sum = trades_sum.to_frame(name='Values in KRW')
        return trades_sum

    def get_portfolio_w_cash(self, current_portfolio:
                             pd.DataFrame, cash: float) -> pd.DataFrame:
        use_col = ['current_value', 'currency']
        portfolio_component = current_portfolio[use_col]
        cash = pd.Series(cash, index=['CASH'])
        try:
            us_stock = portfolio_component.groupby('currency').get_group('USD')
            stock_list = us_stock['current_value']
            if not self.display_krw:
                stock_list *= self.usd_to_krw
        except KeyError:
            stock_list = portfolio_component['current_value']
        finally:
            portfolio_w_cash = pd.concat([stock_list, cash])
            return portfolio_w_cash

    def __repr__(self) -> str:
        return f"Portfolio(table='{self.table}')"
