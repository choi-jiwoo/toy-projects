import finnhub
import os
from dotenv import load_dotenv


def set_finnhub():
    load_dotenv()
    api_key = os.environ.get('FINNHUB_API_KEY')
    finnhub_client = finnhub.Client(api_key=api_key)
    return finnhub_client