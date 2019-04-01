IIJトラフィック取得ツール
=========

目的
---------------

本ツールは、IIJ社が提供するIIJサービスオンラインより、インターネット接続サービスのトラフィック情報を取得するためのツールです。

PythonにてIIJサービスオンラインに自動ログインし、対象トラフィックのPNG/CSVをダウンロードします。
  
事前準備
---------------

ツールを実行する前に下記の設定ファイルに必要事項を記入してください

login.json  

| Left align | Right align |
|:-----------|:------------|
| baseurl    | 必須。IIJサービスオンラインのURL。通常https://help.iij.ad.jp/ |
| username   | 必須。IIJサービスオンラインのユーザID |
| userpass   | 必須。IIJサービスオンラインのユーザパスワード |

node.json

| Left align | Right align |
|:-----------|:------------|
| servicecode   | 必須。トラフィック取得対象のインターネット接続サービスが所属するサービスコード |
| customercode  | 必須。トラフィック取得対象のインターネット接続サービスのカスタマーコード |
| bandwidth     | 必須。トラフィック取得対象のインターネット接続サービスの契約帯域 |

proxy.json

| Left align | Right align |
|:-----------|:------------|
| PROXY_HOST | 必須。プロキシのURL |
| PROXY_PORT | 必須。プロキシのポート |
| PROXY_USER | 必須。プロキシ認証のユーザID |
| PROXY_PASS | 必須。プロキシ認証のユーザパスワード |

データ取得
---------------

コマンドラインより下記の通りツールを起動してください。
`[START_DATE]`と`[END_DATE]`は、YYYY/MM/DD形式で取得開始日と取得終了日を指定してください。

```sh
$ python main.py -h
usage: iij.py [-h] --start_date [START_DATE] --end_date [END_DATE] [--proxy]

get IIJ Service Online graph download as csv and png

optional arguments:
  -h, --help            show this help message and exit
  --start_date [START_DATE]
                        specify a start date of data. Style: YYYY/MM/DD
  --end_date [END_DATE]
                        specify a end date of data. Style: YYYY/MM/DD
  --proxy               Enable proxy option. Attention: you must set
                        proxy.json as proxy infomation
```

プロキシを通す場合は、`--proxy`オプション付きで実行

```sh
$python main.py --start_date [START_DATE] --end_date [END_DATE] --proxy
```

動作環境
---------------

ツールの実行にあたり下記のインストールが必要です

* Python3
* Selenium
* Chromedriver
* Requests
