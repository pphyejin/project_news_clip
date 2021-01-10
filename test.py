import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbmyproject

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://news.naver.com/main/home.nhn', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

section_tags = ["politics", "economy", "society"]

for section_tag in section_tags:
    articles = soup.select(f'#section_{section_tag} > div.com_list > div > ul > li')

    for article in articles:
        title = article.select_one('a > strong').text
        if title is not None:
            url = article.select_one('a')['href']
            # print(title, url)
            doc = {
                'title': title,
                'url': url,
            }
            db.articleurl.insert_one(doc)


urls = list(db.articleurl.find())

for url in urls:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url['url'], headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    contents = soup.select('#main_content')
    og_desc = soup.select_one('meta[property="og:description"]')['content']

    for content in contents:
        title = soup.select_one('div.article_header > div.article_info > h3').text
        desc = soup.select_one('head > meta:nth-child(14)')
        date = soup.select_one('div.article_header > div.article_info > div > span').text
        media = soup.select_one('div.article_header > div.press_logo > a > img')['alt']

        print(title, og_desc, date, media)
