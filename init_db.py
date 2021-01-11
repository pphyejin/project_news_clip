import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs

import schedule

client = MongoClient('localhost', 27017)
db = client.dbmyproject


def get_article():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    data = requests.get('https://news.naver.com/main/home.nhn', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    section_tags = ["politics", "economy", "society"]

    for section_tag in section_tags:
        articles = soup.select(f'#section_{section_tag} > div.com_list > div > ul > li')

        for article in articles:
            title = article.select_one('a > strong').text
            if title:
                url = article.select_one('a')['href']

                # 기사를 겹치지 않고 가지고 오기 위한 유니크 키 생성.
                unique_url = f"{url}"

                parts = urlparse(unique_url)

                query_string = parse_qs(parts.query)
                # print(query_string)

                sid1 = query_string["sid1"][0]
                oid = query_string["oid"][0]
                aid = query_string["aid"][0]

                unique_key = f"{sid1}-{oid}-{aid}"
                # print(unique_key)

                doc = {
                    'unique_key': unique_key,
                    'title': title,
                    'url': url,
                }

                # # unique_key 값이 중복되지 않을때 db에 insert 하기.
                # Tutor : document가 있는지 찾기
                document = db.articleurl.find_one({"unique_key": unique_key})

                # Tutor : document가 없다면 추가하기
                if document is None:
                    db.articleurl.insert_one(doc)


def post_article():
    urls = list(db.articleurl.find())

    for url in urls:
        target_url = url['url']

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(target_url, headers=headers)

        soup = BeautifulSoup(data.text, 'html.parser')

        contents = soup.select('#main_content')
        og_desc = soup.select_one('meta[property="og:description"]')['content']

        for content in contents:
            title = soup.select_one('div.article_header > div.article_info > h3').text
            date = soup.select_one('div.article_header > div.article_info > div > span.t11').text
            media = soup.select_one('div.article_header > div.press_logo > a > img')['alt']

            # 기사를 겹치지 않고 가지고 오기 위한 유니크 키 생성.
            parts = urlparse(target_url)

            query_string = parse_qs(parts.query)
            # print(query_string)

            sid1 = query_string["sid1"][0]
            oid = query_string["oid"][0]
            aid = query_string["aid"][0]

            unique_key = f"{sid1}-{oid}-{aid}"

            # articleurl DB의 데이터 개수를 이용하여 번호를 매긴 후, 딕셔너리로 저장할때 순서대로 번호 매겨주기.
            # num = db.articleurl.countDocument()
            # for i in range(1,num):
            #     print("%s번째 기사입니다." %i)
            #     return

            # url주소가 네이버뉴스홈이면 korea 아이콘으로 db에 같이 저장하기.
            if target_url[:27] == "https://news.naver.com/main":
                doc2 = {
                    # 'num': num,
                    'icon': "../static/south-korea.png",
                    'unique_key': unique_key,
                    'url': url['url'],
                    'title': title,
                    'desc': og_desc,
                    'date': date,
                    'media': media,
                }

                # unique_key 값이 중복되지 않을때 db에 insert 하기.
                # Tutor : document가 있는지 찾기
                document2 = db.latestNews.find_one({"unique_key": unique_key})

                # Tutor : document가 없다면 추가하기
                if document2 is None:
                    db.latestNews.insert_one(doc2)

    # print(url['url'], title, og_desc, date, media)


post_article()
get_article()

# def job():
#    get_article()


# def run():
#    schedule.every(3).minutes.do(job)  # 3분에 한번씩 실행
#    while True:
#        schedule.run_pending()


# if __name__ == "__main__":
#    run()
