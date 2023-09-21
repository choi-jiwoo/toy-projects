from datetime import datetime
from bs4 import BeautifulSoup as bs
import re
import requests
import pandas as pd

class MusinsaRanking:

    def __init__(self, url: str) -> None:
        self.url = url

    def _get_request(self) -> requests.Response:
        res = requests.get(self.url)
        if res.status_code != 200:
            res.raise_for_status()
        return res

    def get_ranking(self) -> pd.DataFrame:
        res = self._get_request()
        data = res.text
        soup = bs(data, 'html.parser')
        ranking_section = soup.find(class_='tbl_box_sranking')

        # 키워드 부분
        item_html = ranking_section.find_all('a')
        # 순위 변동 방향 부분
        status_html = ranking_section.find_all(class_='arrow')
        # 순위 변동 부분
        chng_html = ranking_section.find_all(class_='p_srank_last')

        item = []
        status = []
        change = []

        for i in range(len(status_html)):
            item_name = item_html[i].attrs['title']
            item.append(item_name)
            change_direction = status_html[i].get_text()
            status.append(change_direction)
            status_change = chng_html[i].get_text()
            change_num = re.sub(r'[^0-9]', '', status_change)
            change.append(change_num)

        item_mapping = list(zip(item, status, change))
        ranking = pd.DataFrame(item_mapping,
                               columns=['Item', 'Status', 'Change'])
        return ranking
