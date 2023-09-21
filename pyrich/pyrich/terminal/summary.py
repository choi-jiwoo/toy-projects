import pandas as pd
from datetime import datetime
from functools import wraps
from typing import Optional
from typing import List
from pyrich.portfolio import Portfolio
from pyrich.cash import Cash
from pyrich.asset import Asset
from pyrich.summary import PortfolioType
from pyrich.summary import portfolio_data
from pyrich.summary import cash_data
from pyrich.summary import current_asset_data
from pyrich.summary import current_yield
from pyrich.style import style_terminal_text
from pyrich.style import style_change


SIGN_COLOR = {
    'green': '+',
    'red': '',
    'none': '',
}
TRANSACTION_TABLE = 'transaction'
CASH_TABLE = 'cash'
ASSET_TABLE = 'current_asset'

def style_print(color: Optional[str] = None, style: Optional[str] = None):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            text = func(*args, **kwargs)
            styled_text = style_terminal_text(
                text=text,
                color=color,
                style=style,
            )
            return styled_text
        return wrapper
    return decorate

def attach_arrow(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        text = func(*args, **kwargs)
        text = text + " " + "▸"
        return text
    return wrapper

@style_print(color='magenta', style='bold')
def timestamp(date_format: str) -> str:
    today = datetime.today()
    today_string = today.strftime(date_format)
    text = f"\n{today_string}\n"
    return text

@style_print(style='bold')
def header(text: str, style: Optional[str] = None) -> str:
    if style is None:
        return text

    if style == 'uppercase':
        return text.upper()
    elif style == 'title':
        return text.title()
    else:
        print(f"'{style}' is not available.")

@attach_arrow
@style_print(color='green', style='bold')
def component(component_text: str, indent_left: int = 0) -> str:
    component_text = component_text.upper()
    text = f"{component_text:<{indent_left}}"
    return text

def change(gain: float, yield_: float):
    color = style_change(yield_, 'terminal')
    sign = SIGN_COLOR[color]
    @style_print(color=color)
    def change_text():
        text = f"{gain:,.2f} ({sign}{yield_:,.2f} %)"
        return text
    return change_text()


class Financial:

    @property
    def portfolio(self) -> Portfolio:
        return Portfolio(TRANSACTION_TABLE)

    @property
    def cash(self) -> Cash:
        return Cash(CASH_TABLE)

    @property
    def asset(self) -> ASSET_TABLE:
        return Asset(ASSET_TABLE)

    @property
    def portfolio_data_(self) -> PortfolioType:
        return portfolio_data(self.portfolio)

    @property
    def portfolio_table(self) -> pd.DataFrame:
        table = self.portfolio_data_['portfolio_table']
        table = table.reset_index('symbol')
        return table

    @property
    def portfolio_value(self) -> pd.DataFrame:
        return self.portfolio_data_['portfolio_value']
    
    @property
    def total_cash(self) -> pd.DataFrame:
        return cash_data(self.cash).item()

    @property
    def cur_asset_value(self) -> float:
        return current_asset_data(self.portfolio_value['current_value'],
                                  self.total_cash)

    @property
    def stock_list(self) -> List[List[str]]:
        stock_list_ = self.portfolio_table[
                [
                    'symbol',
                    'current_value',
                    'invested_amount'
                ]
            ]
        return stock_list_.values

    @property
    def gain(self) -> float:
        return self.portfolio_value['portfolio_gain']

    @property
    def current_value(self) -> float:
        return self.portfolio_value['current_value']

    @property
    def invested(self) -> float:
        return self.portfolio_value['invested_amount']

    @property
    def yield_(self) -> float:
        return current_yield(self.gain, self.invested)
