import pandas as pd
import numpy as np
from pyrich.record import TransactionRecord


class Dividend(TransactionRecord):

    def __init__(self, table: str) -> None:
        super().__init__(table)

    def get_dividends_received_by_stock(self) -> pd.DataFrame:
        stock_group = self.record.groupby('symbol')
        dividends_by_stock = stock_group.agg(
            {
                'dividend': np.sum,
                'currency': lambda x: x.unique().item(),
            }
        )
        return dividends_by_stock

    def _get_dividends_by_currency(self, dividends: pd.DataFrame,
                                   currency: str='USD') -> pd.Series:
        dividends_table = dividends.get_group(currency)
        dividends_by_currency = dividends_table.agg(
            {
                'dividend': np.sum,
            }
        )
        if currency == 'USD':
            dividends_by_currency *= self.usd_to_krw
        return dividends_by_currency

    def get_total_dividends(self) -> pd.Series:
        currency_group = self.record.groupby('currency')
        existing_currency = currency_group.groups.keys()
        total_dividends = [
            self._get_dividends_by_currency(currency_group, currency)
            for currency
            in list(existing_currency)
        ]
        total_dividends = np.sum(total_dividends)
        return total_dividends

    def __repr__(self) -> str:
        return f"Dividend(table='{self.table}')"
