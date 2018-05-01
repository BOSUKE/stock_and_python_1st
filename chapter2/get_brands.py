# -*- coding: utf-8 -*-
from pyquery import PyQuery
import time
import sqlite3


def get_brand(code):
  url = 'https://kabutan.jp/stock/?code={}'.format(code)

  q = PyQuery(url)

  if len(q.find('.stock_st_table')) == 0:
    return None

  try:
    name = q.find('#kobetsu_right > h4')[0].text
    short_name = q.find('td.kobetsu_data_table1_meigara')[0].text
    market = q.find('td.kobetsu_data_table1_meigara + td')[0].text
    unit_str = q.find('.stock_st_table:eq(1) > tr:eq(5) > td.tar:eq(0)')[0].text
    unit = int(unit_str.split()[0].replace(',', ''))
    sector = q.find('.kobetsu_data_table2 a')[0].text
  except ValueError:
    return None

  return code, name, short_name, market, unit, sector

def brands_generator(code_range):
  for code in code_range:
    brand = get_brand(code)
    if brand:
      yield brand
    time.sleep(1)

def insert_brands_to_db(db_file_name, code_range):
  conn = sqlite3.connect(db_file_name)
  with conn:
    sql = 'INSERT INTO brands(code,name,short_name,market,unit,sector) ' \
          'VALUES(?,?,?,?,?,?)'
    conn.executemany(sql, brands_generator(code_range))
