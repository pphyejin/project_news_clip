from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs

import schedule

client = MongoClient('localhost', 27017)
db = client.dbmyproject

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/latest')
def latest():
    return render_template("latest.html")

@app.route('/api/latest', methods=['GET'])
def show_latest_news():
    news = list(db.latestNews.find({}, {'_id': False}).sort('datetime', -1).limit(15))
    return jsonify({'result': 'success', 'all_news': news})

@app.route('/hottest')
def hottest():
    return render_template("hottest.html")

@app.route('/api/hottest', methods=['GET'])
def show_hottest_news():
    date_0_receive = request.form['date_0']
    date_1_receive = request.form['date_1']
    date_2_receive = request.form['date_2']
    date_3_receive = request.form['date_3']
    date_4_receive = request.form['date_4']
    date_5_receive = request.form['date_5']
    date_6_receive = request.form['date_6']
    news = list(db.hottestNews.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'all_news': news})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)