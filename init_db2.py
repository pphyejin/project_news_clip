import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import datetime

import schedule

client = MongoClient('localhost', 27017)
db = client.dbmyproject

def get_hottest_article():
    # 파이낸셜뉴스, YTN, SBS
    target_media = ["014", "052", "055"]

    # 타겟 언론사의 많이본 뉴스 url 뽑아내기
    for target_num in target_media:
        # print(target_num)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(f'https://news.naver.com/main/ranking/office.nhn?officeId={target_num}', headers=headers)

        soup = BeautifulSoup(data.text, 'html.parser')

        articles = soup.select(
            '#wrap > div.rankingnews > div.rankingnews_box._officeResult > div:nth-child(2) > ul > li')

        for article in articles:
            url = article.select_one('div > a')['href']
            # print(url)

            target_url = f'https://news.naver.com{url}'
            # print(target_url)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
            data = requests.get(target_url, headers=headers)

            soup2 = BeautifulSoup(data.text, 'html.parser')

            contents = soup2.select('#main_content')
            og_desc = soup2.select_one('meta[property="og:description"]')['content']

            for content in contents:
                title = soup2.select_one('#articleTitle').text
                date = soup2.select_one('div.article_header > div.article_info > div > span.t11').text
                media = soup2.select_one('div.article_header > div.press_logo > a > img')['alt']

                # date의 년월일만 가져와서 datetime 형식으로 변환.
                target = date[:10]
                date_time_obj = datetime.datetime.strptime(target, '%Y.%m.%d')

                # date의 오전오후를 am.pm으로 바꾸기,0 추가하기
                if date[12:14] == '오전':
                    date1 = date[:12] + 'AM' + date[14:]
                else:
                    date1 = date[:12] + 'PM' + date[14:]

                if date[16] == ':':
                    date1 = date1[:15] + '0' + date1[15:]

                # date 문자열을 datetime 형식으로 변환.
                date_time_obj2 = datetime.datetime.strptime(date1, '%Y.%m.%d. %p %I:%M')


                # 기사를 겹치지 않고 가지고 오기 위한 유니크 키 생성.
                parts = urlparse(target_url)

                query_string = parse_qs(parts.query)

                sid1 = query_string["sid1"][0]
                oid = query_string["oid"][0]
                aid = query_string["aid"][0]

                unique_key = f"{sid1}-{oid}-{aid}"

                # url주소가 네이버뉴스홈이면 korea 아이콘으로 db에 같이 저장하기.
                if target_url[:27] == "https://news.naver.com/main":
                    doc = {
                        'icon': "../static/south-korea.png",
                        'unique_key': unique_key,
                        'url': url,
                        'title': title,
                        'desc': og_desc,
                        'date': date,
                        'datetime': date_time_obj2,
                        'datetime_server': date_time_obj,
                        'media': media,
                    }

                    # db.hottestNews.drop()

                    # unique_key 값이 중복되지 않을때 db에 insert 하기.
                    # Tutor : document가 있는지 찾기
                    document = db.hottestNews.find_one({"unique_key": unique_key})
                    #
                    # # Tutor : document가 없다면 추가하기
                    if document is None:
                        db.hottestNews.insert_one(doc)


get_hottest_article()


# def job():
#    get_hottest_article()


# def run():
#    schedule.every().day.at("08:00").do(job)  # 매일 08:00에 실행
#    while True:
#        schedule.run_pending()


# if __name__ == "__main__":
#    run()
