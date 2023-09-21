import argparse


def set_args():
    description = ("Hello👋🏼 I'm pyrich!\n\n"
                   "Here are some guidelines to inputting specific arguments.\n"
                   "DATE: YYYY-MM-DD\n"
                   "COUNTRY: Three letter country code. Alpha-3 code (ISO 3166) (e.g. USA, KOR)\n"
                   "TYPE: Either 'buy' or 'sell'")
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-s',
        '--summary',
        action='store_true',
        default=False,
        help='Show current porfolio summary.'
    )
    parser.add_argument(
        '-t',
        '--transaction',
        type=str,
        nargs=6,
        metavar=('DATE', 'COUNTRY', 'TYPE', 'SYMBOL', 'QUANTITY', 'PRICE'),
        default=False,
        help='Record transaction'
    )
    parser.add_argument(
        '-d',
        '--dividend',
        type=str,
        nargs=4,
        metavar=('DATE', 'SYMBOL', 'AMOUNT', 'CURRENCY'),
        default=False,
        help='Record dividends received'
    )
    parser.add_argument(
        '--csv',
        type=str,
        metavar='CSV_FILENAME',
        default=False,
        help=('Csv filename to copy data from. Filename should match with '
              'database table name. The file should be located '
              'in the root directory of the package')
    )
    parser.add_argument(
        '--show',
        type=str,
        metavar='TABLE_NAME',
        default=False,
        help='Table name to display'
    )
    parser.add_argument(
        '--deletelast',
        type=str,
        metavar='TABLE_NAME',
        default=False,
        help='Table name to delete the last row'
    )
    parser.add_argument(
        '--deleteall',
        type=str,
        metavar='TABLE_NAME',
        default=False,
        help='Table name to delete all rows'
    )
    parser.add_argument(
        '--cash',
        metavar=('CURRENT_CASH', 'CURRENCY'),
        nargs=2,
        default=False,
        help='Update current cash'
    )
    parser.add_argument(
        '-w',
        '--web',
        action='store_true',
        help='Open streamlit dashboard in a web browser'
    )
    parser.add_argument(
        '-p',
        '--price',
        type=str,
        metavar=('SYMBOL', 'COUNTRY'),
        nargs=2,
        default=False,
        help='Get current price of a stock'
    )
    return parser
