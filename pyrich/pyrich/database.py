from collections.abc import Iterable
import csv
from dotenv import load_dotenv
import os
import pandas as pd
import psycopg2
from urllib.parse import urlparse
from pyrich.error import ArrayLengthDoesNotMatchError


class PostgreSQL:

    load_dotenv()
    DATABASE_URL = os.environ.get('DATABASE_URL')

    def __init__(self) -> None:
        self._parse_database_url()
        self._connect()
        self._create_current_asset_table()
        self._create_cash_table()
        self._create_transaction_table()
        self._create_dividend_table()

    def _parse_database_url(self) -> None:
        connection_info = urlparse(PostgreSQL.DATABASE_URL)
        self.dbname = connection_info.path.lstrip('/')
        self.user = connection_info.username
        self.password = connection_info.password
        self.host = connection_info.hostname
        self.port = connection_info.port

    def _connect(self) -> None:
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            self.cur = self.conn.cursor()
        except psycopg2.OperationalError:
            raise

    def run_query(self, query: str, values: Iterable = None,
                  msg: bool = False) -> None:
        try:
            self.cur.execute(query, values)
            self.conn.commit()
            if msg:
                print('Query ran successfully.')
        except psycopg2.ProgrammingError:
            raise

    def _check_empty_table(self, table: str) -> bool:
        query = f'SELECT COUNT(*) FROM {table}'
        self.run_query(query)
        row_count = self.cur.fetchone()[0]
        is_empty = True if row_count == 0 else False
        return is_empty

    def _create_current_asset_table(self) -> None:
        query = ('CREATE TABLE IF NOT EXISTS current_asset'
                 '(id serial PRIMARY KEY,'
                 'date DATE NOT NULL,'
                 'amount REAL NOT NULL);')
        self.run_query(query)

    def _create_cash_table(self) -> None:
        cash_table = 'cash'
        query = ('CREATE TABLE IF NOT EXISTS cash'
                 '(id serial PRIMARY KEY,'
                 'amount REAL NOT NULL,'
                 'currency VARCHAR(5) NOT NULL);')
        self.run_query(query)
        default_cash = {
            'default_krw_amount': {
                'amount': 0,
                'currency': 'KRW',
            },
            'default_usd_amount': {
                'amount': 0,
                'currency': 'USD',
            }
        }
        is_empty = self._check_empty_table(cash_table)
        if is_empty:
            for item in default_cash.values():
                self.insert(cash_table, item, msg=False)

    def _create_transaction_table(self) -> None:
        query = ('CREATE TABLE IF NOT EXISTS transaction'
                 '(id serial PRIMARY KEY,'
                 'date DATE NOT NULL,'
                 'country VARCHAR(10) NOT NULL,'
                 'symbol VARCHAR(15) NOT NULL,'
                 'type VARCHAR(5) NOT NULL,'
                 'quantity REAL NOT NULL,'
                 'price REAL NOT NULL,'
                 'total_price_paid REAL NOT NULL,'
                 'total_price_paid_in_krw REAL NOT NULL);')
        self.run_query(query)

    def _create_dividend_table(self) -> None:
        query = ('CREATE TABLE IF NOT EXISTS dividend'
                 '(id serial PRIMARY KEY,'
                 'date DATE NOT NULL,'
                 'symbol VARCHAR(15) NOT NULL,'
                 'dividend REAL NOT NULL,'
                 'currency VARCHAR(3) NOT NULL);')
        self.run_query(query)

    def copy_from_csv(self, table: str, msg: bool = True) -> None:
        path = f'./{table}.csv'
        abs_path = os.path.abspath(path)
        with open(abs_path, 'r', encoding='utf-8-sig') as f:
            header = csv.reader(f)
            header = next(header)
            self.cur.copy_from(
                f,
                table,
                sep=',',
                columns=header,
            )

    def _get_column_name(self, table: str) -> list:
        try:
            query = f'SELECT * FROM {table} LIMIT 0;'
            self.run_query(query)
            col_name = [desc[0] for desc in self.cur.description]
        except Exception as e:
            print(e)
        finally:
            return col_name

    def show_table(self, table: str, msg: bool = False) -> pd.DataFrame:
        try:
            col_name = self._get_column_name(table)
            query = f'SELECT * FROM {table} ORDER BY id;'
            self.run_query(query, msg=msg)
            result = self.cur.fetchall()
            rows = []
            for item in result:
                rows.append(item)
        except Exception as e:
            print(e)
        finally:
            table = pd.DataFrame(rows, columns=col_name)
            return table

    def insert(self, table: str, record: dict, msg: bool = True) -> None:
        keys = list(record.keys())
        values = list(record.values())
        column = ', '.join(keys)
        value_seq = ['%s' for i in range(len(values))]
        placeholders = ', '.join(value_seq)
        query = (f"INSERT INTO {table} ({column}) "
                 f"VALUES ({placeholders});")
        self.run_query(query, values, msg=msg)

    def update(self, table: str, column: list,
               value: list, _id: int, msg: bool = True) -> None:
        col_len = len(column)
        val_len = len(value)
        if col_len != val_len:
            msg = 'column length does not match value length.'
            raise ArrayLengthDoesNotMatchError(msg)

        set_clause_holder = []
        for i in column:
            item = f'{i}=%s'
            set_clause_holder.append(item)
        set_clause = ', '.join(set_clause_holder)
        query = f'UPDATE {table} SET {set_clause} WHERE id=%s;'
        value.append(_id)
        self.run_query(query, value, msg=msg)

    def delete_rows(self, table: str, all_rows: bool = False,
                    msg: bool = True) -> None:
        if all_rows:
            query = f'DELETE FROM {table};'
            reset_sequence_query = f"ALTER SEQUENCE {table}_id_seq RESTART;"
            warning_msg = input('Deleting all rows in the table. Continue? (Y/n): ')
        else:
            query = f'DELETE FROM {table} WHERE id=(SELECT MAX(id) FROM {table});'
            reset_sequence_query = (f"SELECT SETVAL('{table}_id_seq', "
                                    f"(SELECT MAX(id) FROM {table}));")
            warning_msg = input('Deleting the last row. Continue? (Y/n): ')

        if warning_msg.upper() == 'Y':
            self.run_query(query, msg=msg)
            self.run_query(reset_sequence_query)
        else:
            print('Deleting stopped.')
        
    def __del__(self) -> None:
        self.cur.close()
        self.conn.commit()
        self.conn.close()

    def __repr__(self) -> str:
        return f"PostgreSQL(database_url='{PostgreSQL.DATABASE_URL}')"
