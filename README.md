# 株とPythonでお金儲けを目指す本 ソースコード

サークル電脳律速が頒布している同人誌「株とでお金儲けを目指す本　はじめのいっぽ編」に登場するソースコードです。

## 同人誌「株とでお金儲けを目指す本　はじめのいっぽ編」について

下記URLを参照願います。  
http://d-rissoku.net/サークルサポート/株とpythonでお金儲けを目指す本-はじめのいっぽ編/

PDF版をBOOTHにて販売中です。  
https://d-rissoku.booth.pm/items/827638

## 同人誌内のコードと GitHub 上のコードの差異

### 株探(Kabutan.jp)の変更に対応

株探(Kabutan.jp)のページ内容（HTMLデータ内容)が同人誌執筆時から変更されたため、
同人誌内の次のコードがそのままでは動作しません。GitHubのコードは2018/12/23 21:00時点で動作を確認していますので、そちらを参考にしてください。

| 同人誌内の動作不可コード | GitHubのコード（動作確認済) |
|------------------------|---------------------------|
| p.14 7203（トヨタ自動車）の業種コードを取得するサンプル | https://github.com/BOSUKE/stock_and_python_1st/blob/master/chapter2/pyquery_sample.py |
| p.18 コード2.1 銘柄情報を取得しSQLite に格納する | https://github.com/BOSUKE/stock_and_python_1st/blob/master/chapter2/get_brands.py |
