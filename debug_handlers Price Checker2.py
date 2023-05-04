import os
import sqlite3  # This is another way to work with SQL
from sqlite3.dbapi2 import Error
from datetime import datetime
from PIL import Image
from flask import Flask
from flask import request
import json
from pony.orm import select, db_session, commit
import ui_global


app = Flask(__name__)


# -BEGIN CUSTOM HANDLERS

DB_PATH_debug = 'db.db'    #DB_PATH = 'db.db' #new2 замена переменной

unit_id = -1
_nom_id = -1
_cell_id = -1
_cells = {}
_cellid = None
# found = []
_green_size = 0
_yellow_size = 0


#func = method.replace('_', '', 1)

def init_on_start():#hashMap, _files=None, _data=None):
    ui_global.init()
    return hashMap

def read_good_cv(hashMap, _files=None, _data=None):
    hashMap.put("toast", 'read_good_cv line15966')  # time!!!
    if hashMap.containsKey("stop_listener_list"):
        hashMap.remove("stop_listener_list") # очистили stop_listener_list

    # create connection with database
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH_debug)# было - заменил('//data/data/ru.travelfood.simple_ui/databases/SimpleWMS')
    except Error as e:
        raise ValueError('Нет соединения с базой!')

    cursor = conn.cursor()
    cursor.execute("SELECT barcode,id,name,price FROM SW_Goods")

    results = cursor.fetchall()

    green_list = []
    red_list = []
    info_list = []
    yellow_list = []
    _goods = {}
    for link in results:
        _goods[link[0]] = link[3]# записали в _goods все QR-коды и цены товаров из базы
        yellow_list.append(link[0])  # записали в yellow_list все QR-коды из базы
        red_list.append(str(link[3]).split('.')[0])  # записали в red_list все цены из базы

    conn.close()
    hashMap.put("_goods", json.dumps(_goods, ensure_ascii=False))# time!!!
    hashMap.put("red_list", ';'.join(red_list))
    hashMap.put("yellow_list", ';'.join(yellow_list))
    hashMap.put("toast", str(hashMap.get('yellow_list')) +' line1595')  # time!!!

    return hashMap



def get_good_cv(hashMap, _files=None, _data=None):

    #hashMap.put("toast", str(hashMap.get("current_object")) + ' line1605')  # time!!! Доходим!!!
    qr_object = str(hashMap.get("current_object"))
    hashMap.put("qr_object", str(qr_object))
    #hashMap.put("toast", str(hashMap.get("qr_object")) + ' line1535')  # time!!!
    hashMap.put("vibrate", "")
    yellow_list = hashMap.get("yellow_list").split(";")# Error sometimes ??!
    if qr_object in yellow_list:#
        hashMap.put("NextStep", "Проверка цены")
    else:
        hashMap.put("toast", 'Штрихкод в базе не найден!! line1542')  # time!!!

    return hashMap

def read_price_cv(hashMap, _files=None, _data=None):# Имя CV-шага: Проверка цены OnCreate

    hashMap.put("toast", 'read_good_cv line15966')  # time!!!

    return hashMap

def found_price_cv(hashMap, _files=None, _data=None):# Имя CV-шага: Проверка цены OnObjectDetected

    price_object = str(hashMap.get("current_object"))

    # перекрашиваем в green

    if hashMap.containsKey("green_list"):
        green_list = hashMap.get("green_list").split(";")

        green_list.append(price_object)
        hashMap.put("green_list", ";".join(green_list))

    else:
        hashMap.put("yellow_list", price_object)

    if hashMap.containsKey("red_list") and price_object in hashMap.get("red_list"):
        red_list = hashMap.get("red_list").split(";")
        red_list.remove(price_object)
        hashMap.put("red_list", ";".join(red_list))

    return hashMap

def wrong_price_cv(hashMap, _files=None, _data=None):# Имя CV-шага: Проверка цены OnInput

    hashMap.put("toast", 'wrong_price_cv line1634')  # time!!!


    return hashMap


# -END CUSTOM HANDLERS



@app.route('/set_input_direct/<method>', methods=['POST'])
def set_input(method):
    #func = method
    func = method.replace('_', '', 1)
    jdata = json.loads(request.data.decode('utf-8'))
    f = globals()[func]
    hashMap.d = jdata['hashmap']
    # f()
    # f('hashmap')
    f(hashMap)  # new
    jdata['hashmap'] = hashMap.export()
    jdata['stop'] = False
    jdata['ErrorMessage'] = ''
    jdata['Rows'] = []

    return json.dumps(jdata)


@app.route('/post_screenshot', methods=['POST'])
def post_screenshot():
    d = request.data
    return '1'


class hashMap:
    d = {}

    def put(key, val):
        hashMap.d[key] = val

    def get(key):
        return hashMap.d.get(key)

    def remove(key):
        if key in hashMap.d:
            hashMap.d.pop(key)

    def containsKey(key):
        return key in hashMap.d

    def export():  # It's NOT error!!!
        ex_hashMap = []
        for key in hashMap.d.keys():
            ex_hashMap.append({'key': key, 'value': hashMap.d[key]})
        return ex_hashMap


if __name__ == '__main__':
    init_on_start()  # new
    app.run(host='0.0.0.0', port=2075, debug=True)
