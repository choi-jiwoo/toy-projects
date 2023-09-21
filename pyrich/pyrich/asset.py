from datetime import date
import pandas as pd
from pyrich.record import TransactionRecord


class Asset(TransactionRecord):

    def __init__(self, table: str) -> None:
        super().__init__(table)

    def record_current_asset(self, current_asset: float) -> None:
        table = 'current_asset'
        query = (f'SELECT date FROM {table} '
                 f'WHERE id=(SELECT MAX(id) FROM {table});')
        self.db.run_query(query)
        date_format = '%Y-%m-%d'
        today = date.today()
        timestamp = today.strftime(date_format)
        record = {
            'date': timestamp,
            'amount': current_asset,
        }
        try:
            latest_date = self.db.cur.fetchone()[0]
        except TypeError:
            self.db.insert(table, record, msg=False)
        else:
            if today > latest_date:
                self.db.insert(table, record, msg=False)

    def __repr__(self) -> str:
        return f"Asset(table='{self.table}')"
