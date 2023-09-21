import pandas as pd
from functools import cached_property
from typing import List
from pyrich.database import PostgreSQL
from pyrich import forex


class TransactionRecord:

    def __init__(self, table: str) -> None:
        self.table = table
        self.db = PostgreSQL()

    @cached_property
    def record(self) -> pd.DataFrame:
        return self.db.show_table(self.table)

    @property
    def usd_to_krw(self) -> float:
        return forex.get_usd_to_krw()

    @staticmethod
    def map_currency(currency_indicator: pd.Series,
                     display_krw: bool = False) -> List[str]:
        currency_mapping = {
            'CRYPTO': 'KRW',
            'KOR': 'KRW',
            'USA': 'USD',
        }
        if display_krw:
            currency_mapping['USA'] = 'KRW'

        currency_map = [
            currency_mapping[country]
            for country
            in currency_indicator
        ]
        return currency_map

    def __repr__(self) -> str:
        return f"Record(table='{self.table}')"
