import pandas as pd
from typing import Callable
from typing import Optional
from pyrich.error import UnknownFormat


BLACK = '#000000'
GREEN = '#137333'
RED = '#a50e0e'

def style_table(table: pd.DataFrame, style: Callable[[float], str],
                subset: list, **kwargs) -> pd.DataFrame:
    styled_table = table.style.applymap(style, subset=subset, **kwargs)
    return styled_table

def style_neg_value(value: float) -> str:
    return f'color:{RED};' if value < 0 else None

def style_change(value: float, _format: str='html') -> str:
    color = {
        'zero': {
            'html': BLACK,
            'terminal': 'none',
        },
        'neg': {
            'html': RED,
            'terminal': 'red',
        },
        'pos': {
            'html': GREEN,
            'terminal': 'green',
        },
    }
    if value > 0:
        style = 'pos'
    elif value < 0:
        style = 'neg'
    else:
        style = 'zero'

    if _format == 'html':
        return f"color:{color[style]['html']};"
    elif _format == 'terminal':
        return color[style]['terminal']
    else:
        error_msg = (f"Given format '{_format}' is not supported. Try either"
                     "'html' or 'terminal'.")
        raise UnknownFormat(error_msg)

def style_trade_type(_type: str) -> str:
    color = {
        'buy': GREEN,
        'sell': RED,
    } 
    if _type == 'buy':
        style = f"color:{color['buy']};"
    elif _type == 'sell':
        style = f"color:{color['sell']};"
    return style

def style_terminal_text(text, color: Optional[str]=None,
                        style: Optional[str]=None) -> str:
    ansi_styles = {
        None: '',
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'none': '\033[39m',  # reset
        'end': '\033[0m',  # reset all
        'bold': '\033[1m',
    }
    styled_text = (f"{ansi_styles[style]}{ansi_styles[color]}{text}"
                   f"{ansi_styles['end']}")
    return styled_text
