from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/latest')
def latest():
    return render_template("latest.html")

@app.route('/hottest')
def hottest():
    return render_template("hottest.html")



if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)