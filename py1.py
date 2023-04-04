def invcv_cell_on_start(hashMap, _files=None, _data=None):
    #global cells
    #global cellid

    # _cellid = None # it's not necessary???
    # hashMap.put('_cellid', str(_cellid))  # ввод _cellid Time!!!

    if hashMap.containsKey("stop_listener_list"):
        hashMap.remove("stop_listener_list")

    # create connection with database
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH_debug)# было - заменил('//data/data/ru.travelfood.simple_ui/databases/SimpleWMS')
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
    hashMap.put("_cells", json.dumps(_cells, ensure_ascii=False))# time!!!
    hashMap.put("toast", str(hashMap.get('_cells')) +' line1263')  # time!!!
    # hashMap.put("object_info_list",json.dumps(info_list,ensure_ascii=False))
    hashMap.put("green_list", ';'.join(green_list))
    hashMap.put("toast", str(hashMap.get('green_list')) +' line1265')  # time!!!
    hashMap.put("toast", str(hashMap.get('yellow_list')) + ' line1266')  # time!!!

    return hashMap




def invcv_cell_on_new_object(hashMap, _files=None, _data=None):
    #global cells
    #global cellid
    #global green_size, yellow_size

    if not hashMap.get('_green_size')== None:
        _green_size = int(hashMap.get('_green_size'))  # прочитали _green_size Time!!!
    else:
        _green_size = 0

    if not hashMap.get('_yellow_size') == None:
        _yellow_size = int(hashMap.get('_yellow_size'))  # прочитали _yellow_size Time!!!
    else:
        _yellow_size = 0

    hashMap.put("vibrate", "")
    _cells = json.loads(hashMap.get("_cells"))
    _cellid = _cells.get(hashMap.get("current_object"))#enter error!!! Time!!!
    hashMap.put('_cellid', str(_cellid))  # ввод _cellid Time!!!
    hashMap.put("toast", str(hashMap.get("_cellid")) + ' line1280')  # Time!!!

    if not _cellid == None:

        # create connection with database
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH_debug)
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

        #found = []

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

        #hashMap.put("toast", hashMap.get('yellow_list')+' line1324')# before error Time!!!

        invdate = datetime.fromisoformat(str(hashMap.get("inv_date")))
        hashMap.put("inv", "Инвентаризация " + str(hashMap.get("inv_name")) + " от " + invdate.strftime(
            "%m.%d.%Y, %H:%M:%S") + "</n> Найдено: <big>" + str(_green_size) + "</big>" + " из " + "<big>" + str(
            _yellow_size) + "</big>")

        hashMap.put("NextStep", "Товары ячейки")

    hashMap.put('_green_size', str(_green_size))  # ввод _green_size Time!!!
    hashMap.put('_yellow_size', str(_yellow_size))  # ввод _yellow_size Time!!!

    return hashMap

def invcv_goods_on_new_object(hashMap, _files=None, _data=None):
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

        if hashMap.containsKey("stop_listener_list"):# есть ли stop_listener_list в hashMap
            stop_list = hashMap.get("stop_listener_list").split(";")
            stop_list.append(nom_barcode)# добавить nom_barcode в stop_listener_list
            hashMap.put("stop_listener_list", ";".join(stop_list))
        else:
            hashMap.put("stop_listener_list", nom_barcode)

        object_list = json.loads(hashMap.get("object_info_list"))

        try:#проходим по object_list пока не найдем объект с баркодом текущего объекта
            nom_record = next(item for item in object_list if str(item["object"]) == str(nom_barcode))

        except StopIteration:
            nom_record = None

        if not nom_record == None:
            hashMap.put("_nom_id", str(nom_record.get("_nom_id")))# Запись номера ID товара
            if hashMap.containsKey('write_id_list'):
                write_list = hashMap.get('write_id_list').split(';')
                write_list.append(str(nom_record.get('_nom_id')))
                hashMap.put('write_id_list', ';'.join(write_list))
            else:
                hashMap.put('write_id_list', str(nom_record.get('_nom_id')))
            # hashMap.put("toast","_nom_id="+str(hashMap.get("_nom_id"))+" inv_id="+str(hashMap.get("inv_id")))
            if nom_record['unique'] == 1:# это уникальный штрихкод???

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
                    #found.append(int(hashMap.get("_nom_id")))
                    inventory = ui_global.SW_Inventory[int(hashMap.get("inv_id"))]
                    r = ui_global.SW_Inventory_line(qty=1, sku=int(hashMap.get("_nom_id")),
                                        cell=int(hashMap.get("_cellid")), inventory=inventory) # прочитали _cellid Time!!!
                    commit()

                _green_size += 1
                invdate = datetime.fromisoformat(str(hashMap.get("inv_date")))
                hashMap.put("inv", "Инвентаризация " + str(hashMap.get("inv_name")) + " от " + invdate.strftime(
                    "%m.%d.%Y, %H:%M:%S") + "</n> Найдено: <big>" + str(_green_size) + "</big>" + " из " + "<big>" + str(
                    _yellow_size) + "</big>")
            else:  # неуникальный штрихкод - просим ввести кол-во
                hashMap.put("beep", "50")# начало
                if hashMap.containsKey('write_list'):  # есть ли write_list в hashMap
                    write_list = hashMap.get("write_list").split(";")
                    write_list.append(nom_barcode)  # добавить nom_barcode в write_list
                    hashMap.put("write_list", ";".join(write_list))
                else:
                    hashMap.put("write_list", nom_barcode)

                hashMap.put("nom", nom_record.get("info"))
                hashMap.put("nom_barcode", nom_barcode)
                hashMap.put("ShowDialogProcess", "Инвентаризация Active CV")
                hashMap.put("ShowDialog", "ДиалогВводКоличества")
                hashMap.put("ShowDialogStyle",
                            json.dumps({"title": "Введите количество факт", "yes": "Подтвердить", "no": "Отмена"}))

        hashMap.put('_green_size', str(_green_size))  # ввод _green_size Time!!!
        hashMap.put('_yellow_size', str(_yellow_size))  # ввод _yellow_size Time!!!


    return hashMap

def invcv_goods_action(hashMap, _files=None, _data=None):

    if hashMap.get("listener") == "onResultPositive":# в диалоге ввода количества - "Ок"

        hashMap.put("vibrate", "")

        if hashMap.containsKey('write_list'):  # есть ли write_list в hashMap
            write_list = hashMap.get("write_list").split(";")
            nom_barcode_write = str(write_list[-1])
            write_list.remove(nom_barcode_write)
            hashMap.put("write_list", ";".join(write_list))
            #hashMap.put("toast", "line 1478") after error!!!

        else:
            nom_barcode_write = str(hashMap.get("current_object"))
            hashMap.put("toast", "line 1482")
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

        #определяем ID
        if hashMap.containsKey('write_id_list'):  # есть ли write_id_list в hashMap
            write_id_list = hashMap.get("write_id_list").split(";")

            try:# есть ли _nom_id in write_id_list
                _nom_id = str(write_id_list[-1])
            except ValueError:
                hashMap.put("toast", "3 Error line 1515")
            else:
                _nom_id = str(write_id_list[-1])
                #hashMap.put("toast", "3 GOOD! line 1515") #after error!!!
            write_id_list.remove(_nom_id)
            hashMap.put("write_id_list", ";".join(write_id_list))

        else:
            try:# есть ли _nom_id in hashMap
                _nom_id = str(hashMap.get('_nom_id'))
            except ValueError:
                hashMap.put("toast", "4 Error line 1526")
            else:
                _nom_id = str(hashMap.get('_nom_id'))
                hashMap.put("toast", "4 GOOD! line 1526")

        #hashMap.put("toast", "line 1507")#after error!!!

            # добавляем в базу
        if getfloat_if_exist(hashMap, "qty") > 0:
            #hashMap.put("toast", str(type(getfloat_if_exist(hashMap, "qty"))) + " line 1511")# прочитали qty Time!!! после error!!!

            if not hashMap.get('_green_size') == None:
                # try:
                #     _green_size = int(hashMap.get('_green_size'))  # прочитали _green_size Time!!!
                # except ValueError:
                #     hashMap.put("toast", "1 Error line 1459")
                # else:
                _green_size = int(hashMap.get('_green_size'))
                hashMap.put("toast", hashMap.get('_green_size') + " GOOD 1! line 1459")
            else:
                _green_size = 0

            if not hashMap.get('_yellow_size') == None:
                try:
                    _yellow_size = int(hashMap.get('_yellow_size'))  # прочитали _yellow_size Time!!!
                except ValueError:
                    hashMap.put("toast", "2 Error line 1470")
                else:
                    _yellow_size = int(hashMap.get('_yellow_size'))
                    #hashMap.put("toast", "2 GOOD! line 1470")
            else:
                _yellow_size = 0

            try:# есть ли inv_id in hashMap
                inv_id1 = int(hashMap.get("inv_id"))
            except ValueError:
                hashMap.put("toast", "5 Error line 1539")
            #else:
                #hashMap.put("toast", "5 GOOD! line 1539")
            try:# есть ли _cellid in hashMap
                _cellid1 = int(hashMap.get("_cellid"))
            except ValueError:
                hashMap.put("toast", hashMap.get("_cellid") + " 6 Error line 1545")
            #else:
                #hashMap.put("toast", "6 GOOD! line 1545")
            _green_size += 1
            hashMap.put('_green_size', str(_green_size))  # ввод _green_size Time!!!
            hashMap.put("toast", hashMap.get('_green_size') + "  line 1555")
            hashMap.put('_yellow_size', str(_yellow_size))  # ввод _yellow_size Time!!!
            invdate = datetime.fromisoformat(str(hashMap.get("inv_date")))
            hashMap.put("inv", "Инвентаризация " + str(hashMap.get("inv_name")) + " от " + invdate.strftime(
                "%m.%d.%Y, %H:%M:%S") + "</n> Товаров в ячейке: <big>" + str(_yellow_size) + "</big>")

            with db_session:
                inventory = ui_global.SW_Inventory[int(hashMap.get("inv_id"))]
                r = ui_global.SW_Inventory_line(qty=getfloat_if_exist(hashMap, "qty"), sku=int(_nom_id),
                                                cell=int(hashMap.get("_cellid")), inventory=inventory)# прочитали qty Time!!!
                #found.append(int(_nom_id))
                commit()


    if hashMap.get("listener") == "К ЯЧЕЙКЕ":
        hashMap.put("NextStep", "Выбор ячейки")
        invdate = datetime.fromisoformat(str(hashMap.get("inv_date")))
        hashMap.put("inv",
                    "Инвентаризация " + str(hashMap.get("inv_name")) + " от " + invdate.strftime("%m.%d.%Y, %H:%M:%S"))



    return hashMap