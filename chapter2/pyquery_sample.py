# -*- coding: utf-8 -*-
from pyquery import PyQuery

q = PyQuery('https://kabutan.jp/stock/?code=7203')
sector = q.find('table.kobetsu_data_table2 a')[0].text
print(sector)
