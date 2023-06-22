import flask
from flask import jsonify
from bs4 import BeautifulSoup
import string
import requests

cookies = {}

headers = {
    'Referer': 'https://foresignal.com/en/login',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://foresignal.com',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}


app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def index():
    return get_cookie_token()
    # return 'This is scrapping url'


@app.route('/get_data', methods=['GET'])
def get_data():

    try:
        resData = []

        url = 'https://foresignal.com/en/login/login'
        form_data = {
            'user_name': 'Kai.Stefan.Dietrich@gmail.com',
            'user_password': 'foresignalonline',
            'set_remember_me_cookie': 'on'
        }
        response = requests.post(url, headers=headers, cookies=cookies, data=form_data)
        print(response.status_code)

        soup = BeautifulSoup(str(response.content), 'html.parser')
        
        cardElems = soup.select('div.card.signal-card')
        date = ""
        signalData = []
        for cardElem in cardElems:
            signal = {
                "signal_time": "",
                "from": "",
                "to": "",
                "dirction": ""
            }

            symbolDiv = cardElem.select_one('div.card-header.signal-header a')
            if symbolDiv:
                symbol = symbolDiv.string
                signal["symbol"] = symbol

            signalTimeDiv = cardElem.select_one('div.card-body>div.signal-row:first-child .timeago ')
            if signalTimeDiv:
                signalTime = signalTimeDiv['datetime']
                signal["signal_time"] = signalTime

            fromDiv = cardElem.select_one('div.card-body>div.signal-row:nth-child(2) script:nth-child(2)')
            if fromDiv:
                fromVal = fromDiv.string
                signal["from"] = fromVal.replace('w(hhmm(', '').replace('));', '') + "000"

            toDiv = cardElem.select_one('div.card-body>div.signal-row:nth-child(3) script:nth-child(2)')
            if toDiv:
                toVal = toDiv.string
                signal["to"] = toVal.replace('w(hhmm(', '').replace('));', '') + '000'

            dirctionDiv = cardElem.select_one('div.card-body>div.signal-row:nth-child(4)')
            if dirctionDiv:
                dirction = dirctionDiv.string
                signal["dirction"] = dirction.replace('\\r', '').replace('\\n', '').replace('\\t', '').replace(' ', '')
           

            resData.append(signal)
        return jsonify(resData)
    except HTTPError as err:
        print(err)
        return jsonify('error')


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
