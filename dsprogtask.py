import time
import json
import requests
import csv
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# アクセスしたいWebサイトのURL
url = 'https://www.musashino-u.ac.jp'
domain = urlparse(url).netloc
print(domain)

# URLを保存する集合
urls = {url}

# 訪問済みURLを保存する集合
visited = set()

# URLとタイトルを保存する辞書
site_map = {}

while urls:
    # URLを1つ取り出す
    current_url = urls.pop()

    # すでに訪問済みならスキップ
    if current_url in visited:
        continue

    # 訪問済みに登録
    visited.add(current_url)

    # サーバーにアクセスする
    time.sleep(1)
    try:
        response = requests.get(current_url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f'接続エラー：{current_url} / {e}')
        continue

    # HTML以外のファイルはスキップする
    if 'text/html' not in response.headers.get('Content-Type', ''):
        continue

    # HTMLを解析する
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # タイトルを取得する
    if soup.title:
        title = soup.title.text.strip()
    else:
        title = ''

     # 辞書に保存する
    site_map[current_url] = title

    # 100ページ取得するごとにCSVを保存する
    if len(site_map) % 100 == 0:
        with open('sitemap.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title'])

            for page_url, page_title in site_map.items():
                writer.writerow([page_url, page_title])

        print(f'途中保存完了：{len(site_map)}ページ')

    print(f'取得ページ数：{len(site_map)} | {title} | {current_url}', flush=True)

    # ページ内のリンクを取得する
    links = soup.find_all('a')

    # リンク先を絶対URLに変換する
    for link in links:
        href = link.get('href')

        if href:
            full_url = urljoin(current_url, href)
            full_url = full_url.split('#')[0]

            # 同一ドメインのリンクだけを追加する
            if urlparse(full_url).netloc == domain:
                if full_url.startswith('https://'):
                    if full_url not in visited:
                        urls.add(full_url)
# 取得結果をCSVファイルに保存する
with open('sitemap.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)

    # 見出しを書き込む
    writer.writerow(['URL', 'Title'])

    # 辞書の内容を書き込む
    for page_url, page_title in site_map.items():
        writer.writerow([page_url, page_title])

print('CSVファイルの保存が完了しました')


        