def summ_list(l):
    res = 0
    for i in l:
        print(f'Cчетчик = {i}, ID элемента списка = {id(i)}')
        res += i
        print(f'Результат = {res}, ID результата = {id(res)}')
        print('--------------------')


summ_list([0, 1, 2, 3])