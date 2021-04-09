import requests
import requests_html
import flask
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re
from flask import Flask
from flask import request
from flask import jsonify
from flask_sslify import SSLify
import json


app=Flask(__name__)
sslify=SSLify(app)

cable_parametr = ["Максимальный наружный диаметр (мм)", "Допустимый радиус изгиба (мм)","Электрическое сопротивление жилы (ом/км)",
                  "Допустимая токовая нагрузка при прокладке на воздухе (А)","Допустимая токовая нагрузка при прокладке в земле (А)",
                  "Допустимый ток односекундного короткого замыкания (кА)"]

""" Функция google_site_page_open принимает query, передаёт его в Google 
Search и возвращает ссылку на сайт с искомым кабелем """

def google_site_page_open(message):
    url = f"http://www.google.com/search?q={message}"
    session = HTMLSession()
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    site_list = soup.find(href=re.compile("https\:\/\/e\-kc\.ru\/[^&]"))
    adress = str(site_list).split('"')
    cable_site = adress[1]
    return cable_site

""" Функция get_cabel_parametr принимает ссылку на сайт с искомым кабелем 
и интересующие параметры,значения которых необходимо возвратить"""

def get_cabel_parametr(cable_site,cable_parametr):
    value_cable_list=[]
    session = HTMLSession()
    r = session.get(cable_site)
    soup = BeautifulSoup(r.text, "html.parser")
    info_cabel_sheet = soup.find("ul", {"id": "idTab2", "class": "features"})
    for i in range(0,len(cable_parametr)):
        try:
            info_cabel_column_1 = info_cabel_sheet.find("label", string=cable_parametr[i])
            info_cabel_column_2 = info_cabel_column_1.find_next_sibling()
            info_cabel_column_3= info_cabel_column_2.get_text()
        except AttributeError:
            info_cabel_column_3="Данный параметр отсутствует"
        value_cable_list.append(info_cabel_column_3)
    return value_cable_list

"""Функция соотносит названия искомых праметров кабеля с их значениями и формирует словарь"""

def dictionaty_cabel_parametr(cable_parametr,value_cable_list):
    dictionaty_cabel_parametr={}
    for i in range(0,len(value_cable_list)):
        dictionaty_cabel_parametr[cable_parametr[i]]=value_cable_list[i]
    return dictionaty_cabel_parametr
"""Функция отправляет сообщения пользователю"""

def send_messages(chat_id,text="Введите марку кабеля"):
    URL="https://api.telegram.org/bot"+"1234823733:AAFfpdjr212av84TUxbJ8HbFbiActvJXccA"+"/sendMessage"
    answer={"chat_id":chat_id,"text":text}
    response=requests.post(URL,json=answer)
    return response.json()

@app.route("/",methods=["POST","GET"])

def index():
    if request.method=="POST":
        response=request.get_json()
        chat_id=response["message"]["chat"]["id"]
        message=response["message"]["text"]
        if "/start" == message:
            send_messages(chat_id)
        patern = re.fullmatch(r'[А-Яа-я()]{1,10}\-{0,1}[А-Я-а-яA-Za-z]{0,7}\s\d{0,2}х\d{0,3}\,{0,1}\d{0,3}', message)
        if patern != None:
            info=str(dictionaty_cabel_parametr(cable_parametr,get_cabel_parametr(google_site_page_open(message),cable_parametr)))
            send_messages(chat_id,text=info)
        elif patern == None and "/start" != message :
            send_messages(chat_id, text="Чувак ты вводишь маркировку кабеля некорректно")
        return jsonify(response)
    return '<h1> Bot wellcome you1</h1>'

if __name__=="__main__":
    app.run()

