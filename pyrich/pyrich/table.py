import pandas as pd


def sort_table(table: pd.DataFrame, **kwargs) -> pd.DataFrame:
    return table.sort_values(**kwargs)
