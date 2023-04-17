from unicodedata import name

import ui_global
from pony.orm.core import db_session
from pony import orm
from pony.orm import Database, Required, Set, select, commit
import json
import os
import sqlite3  # This is another way to work with SQL
from sqlite3.dbapi2 import Error
from datetime import datetime
from PIL import Image

# from flask import Flask
# from flask import request
# import json
# from pony.orm import select, db_session, commit
# import ui_global


unit_id = -1
_nom_id = -1
_cell_id = -1
_cells = {}
_cellid = None
# found = []
_green_size = 0
_yellow_size = 0


def init_on_start(hashMap, _files=None, _data=None):
    ui_global.init()
    return hashMap


def menu_input(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "menu":
        if hashMap.get("menu") == "Добавить товар":
            hashMap.put("ShowScreen", "Добавить товар")
        if hashMap.get("menu") == "Добавить ячейку":
            hashMap.put("ShowScreen", "Добавить ячейку")
        if hashMap.get("menu") == "Добавить группу товаров":
            hashMap.put("ShowScreen", "Добавить группу товаров")

        elif hashMap.get("menu") == "Добавить единицу измерения":
            hashMap.put("ShowScreen", "Добавить единицу измерения")
    elif hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("FinishProcess", "")
    return hashMap


def menu_on_start(hashMap, _files=None, _data=None):
    # hashMap.put("getfiles","")
    # hashMap.put("toast","test1")
    return hashMap


# ---------------------------доп функции
def get_table_by_cell(id):
    table = {
        "type": "table",
        "textsize": "17",

        "columns": [
            {
                "name": "cell",
                "header": "Ячейка",
                "weight": "1"
            },
            {
                "name": "nom",
                "header": "Товар",
                "weight": "2"
            },
            {
                "name": "qty",
                "header": "Остаток",
                "weight": "1"
            }
        ]
    }

    conn = None
    try:
        conn = sqlite3.connect('//data/data/ru.travelfood.simple_ui/databases/SimpleWMS')
    except Error as e:
        raise ValueError('Нет соединения с базой!')

    cursor = conn.cursor()
    cursor.execute(
        "SELECT SW_Cells.name as cell,SW_Goods.name as nom, ifnull(sum(qty),0) as qty FROM SW_Account LEFT JOIN SW_Goods ON SW_Account.sku=SW_Goods.id LEFT JOIN SW_Cells ON SW_Account.cell=SW_Cells.id WHERE SW_Account.cell = " + str(
            id) + " GROUP BY SW_Goods.name ,SW_Cells.name HAVING ifnull(sum(qty),0)<>0")

    results = cursor.fetchall()

    rows = []
    for record in results:
        rows.append({"cell": record[0], "nom": record[1], "qty": record[2]})

    table['rows'] = rows

    return json.dumps(table)


# ---------------------------Добавить единицу измерения
def units_on_start(hashMap, _files=None, _data=None):
    table = {
        "type": "table",
        "textsize": "20",

        "columns": [
            {
                "name": "name",
                "header": "Наименование",
                "weight": "1"
            }
        ]
    }
    # work with SQL via Pony ORM

    query = select(c for c in ui_global.SW_Units)
    rows = []
    for record in query:
        rows.append({"name": record.name, "id": record.id})

    table['rows'] = rows
    hashMap.put("list", json.dumps(table))

    return hashMap


def units_input(hashMap, _files=None, _data=None):
    global unit_id

    if hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("ShowScreen", "Меню НСИ")

    elif hashMap.get("listener") == "btn_add":
        hashMap.put("name", "")
        unit_id = -1
        hashMap.put("ShowDialog", "ДиалогЕдиницы")
        hashMap.put("ShowDialogStyle", json.dumps({"title": "Добавление записи", "yes": "Сохранить", "no": "Отмена"}))

    elif hashMap.get("listener") == "TableClick":

        jrecord = json.loads(hashMap.get("selected_line"))
        # hashMap.put("toast",str(jrecord['id']))
        unit_id = jrecord['id']
        hashMap.put("name", jrecord['name'])

        hashMap.put("ShowDialog", "ДиалогЕдиницы")
        hashMap.put("ShowDialogStyle", json.dumps({"title": "Добавление записи", "yes": "Сохранить", "no": "Отмена"}))
    elif hashMap.get("event") == "onResultPositive":
        # hashMap.put("toast",str(unit_id))
        if unit_id < 0:
            with db_session:
                r = ui_global.SW_Units(name=hashMap.get('name'))
                commit()
        else:
            with db_session:
                if hashMap.get('name') == "":  # удаление
                    r = ui_global.SW_Units[unit_id]
                    r.delete()
                else:  # редактирование
                    r = ui_global.SW_Units[unit_id]
                    r.name = hashMap.get('name')

                commit()

    return hashMap


# ---------------------------Добавить группу товаров
def groups_on_start(hashMap, _files=None, _data=None):
    table = {
        "type": "table",
        "textsize": "20",

        "columns": [
            {
                "name": "name",
                "header": "Наименование",
                "weight": "1"
            }
        ]
    }
    # work with SQL via Pony ORM

    query = select(c for c in ui_global.SW_Groups)
    rows = []
    for record in query:
        rows.append({"name": record.name, "id": record.id})

    table['rows'] = rows
    hashMap.put("list", json.dumps(table))

    return hashMap


def groups_input(hashMap, _files=None, _data=None):
    global unit_id

    if hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("ShowScreen", "Меню НСИ")
    elif hashMap.get("listener") == "btn_add":
        hashMap.put("name", "")
        unit_id = -1
        hashMap.put("ShowDialog", "ДиалогГруппы")
        hashMap.put("ShowDialogStyle", json.dumps({"title": "Добавление записи", "yes": "Сохранить", "no": "Отмена"}))

    elif hashMap.get("listener") == "TableClick":

        jrecord = json.loads(hashMap.get("selected_line"))
        # hashMap.put("toast",str(jrecord['id']))
        unit_id = jrecord['id']
        hashMap.put("name", jrecord['name'])

        hashMap.put("ShowDialog", "ДиалогГруппы")
        hashMap.put("ShowDialogStyle", json.dumps({"title": "Добавление записи", "yes": "Сохранить", "no": "Отмена"}))
    elif hashMap.get("event") == "onResultPositive":
        # hashMap.put("toast",str(unit_id))
        if unit_id < 0:
            with db_session:
                r = ui_global.SW_Groups(name=hashMap.get('name'))
                commit()
        else:
            with db_session:
                if hashMap.get('name') == "":  # удаление
                    r = ui_global.SW_Groups[unit_id]
                    r.delete()
                else:  # редактирование
                    r = ui_global.SW_Groups[unit_id]
                    r.name = hashMap.get('name')

                commit()

    return hashMap


# -----------------------------------------Добавить товар
def goods_on_start(hashMap, _files=None, _data=None):
    hashMap.put("mm_local", "")
    hashMap.put("mm_compression", "70")
    hashMap.put("mm_size", "65")

    list = {"customcards": {

        "layout": {
            "type": "LinearLayout",
            "orientation": "vertical",
            "height": "match_parent",
            "width": "match_parent",
            "weight": "0",
            "Elements": [
                {
                    "type": "LinearLayout",
                    "orientation": "horizontal",
                    "height": "wrap_content",
                    "width": "match_parent",
                    "weight": "0",
                    "Elements": [
                        {
                            "type": "Picture",
                            "show_by_condition": "",
                            "Value": "@pic",
                            "NoRefresh": False,
                            "document_type": "",
                            "mask": "",
                            "Variable": "",
                            "TextSize": "16",
                            "TextColor": "#DB7093",
                            "TextBold": True,
                            "TextItalic": False,
                            "BackgroundColor": "",
                            "width": "75",
                            "height": "75",
                            "weight": 0
                        },
                        {
                            "type": "LinearLayout",
                            "orientation": "vertical",
                            "height": "wrap_content",
                            "width": "match_parent",
                            "weight": "1",
                            "Elements": [
                                {
                                    "type": "TextView",
                                    "show_by_condition": "",
                                    "Value": "@name",
                                    "NoRefresh": False,
                                    "document_type": "",
                                    "mask": "",
                                    "Variable": ""
                                },
                                {
                                    "type": "TextView",
                                    "show_by_condition": "",
                                    "Value": "@product_number",
                                    "NoRefresh": False,
                                    "document_type": "",
                                    "mask": "",
                                    "Variable": ""
                                },
                                {
                                    "type": "TextView",
                                    "show_by_condition": "",
                                    "Value": "@barcode",
                                    "NoRefresh": False,
                                    "document_type": "",
                                    "mask": "",
                                    "Variable": ""
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    }
    }

    # _files = json.loads(hashMap.get("_files"))

    query = select(c for c in ui_global.SW_Goods)
    list["customcards"]["cardsdata"] = []

    for record in query:

        pic = ""
        if 'photo' in record.pictures:

            p = record.pictures['photo']

            if len(p) > 0:

                for jf in _files:# находим путь к файлу по идентификатору
                    if jf['id'] == p[0]:
                        if os.path.exists(jf['path']):
                            pic = "~" + jf['path']
                        break

        list["customcards"]["cardsdata"].append(
            {"name": record.name, "key": record.id, "product_number": str(record.product_number),
             "barcode": str(record.barcode), "unit": str(record.unit), "skugroup": str(record.group),
             "price": record.price, "unique": record.unique, "pictures": json.dumps(record.pictures), "pic": pic})
    hashMap.put("list", json.dumps(list))

    return hashMap


def open_nom(hashMap, key):#, _nom_id, key):
    jlist = json.loads(hashMap.get("list"))
    goodsarray = jlist["customcards"]['cardsdata']

    jrecord = next(item for item in goodsarray if str(item["key"]) == key)

    hashMap.put('_nom_id', str(jrecord['key']))  # ввод _nom_id
    hashMap.put("name", jrecord['name'])
    hashMap.put("barcode", jrecord['barcode'])
    hashMap.put("unit", jrecord['unit'])
    hashMap.put("group", jrecord['skugroup'])
    hashMap.put("price", str(jrecord['price']))
    hashMap.put("product_number", jrecord['product_number'])

    if jrecord['unique'] == 1:
        hashMap.put("unique", "true")
    else:
        hashMap.put("unique", "false")

    # if len(str(jrecord['pictures']))>0:
    jg = json.loads(jrecord['pictures'])
    if 'photo' in jg:
        hashMap.put("photoGallery", json.dumps(jg['photo']))
    else:
        hashMap.put("photoGallery", json.dumps([]))
    hashMap.put("ShowScreen", "ТоварыЗапись")

    return hashMap#, _nom_id


def goods_input(hashMap, _files=None, _data=None):
    # global _nom_id

    if hashMap.get("listener") == "btn_add":
        hashMap.put("name", "")
        hashMap.put("barcode", "")
        hashMap.put("unit", "")
        hashMap.put("group", "")
        hashMap.put("price", "0")
        hashMap.put("unique", "false")
        hashMap.put("product_number", "")

        hashMap.put("photoGallery", json.dumps([]))  # пустой список под галерею

        _nom_id = -1  # изменяется _nom_id
        hashMap.put('_nom_id', str(_nom_id))  # ввод _nom_id
        hashMap.put("ShowScreen", "ТоварыЗапись")


    elif hashMap.get("listener") == "CardsClick":

        hashMap = open_nom(hashMap, hashMap.get("selected_card_key"))  # изменяется переменная


    elif hashMap.get("listener") == "barcode":
        # hashMap.put("toast",hashMap.get("barcode_input"))

        nom = ui_global.SW_Goods.get(barcode=hashMap.get("barcode_search"))
        if nom == None:
            hashMap.put("toast", "Товар не найден")
        else:
            hashMap = open_nom(hashMap, str(nom.id))

            hashMap.put("speak", nom.name)


    elif hashMap.get("listener") == "vision":
        # hashMap.put("toast",hashMap.get("_nom_id"))

        nom = ui_global.SW_Goods.get(id=int(hashMap.get("_nom_id")))
        if nom == None:
            hashMap.put("toast", "Товар не найден")
        else:
            hashMap = open_nom(hashMap, str(nom.id))
            hashMap.put("speak", nom.name)
    elif hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("ShowScreen", "Меню НСИ")

    return hashMap


def get_if_exist(hashMap, field):
    if hashMap.containsKey(field):
        res = hashMap.get(field)
    else:
        res = ""
    return res


def getboolean_if_exist(hashMap, field):
    if not hashMap.containsKey(field):
        res = 0
    else:
        if hashMap.get(field) == "true":
            res = 1
        else:
            res = 0

    return res


def getfloat_if_exist(hashMap, field):
    if not hashMap.containsKey(field):
        res = 0
    else:
        try:
            res = float(hashMap.get(field))

        except:
            return 0
    return res


def save_nom(hashMap):
    # global _nom_id
    if not hashMap.containsKey("name"):
        hashMap.put("toast", "Не указано наименование")
        return hashMap, False
    else:
        if len(hashMap.get("name")) == 0:
            hashMap.put("toast", "Не указано наименование")
            return hashMap, False

    if not hashMap.containsKey("unit"):
        hashMap.put("toast", "Не указана единица")
        return hashMap, False
    else:
        if len(hashMap.get("unit")) == 0:
            hashMap.put("toast", "Не указана единица")
            return hashMap, False

    if int(hashMap.get('_nom_id')) < 0:  # прочитали _nom_id

        with db_session:  # создаем новую запись
            r = ui_global.SW_Goods(name=get_if_exist(hashMap, "name"), barcode=get_if_exist(hashMap, "barcode"),
                                   unit=get_if_exist(hashMap, "unit"), group=get_if_exist(hashMap, "group"),
                                   product_number=get_if_exist(hashMap, "product_number"),
                                   price=getfloat_if_exist(hashMap, "price"),
                                   unique=getboolean_if_exist(hashMap, "unique"))
            _nom_id = r.id  # изменяется _nom_id
            hashMap.put('_nom_id', str(_nom_id))  # ввод _nom_id
            commit()
    else:  # перезаписываеm старую запись
        with db_session:

            r = ui_global.SW_Goods[int(hashMap.get('_nom_id'))]  # прочитали _nom_id
            r.name = get_if_exist(hashMap, "name")
            r.barcode = get_if_exist(hashMap, "barcode")
            r.unit = get_if_exist(hashMap, "unit")
            r.group = get_if_exist(hashMap, "group")
            r.product_number = get_if_exist(hashMap, "product_number")
            r.price = getfloat_if_exist(hashMap, "price")
            r.unique = getboolean_if_exist(hashMap, "unique")

            j = {}

            j['photo'] = json.loads(hashMap.get("photoGallery"))
            r.pictures = j

            commit()
    return hashMap, True


def goods_record_on_start(hashMap, _files=None, _data=None):
    # global _nom_id
    hashMap.put("mm_local", "")
    hashMap.put("mm_compression", "70")
    hashMap.put("mm_size", "65")

    hashMap.put("fill_name", json.dumps({"hint": "Введите наименование товара", "default_text": hashMap.get("name")}))
    hashMap.put("fill_barcode",
                json.dumps({"hint": "Введите/отсканируйте штрихкод товара", "default_text": hashMap.get("barcode")}))
    hashMap.put("fill_product_number",
                json.dumps({"hint": "Введите артикул товара", "default_text": hashMap.get("product_number")}))
    hashMap.put("fill_price", json.dumps({"hint": "Введите цену", "default_text": hashMap.get("price")}))

    units = []
    units.append("<Выберите ед-цу измерения ...>")

    query = select(c for c in ui_global.SW_Units)
    for record in query:
        units.append(record.name)

    hashMap.put("units", ";".join(units))

    groups = []
    groups.append("<Выберите группу товаров ...>")
    query = select(c for c in ui_global.SW_Groups)
    for record in query:
        groups.append(record.name)

    hashMap.put("groups", ";".join(groups))

    # hashMap.put("toast",hashMap.get("photoGallery"))

    return hashMap


def goods_record_input(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "btn_save":
        hashMap, success = save_nom(hashMap)
        if success:
            hashMap.put("ShowScreen", "Добавить товар")

    elif hashMap.get("listener") == "barcode":
        hashMap.put("barcode", hashMap.get("barcode_nom"))

    elif hashMap.get("listener") == "CardsClick":
        hashMap.put("toast", str(hashMap.get("selected_card_key")))

    elif hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("ShowScreen", "Добавить товар")

    elif hashMap.get("listener") == 'menu_del':
        with db_session:
            r = ui_global.SW_Goods[int(hashMap.get('_nom_id'))]
            r.delete()
        hashMap.put("toast", "Удалено...")
        hashMap.put("ShowScreen", "Добавить товар")


    elif hashMap.get("listener") == "photo":

        # Можно вообще этого не делать-оставлять как есть. Это для примера.
        image_file = str(
            hashMap.get("photo_path"))  # "переменная"+"_path" - сюда помещается путь к полученной фотографии
        # hashMap.put("toast",str(hashMap.get("photo_path")))

        # сразу сделаем фотку - квадратной - это простой вариант. Можно сделать например отдельо миниатюры для списка, это немного сложнее
        image = Image.open(image_file)
        im = image.resize((500, 500))
        im.save(image_file)

        jphotoarr = json.loads(hashMap.get("photoGallery"))
        hashMap.put("photoGallery", json.dumps(jphotoarr))
        # hashMap.put("toast",json.dumps(jphotoarr))

    elif hashMap.get(
            "listener") == "gallery_change":  # пользователь может удалить фото из галереи. Новый массив надо поместить к документу

        if hashMap.containsKey("photoGallery"):  # эти 2 обработчика - аналогичные, просто для разных событий
            jphotoarr = json.loads(hashMap.get("photoGallery"))
            hashMap.put("photoGallery", json.dumps(jphotoarr))
            # hashMap.put("toast","#2"+json.dumps(jphotoarr))

    return hashMap

    # -------------------------Добавить ячейку


def cells_on_start(hashMap, _files=None, _data=None):
    list = {"customcards": {

        "layout": {
            "type": "LinearLayout",
            "orientation": "vertical",
            "height": "match_parent",
            "width": "match_parent",
            "weight": "0",
            "Elements": [

                {
                    "type": "TextView",
                    "show_by_condition": "",
                    "Value": "@name",
                    "NoRefresh": False,
                    "document_type": "",
                    "mask": "",
                    "Variable": ""
                },

                {
                    "type": "TextView",
                    "show_by_condition": "",
                    "Value": "@barcode",
                    "NoRefresh": False,
                    "document_type": "",
                    "mask": "",
                    "Variable": ""
                }
            ]
        }

    }
    }

    query = select(c for c in ui_global.SW_Cells)
    list["customcards"]["cardsdata"] = []

    for record in query:
        list["customcards"]["cardsdata"].append({"name": record.name, "key": record.id, "barcode": str(record.barcode)})
    hashMap.put("list", json.dumps(list))

    return hashMap


def cells_input(hashMap, _files=None, _data=None):
    # global _cell_id

    if hashMap.get("listener") == "btn_add":
        hashMap.put("name", "")
        hashMap.put("barcode", "")

        _cell_id = -1
        hashMap.put('_cell_id', str(_cell_id))  # ввод _cell_id Time!!!
        hashMap.put("ShowScreen", "ЯчейкиЗапись")


    elif hashMap.get("listener") == "CardsClick":

        jlist = json.loads(hashMap.get("list"))
        goodsarray = jlist["customcards"]['cardsdata']

        jrecord = next(item for item in goodsarray if str(item["key"]) == hashMap.get("selected_card_key"))

        _cell_id = jrecord['key']
        hashMap.put('_cell_id', str(_cell_id))  # ввод _cell_id
        hashMap.put("name", jrecord['name'])
        hashMap.put("barcode", jrecord['barcode'])

        hashMap.put("ShowScreen", "ЯчейкиЗапись")

    elif hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("ShowScreen", "Меню НСИ")

    return hashMap  # Time!!! 1 Err 'No module named 'flask''


def cells_record_on_start(hashMap, _files=None, _data=None):
    hashMap.put("fill_name", json.dumps({"hint": "Наименование", "default_text": hashMap.get("name")}))
    hashMap.put("fill_barcode", json.dumps({"hint": "Штрихкод", "default_text": hashMap.get("barcode")}))

    return hashMap


def cells_record_input(hashMap, _files=None, _data=None):
    # global cell_id

    if hashMap.get("listener") == "btn_save":
        # hashMap.put("toast",str(cell_id))

        if not hashMap.containsKey("name"):
            hashMap.put("toast", "Не указано наименование")
            return hashMap
        else:
            if len(hashMap.get("name")) == 0:
                hashMap.put("toast", "Не указано наименование")
                return hashMap

        # if _cell_id < 0:
        if int(hashMap.get('_cell_id')) < 0:  # прочитали _cell_id

            with db_session:
                r = ui_global.SW_Cells(name=get_if_exist(hashMap, "name"), barcode=get_if_exist(hashMap, "barcode"))
                commit()
        else:
            with db_session:

                r = ui_global.SW_Cells[int(hashMap.get('_cell_id'))]  # прочитали _cell_id
                r.name = get_if_exist(hashMap, "name")
                r.barcode = get_if_exist(hashMap, "barcode")

                commit()
        hashMap.put("ShowScreen", "Добавить ячейку")

    elif hashMap.get("listener") == "barcode":
        hashMap.put("barcode", hashMap.get("barcode_cell"))

    elif hashMap.get("listener") == "CardsClick":
        a = True
        # hashMap.put("toast",str(hashMap.get("selected_card_key")))

    elif hashMap.get("listener") == 'ON_BACK_PRESSED':
        hashMap.put("ShowScreen", "Меню НСИ")
    elif hashMap.get("listener") == 'menu_del':
        with db_session:
            r = ui_global.SW_Cells[int(hashMap.get('_cell_id'))]  # прочитали _cell_id
            r.delete()
        hashMap.put("ShowScreen", "Добавить ячейку")
        hashMap.put("toast", "Удалено...")

    return hashMap


def income_cell_on_start(hashMap, _files=None, _data=None):
    jt = {
        "type": "table",
        "textsize": "25",
        "hidecaption": "false",
        "hideinterline": "false",
        "columns": [
            {
                "name": "cell",
                "header": "Ячейка",
                "weight": "1"
            },
            {
                "name": "nom",
                "header": "Товар",
                "weight": "2"
            },
            {
                "name": "qty",
                "header": "Кол-во",
                "weight": "1"
            }
        ],
        "rows": []
    }

    if not hashMap.containsKey("pf"):
        # hashMap.put("toast","Новый")
        hashMap.put("pf", "1")  # флаг для определения начала процесса
        hashMap.put("central_table", json.dumps(jt))

    cells = []
    cells.append("<выберите ячейку...>")

    query = select(c for c in ui_global.SW_Cells)
    for record in query:
        cells.append(record.name)

    hashMap.put("cells", ";".join(cells))

    return hashMap


def income_cell_on_input(hashMap, _files=None, _data=None):
    # hashMap.put("toast",hashMap.get("listener"))

    if hashMap.get("listener") == "":
        # hashMap.put("toast","Выбор товара--")

        if not hashMap.containsKey("cell"):
            hashMap.put("toast", "Не указана ячейка")
            return hashMap
        else:
            if len(hashMap.get("cell")) == 0:
                hashMap.put("toast", "Не указана ячейка")
                return hashMap

        hashMap.put("ShowScreen", "Выбор товара")

    elif hashMap.get("listener") == "barcode":

        cell = ui_global.SW_Cells.get(barcode=hashMap.get("barcode_cell"))
        if cell == None:
            hashMap.put("toast", "Ячейка не найдена")
        else:
            hashMap.put("cell", cell.name)
            hashMap.put("_cell_id", str(cell.id))  # ввод _cell_id
            hashMap.put("table_object",
                        get_table_by_cell(cell.id))  # new добавил таблицу для остатков товара в этой ячейке
            hashMap.put("ShowScreen", "Выбор товара")

    elif hashMap.get("listener") == 'cell':

        cell = ui_global.SW_Cells.get(name=hashMap.get("cell"))
        if cell == None:
            hashMap.put("toast", "Ячейка не найдена")
        else:
            hashMap.put("cell", cell.name)
            hashMap.put("_cell_id", str(cell.id))  # ввод _cell_id
            hashMap.put("table_object",
                        get_table_by_cell(cell.id))  # new добавил таблицу для остатков товара в этой ячейке
            hashMap.put("ShowScreen", "Выбор товара")

    return hashMap


def income_nom_input(hashMap, _files=None, _data=None):
    # hashMap.put("toast",hashMap.get("listener"))

    if hashMap.get("listener") == "":

        if not hashMap.containsKey("nom"):
            hashMap.put("toast", "Не указан товар")
            return hashMap
        else:
            if len(hashMap.get("cell")) == 0:
                hashMap.put("toast", "Не указан товар")
                return hashMap

        hashMap.put("ShowScreen", "Ввод количества")
    elif hashMap.get("listener") == "BACK_BUTTON":
        hashMap.put("ShowScreen", "Выбор ячейки")
    elif hashMap.get("listener") == "barcode":

        nom = ui_global.SW_Goods.get(barcode=hashMap.get("barcode"))
        if nom == None:
            hashMap.put("toast", "Товар не найден")
        else:
            hashMap.put("nom", nom.name)
            hashMap.put("_nom_id", str(nom.id))
            hashMap.put("speak", nom.name)
            hashMap.put("ShowScreen", "Ввод количества")
            hashMap.put("qty", "1")

    elif hashMap.get("listener") == "vision":
        # hashMap.put("toast",hashMap.get("_nom_id"))

        nom = ui_global.SW_Goods.get(id=int(hashMap.get("_nom_id")))
        if nom == None:
            hashMap.put("toast", "Товар не найден")
        else:
            hashMap.put("nom", nom.name)
            hashMap.put("_nom_id", str(nom.id))
            hashMap.put("speak", nom.name)
            hashMap.put("ShowScreen", "Ввод количества")
            hashMap.put("qty", "1")

    return hashMap


def income_qty_input(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "":

        if getfloat_if_exist(hashMap, "qty") > 0:
            with db_session:
                r = ui_global.SW_Account(qty=getfloat_if_exist(hashMap, "qty"), sku=int(hashMap.get("_nom_id")),
                                         cell=int(hashMap.get("_cell_id")))
                commit()


        else:

            hashMap.put("toast", "Не указано кол-во")
            return hashMap

    jt = json.loads(hashMap.get("central_table"))
    jt['rows'].append({"cell": hashMap.get("cell"), "nom": hashMap.get("nom"), "qty": hashMap.get("qty")})

    hashMap.put("central_table", json.dumps(jt))
    hashMap.put("table_object", get_table_by_cell(
        int(hashMap.get('_cell_id'))))  # new добавил таблицу для остатков товара в этой ячейке
    hashMap.put("ShowScreen", "Выбор товара")

    return hashMap


def outcome_qty_input(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "":

        if getfloat_if_exist(hashMap, "qty") > 0:
            with db_session:
                select_goods = select(g.qty for g in ui_global.SW_Account if
                                      g.sku == int(hashMap.get("_nom_id")) and g.cell == int(hashMap.get("_cell_id")))[
                               :]

                if sum(select_goods) + (-1 * getfloat_if_exist(hashMap, "qty")) < 0:
                    hashMap.put("toast", "Отгружено больше чем было в наличии!!!")
                else:
                    r = ui_global.SW_Account(qty=-1 * getfloat_if_exist(hashMap, "qty"),
                                             sku=int(hashMap.get("_nom_id")),
                                             cell=int(hashMap.get("_cell_id")))
                    commit()

        else:

            hashMap.put("toast", "Не указано кол-во")
            return hashMap

    jt = json.loads(hashMap.get("central_table"))
    jt['rows'].append({"cell": hashMap.get("cell"), "nom": hashMap.get("nom"), "qty": hashMap.get("qty")})

    hashMap.put("central_table", json.dumps(jt))
    hashMap.put("table_object", get_table_by_cell(
        int(hashMap.get('_cell_id'))))  # new добавил таблицу для остатков товара в этой ячейке
    hashMap.put("ShowScreen", "Выбор товара")

    return hashMap


def stock_on_create(hashMap, _files=None, _data=None):
    table = {
        "type": "table",
        "textsize": "17",

        "columns": [
            {
                "name": "cell",
                "header": "Ячейка",
                "weight": "1"
            },
            {
                "name": "nom",
                "header": "Товар",
                "weight": "2"
            },
            {
                "name": "qty",
                "header": "Остаток",
                "weight": "1"
            },
            {
                "name": "unit",
                "header": "Ед.Изм",
                "weight": "1"
            }
        ]
    }

    conn = None
    try:
        conn = sqlite3.connect('//data/data/ru.travelfood.simple_ui/databases/SimpleWMS')
    except Error as e:
        raise ValueError('Нет соединения с базой!')

    cursor = conn.cursor()
    cursor.execute(
        '''SELECT SW_Cells.name as cell, SW_Goods.name as nom, ifnull(sum(qty),0) as qty, SW_Goods.unit as unit
            FROM SW_Account LEFT JOIN SW_Goods ON SW_Account.sku=SW_Goods.id LEFT JOIN SW_Cells ON SW_Account.cell=SW_Cells.id GROUP BY SW_Goods.name ,SW_Cells.name HAVING ifnull(sum(qty),0)<>0''')

    results = cursor.fetchall()

    rows = []
    for record in results:
        rows.append({"cell": record[0], "nom": record[1], "qty": record[2], "unit": record[3]})

    table['rows'] = rows
    hashMap.put("table", json.dumps(table))

    return hashMap


def get_table_by_nom(id):
    table = {
        "type": "table",
        "textsize": "17",

        "columns": [
            {
                "name": "cell",
                "header": "Ячейка",
                "weight": "1"
            },
            {
                "name": "nom",
                "header": "Товар",
                "weight": "2"
            },
            {
                "name": "qty",
                "header": "Остаток",
                "weight": "1"
            }
        ]
    }

    conn = None
    try:
        conn = sqlite3.connect('//data/data/ru.travelfood.simple_ui/databases/SimpleWMS')
    except Error as e:
        raise ValueError('Нет соединения с базой!')

    cursor = conn.cursor()
    cursor.execute(
        "SELECT SW_Cells.name as cell,SW_Goods.name as nom, ifnull(sum(qty),0) as qty FROM SW_Account LEFT JOIN SW_Goods ON SW_Account.sku=SW_Goods.id LEFT JOIN SW_Cells ON SW_Account.cell=SW_Cells.id WHERE SW_Account.sku = " + str(
            id) + " GROUP BY SW_Goods.name ,SW_Cells.name HAVING ifnull(sum(qty),0)<>0")

    results = cursor.fetchall()

    rows = []
    for record in results:
        rows.append({"cell": record[0], "nom": record[1], "qty": record[2]})

    table['rows'] = rows

    return json.dumps(table)


def stock_input(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "barcode":

        nom = ui_global.SW_Goods.get(barcode=hashMap.get("barcode"))
        is_nom = False

        object = ""

        if nom == None:
            is_nom = False
        else:
            is_nom = True
            hashMap.put("object", nom.name)
            hashMap.put("table_object", get_table_by_nom(nom.id))
            hashMap.put("ShowScreen", "Остатки по объекту")

        if not is_nom:

            cell = ui_global.SW_Cells.get(barcode=hashMap.get("barcode"))
            if cell == None:
                hashMap.put("toast", "Штрихкод ни ячейки ни товара")
            else:
                hashMap.put("object", cell.name)
                hashMap.put("table_object", get_table_by_cell(cell.id))
                hashMap.put("ShowScreen", "Остатки по объекту")

    return hashMap


def stock_object_input(hashMap, _files=None, _data=None):
    if hashMap.get("listener") == "BACK_BUTTON":
        hashMap.put("ShowScreen", "Остатки")

    return hashMap


def inventory_on_start(hashMap, _files=None, _data=None):  # Экран: Документы (inventory)
    list = {"customcards": {

        "layout": {
            "type": "LinearLayout",
            "orientation": "vertical",
            "height": "match_parent",
            "width": "match_parent",
            "weight": "0",
            "Elements": [

                {
                    "type": "TextView",
                    "show_by_condition": "",
                    "Value": "@descr",
                    "NoRefresh": False,
                    "document_type": "",
                    "mask": "",
                    "Variable": ""
                },

                {
                    "type": "TextView",
                    "show_by_condition": "",
                    "Value": "@date",
                    "NoRefresh": False,
                    "document_type": "",
                    "mask": "",
                    "Variable": ""
                }
            ]
        }

    }
    }

    query = select(c for c in ui_global.SW_Inventory)
    list["customcards"]["cardsdata"] = []

    for record in query:
        list["customcards"]["cardsdata"].append(
            {"descr": record.description, "key": record.id, "date": str(record.created_at)})
    hashMap.put("inventory", json.dumps(list))

    return hashMap


def inventory_input(hashMap, _files=None, _data=None):  # Экран: Документы (inventory)
    # global cell_id

    if hashMap.get("listener") == "btn_new":

        hashMap.put("ShowScreen", "Новая инвентаризация")


    elif hashMap.get("listener") == "CardsClick":

        jlist = json.loads(hashMap.get("inventory"))
        goodsarray = jlist["customcards"]['cardsdata']

        jrecord = next(item for item in goodsarray if str(item["key"]) == hashMap.get("selected_card_key"))

        inv_id = jrecord['key']
        hashMap.put("inv_name", jrecord['descr'])
        hashMap.put("inv_id", str(inv_id))
        hashMap.put("inv_date", str(jrecord['date']))

        hashMap.put("ShowScreen", "Инвентаризация Результаты")

    return hashMap


def newinv_input(hashMap, _files=None, _data=None):
    # global cell_id

    if hashMap.get("listener") == "":
        with db_session:
            r = ui_global.SW_Inventory(description=hashMap.get('name'))
            commit()

            hashMap.put("inv_name", hashMap.get('name'))
            hashMap.put("inv_id", str(r.id))
            hashMap.put("inv_date", str(r.created_at))
            # hashMap.put("toast",str(r.id))

            hashMap.put("ShowScreen", "Инвентаризация Результаты")

    return hashMap


def invres_on_start(hashMap, _files=None, _data=None):
    invdate = datetime.fromisoformat(str(hashMap.get("inv_date")))
    hashMap.put("inv",
                "Инвентаризация " + str(hashMap.get("inv_name")) + " от " + invdate.strftime("%m.%d.%Y, %H:%M:%S"))

    table = {
        "type": "table",
        "textsize": "17",

        "columns": [
            {
                "name": "cell",
                "header": "Ячейка",
                "weight": "1"
            },
            {
                "name": "nom",
                "header": "Товар",
                "weight": "2"
            },
            {
                "name": "qtyplan",
                "header": "План",
                "weight": "1"
            },
            {
                "name": "qtyfact",
                "header": "Факт",
                "weight": "1"
            }
        ]
    }

    conn = None
    try:
        conn = sqlite3.connect('//data/data/ru.travelfood.simple_ui/databases/SimpleWMS')
    except Error as e:
        raise ValueError('Нет соединения с базой!')

    cursor = conn.cursor()
    cursor.execute(
        "select T.cell,T.nom,max(T.qtyplan) as qtyplan, ifnull(sum(F.qty),0) as qtyfact FROM (SELECT SW_Cells.name as cell,SW_Goods.name as nom, ifnull(sum(SW_Account.qty),0) as qtyplan,SW_Account.sku as skuid, SW_Account.cell as cellid FROM SW_Account LEFT JOIN SW_Goods ON SW_Account.sku=SW_Goods.id LEFT JOIN SW_Cells ON SW_Account.cell=SW_Cells.id   GROUP BY SW_Goods.name ,SW_Cells.name, SW_Account.cell, SW_Account.sku HAVING ifnull(sum(SW_Account.qty),0)<>0) as T LEFT JOIN SW_Inventory_line AS F ON T.cellid=F.cell AND T.skuid=F .sku and F .inventory=" + hashMap.get(
            "inv_id") + " GROUP BY T.cell,T.nom")

    results = cursor.fetchall()

    rows = []
    colorcells = []
    row = 0
    for record in results:

        rows.append({"cell": record[0], "nom": record[1], "qtyplan": record[2], "qtyfact": record[3]})
        # подкрашиваем результаты в зеленый и красный цвета
        if record[3] > 0:
            if record[3] >= record[2]:
                colorcells.append({"row": row, "column": "3", "color": "#32a852"})
            else:
                colorcells.append({"row": row, "column": "3", "color": "#e64c4c"})
        row += 1

    table['rows'] = rows
    table['colorcells'] = colorcells

    hashMap.put("table", json.dumps(table))

    return hashMap


def invres_input(hashMap, _files=None, _data=None):
    # global cell_id

    if hashMap.get("listener") == "btn_run":
        hashMap.put("RunCV", "ИнвCV")

    return hashMap


def invcv_cell_on_start(hashMap, _files=None, _data=None):
    # global cells
    # global cellid

    # _cellid = None # it's not necessary???
    # hashMap.put('_cellid', str(_cellid))  # ввод _cellid Time!!!

    if hashMap.containsKey("stop_listener_list"):
        hashMap.remove("stop_listener_list")

    # create connection with database
    conn = None
    try:
        conn = sqlite3.connect('//data/data/ru.travelfood.simple_ui/databases/SimpleWMS')
    except Error as e:
        raise ValueError('Нет соединения с базой!')

    cursor = conn.cursor()
    cursor.execute("SELECT barcode,id,name FROM SW_Cells")

    results = cursor.fetchall()

    green_list = []
    red_list = []
    info_list = []
    _cells = {}
    for link in results:
        # job = {"object":str(link[0]),"info":str(link[1])+" </n> Остаток: <big>"+str(link[2])+"</big>"}
        # info_list.append(job)
        green_list.append(link[0])
        _cells[link[0]] = link[1]

    conn.close()
    hashMap.put("_cells", json.dumps(_cells, ensure_ascii=False))  # time!!!
    # hashMap.put("object_info_list",json.dumps(info_list,ensure_ascii=False))
    hashMap.put("green_list", ';'.join(green_list))

    return hashMap


def invcv_cell_on_new_object(hashMap, _files=None, _data=None):
    # global cells
    # global cellid
    # global green_size, yellow_size

    if not hashMap.get('_green_size') == None:
        _green_size = int(hashMap.get('_green_size'))  # прочитали _green_size Time!!!
    else:
        _green_size = 0

    if not hashMap.get('_yellow_size') == None:
        _yellow_size = int(hashMap.get('_yellow_size'))  # прочитали _yellow_size Time!!!
    else:
        _yellow_size = 0

    hashMap.put("vibrate", "")
    _cells = json.loads(hashMap.get("_cells"))
    _cellid = _cells.get(hashMap.get("current_object"))  # enter error!!! Time!!!
    hashMap.put('_cellid', str(_cellid))  # ввод _cellid Time!!!

    if not _cellid == None:

        # create connection with database
        conn = None
        try:
            conn = sqlite3.connect('//data/data/ru.travelfood.simple_ui/databases/SimpleWMS')
        except Error as e:
            raise ValueError('Нет соединения с базой!')

        cursor = conn.cursor()
        try:
            # тут я понял что лажанулся, использовав unique в качестве имени, но было уже поздно
            cursor.execute(
                "SELECT SW_Goods.barcode as barcode,SW_Cells.name as cell,SW_Goods.name as nom, ifnull(sum(qty),0) as qty, \"unique\" as un,SW_Goods.id as _nom_id  FROM SW_Account LEFT JOIN SW_Goods ON SW_Account.sku=SW_Goods.id LEFT JOIN SW_Cells ON SW_Account.cell=SW_Cells.id WHERE SW_Account.cell = " + str(
                    _cellid) + " GROUP BY SW_Goods.name ,SW_Cells.name HAVING ifnull(sum(qty),0)<>0")
        except Error as e:
            raise ValueError(e)

        results = cursor.fetchall()

        # found = []

        yellow_list = []
        red_list = []
        info_list = []
        _yellow_size = 0
        _green_size = 0
        # используем object_info_list и запрос чтобы хранить заодно нужные поля, они нужны не для отобрадаения а для дальнейшей логики - unique, _nom_id
        for link in results:
            job = {"object": str(link[0]), "info": str(link[2]) + " </n> Остаток: <big>" + str(link[3]) + "</big>",
                   "unique": link[4], "_nom_id": str(link[5])}
            info_list.append(job)
            yellow_list.append(link[0])
            _yellow_size += 1

        conn.close()

        hashMap.put("object_info_list", json.dumps(info_list, ensure_ascii=False))

        if not yellow_list == None:
            hashMap.put("yellow_list", ';'.join(yellow_list))

        invdate = datetime.fromisoformat(str(hashMap.get("inv_date")))
        hashMap.put("inv", "Инвентаризация " + str(hashMap.get("inv_name")) + " от " + invdate.strftime(
            "%m.%d.%Y, %H:%M:%S") + "</n> Товаров: <big>" + str(_yellow_size) + "</big>")

        hashMap.put("NextStep", "Товары ячейки")

    hashMap.put('_green_size', str(_green_size))  # ввод _green_size Time!!!
    hashMap.put('_yellow_size', str(_yellow_size))  # ввод _yellow_size Time!!!

    return hashMap


def invcv_goods_on_new_object(hashMap, _files=None, _data=None):
    # global cells
    # global cellid
    # global green_size, _yellow_size

    nom_barcode = str(hashMap.get("current_object"))
    if nom_barcode in hashMap.get("yellow_list"):

        if not hashMap.get('_green_size') == None:
            _green_size = int(hashMap.get('_green_size'))  # прочитали _green_size Time!!!
        else:
            _green_size = 0

        if not hashMap.get('_yellow_size') == None:
            _yellow_size = int(hashMap.get('_yellow_size'))  # прочитали _yellow_size Time!!!
        else:
            _yellow_size = 0

        if hashMap.containsKey("stop_listener_list"):  # есть ли stop_listener_list в hashMap
            stop_list = hashMap.get("stop_listener_list").split(";")
            stop_list.append(nom_barcode)  # добавить nom_barcode в stop_listener_list
            hashMap.put("stop_listener_list", ";".join(stop_list))
        else:
            hashMap.put("stop_listener_list", nom_barcode)

        object_list = json.loads(hashMap.get("object_info_list"))

        try:  # проходим по object_list пока не найдем объект с баркодом текущего объекта
            nom_record = next(item for item in object_list if str(item["object"]) == str(nom_barcode))

        except StopIteration:
            nom_record = None

        if not nom_record == None:
            hashMap.put("_nom_id", str(nom_record.get("_nom_id")))  # Запись номера ID товара
            if hashMap.containsKey('write_id_list'):
                write_list = hashMap.get('write_id_list').split(';')
                write_list.append(str(nom_record.get('_nom_id')))
                hashMap.put('write_id_list', ';'.join(write_list))
            else:
                hashMap.put('write_id_list', str(nom_record.get('_nom_id')))
            if nom_record['unique'] == 1:  # это уникальный штрихкод???

                hashMap.put("vibrate", "")
                hashMap.put("beep", "5")

                # это уникальный штрихкод - добавляем его в зеленый список сразу и убираем из желтого
                _green_size = 0
                if hashMap.containsKey("green_list"):
                    green_list = hashMap.get("green_list").split(";")
                    green_list.append(nom_barcode)
                    hashMap.put("green_list", ";".join(green_list))

                else:
                    hashMap.put("green_list",
                                nom_barcode)

                if hashMap.containsKey("yellow_list"):
                    yellow_list = hashMap.get("yellow_list").split(";")
                    yellow_list.remove(nom_barcode)
                    hashMap.put("yellow_list", ";".join(yellow_list))

                    # добавляем в базу - он посчитан
                with db_session:
                    # found.append(int(hashMap.get("_nom_id")))
                    inventory = ui_global.SW_Inventory[int(hashMap.get("inv_id"))]
                    r = ui_global.SW_Inventory_line(qty=1, sku=int(hashMap.get("_nom_id")),
                                                    cell=int(hashMap.get("_cellid")),
                                                    inventory=inventory)  # прочитали _cellid Time!!!
                    commit()

                _green_size += 1
                invdate = datetime.fromisoformat(str(hashMap.get("inv_date")))
                hashMap.put("inv", "Инвентаризация " + str(hashMap.get("inv_name")) + " от " + invdate.strftime(
                    "%m.%d.%Y, %H:%M:%S") + "</n> Товаров: <big>" + str(_yellow_size) + "</big>")
            else:  # неуникальный штрихкод - просим ввести кол-во
                hashMap.put("beep", "50")  # начало Error!!! invalid literal for int() with base 10 none
                if hashMap.containsKey('write_list'):  # есть ли write_list в hashMap
                    write_list = hashMap.get("write_list").split(";")
                    write_list.append(nom_barcode)  # добавить nom_barcode в write_list
                    hashMap.put("write_list", ";".join(write_list))
                else:
                    hashMap.put("write_list", nom_barcode)

                hashMap.put("nom", nom_record.get("info"))
                hashMap.put("nom_barcode", nom_barcode)
                hashMap.put("ShowDialogProcess", "Инвентаризация Active CV")
                hashMap.put("ShowDialog", "ДиалогВводКоличества")  # error!!!
                hashMap.put("ShowDialogStyle",
                            json.dumps({"title": "Введите количество факт", "yes": "Подтвердить", "no": "Отмена"}))
        hashMap.put('_green_size', str(_green_size))  # ввод _green_size Time!!!
        hashMap.put('_yellow_size', str(_yellow_size))  # ввод _yellow_size Time!!!

    return hashMap


def invcv_goods_action(hashMap, _files=None, _data=None):
    # global cellid
    # global green_size, yellow_size

    # hashMap.put("toast",str(hashMap.get("event")))

    if hashMap.get("listener") == "onResultPositive":  # в диалоге ввода количества - "Ок" Error!!!

        hashMap.put("vibrate", "")

        if hashMap.containsKey('write_list'):  # есть ли write_list в hashMap
            write_list = hashMap.get("write_list").split(";")
            nom_barcode_write = str(write_list[-1])
            write_list.remove(nom_barcode_write)
            hashMap.put("write_list", ";".join(write_list))
        else:
            nom_barcode_write = str(hashMap.get("current_object"))
        # перекрашиваем в зеленый

        if hashMap.containsKey("green_list"):
            green_list = hashMap.get("green_list").split(";")
            green_list.append(nom_barcode_write)
            hashMap.put("green_list", ";".join(green_list))

        else:
            hashMap.put("green_list", nom_barcode_write)

        if hashMap.containsKey("yellow_list") and nom_barcode_write in hashMap.get("yellow_list"):
            yellow_list = hashMap.get("yellow_list").split(";")
            yellow_list.remove(nom_barcode_write)  # ValueError: list.remove(x): x not in list
            hashMap.put("yellow_list", ";".join(yellow_list))

        # определяем ID
        if hashMap.containsKey('write_id_list'):  # есть ли write_id_list в hashMap
            write_id_list = hashMap.get("write_id_list").split(";")
            _nom_id = str(write_id_list[-1])
            write_id_list.remove(_nom_id)
            hashMap.put("write_id_list", ";".join(write_id_list))
        else:
            _nom_id = str(hashMap.get('_nom_id'))

            # добавляем в базу
        if getfloat_if_exist(hashMap, "qty") > 0:
            if not hashMap.get('_green_size') == None:
                _green_size = int(hashMap.get('_green_size'))
            else:
                _green_size = 0

            if not hashMap.get('_yellow_size') == None:
                _yellow_size = int(hashMap.get('_yellow_size'))
            else:
                _yellow_size = 0
            _green_size += 1
            hashMap.put('_green_size', str(_green_size))  # ввод _green_size Time!!!
            hashMap.put('_yellow_size', str(_yellow_size))  # ввод _yellow_size Time!!!
            invdate = datetime.fromisoformat(str(hashMap.get("inv_date")))
            hashMap.put("inv", "Инвентаризация " + str(hashMap.get("inv_name")) + " от " + invdate.strftime(
                "%m.%d.%Y, %H:%M:%S") + "</n> Товаров: <big>" + str(_yellow_size) + "</big>")

            with db_session:
                inventory = ui_global.SW_Inventory[int(hashMap.get("inv_id"))]
                r = ui_global.SW_Inventory_line(qty=getfloat_if_exist(hashMap, "qty"), sku=int(_nom_id),
                                                cell=int(hashMap.get("_cellid")),
                                                inventory=inventory)  # прочитали qty Time!!!
                # found.append(int(_nom_id))
                commit()

    if hashMap.get("listener") == "К ЯЧЕЙКЕ":
        hashMap.put("NextStep", "Выбор ячейки")
        invdate = datetime.fromisoformat(str(hashMap.get("inv_date")))
        hashMap.put("inv",
                    "Инвентаризация " + str(hashMap.get("inv_name")) + " от " + invdate.strftime("%m.%d.%Y, %H:%M:%S"))

    return hashMap
