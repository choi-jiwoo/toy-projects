
from datetime import datetime
import pandas as pd

def to_html(keyword_rank: pd.DataFrame, now: datetime):
    content = '<html>\n<body>\n'
    content += f'<h3>무신사 스토어 {now} 검색어 랭킹</h3>\n'
    content += '''<table>\n<tr>\n<th>순위</th>\n<th>키워드</th>\n
    <th colspan="2">상승/감소</th>\n</tr>\n'''

    for i in range(len(keyword_rank)):
        content += '<tr>\n'
        content += f'<td>{str(keyword_rank.index[i])}</td>\n'
        content += f'<td>{str(keyword_rank["Item"].iloc[i])}</td>\n'
        content += f'<td>{str(keyword_rank["Status"].iloc[i])}</td>\n'
        content += f'<td>{str(keyword_rank["Change"].iloc[i])}</td>\n'
        content += '</tr>\n'

    content += '</table>\n</body>\n</html>'
    return content